# core/quality_checks.py
import pandas as pd
import numpy as np
from datetime import datetime

class DataQualityChecker:

    def __init__(self, df: pd.DataFrame,
                 dataset_name: str = "Dataset"):
        self.df = df
        self.dataset_name = dataset_name
        self.run_timestamp = datetime.now().isoformat()

    # ── DIMENSION 1: COMPLETENESS ─────────────────────
    def check_completeness(self) -> dict:
        """Check for missing values across all columns"""
        total = len(self.df)
        missing_counts = self.df.isnull().sum()
        missing_pct = (
            missing_counts / total * 100
        ).round(2)

        score = round(100 - missing_pct.mean(), 2)

        return {
            "missing_counts": missing_counts.to_dict(),
            "missing_pct": missing_pct.to_dict(),
            "completeness_score": max(score, 0),
            "columns_with_missing": int(
                (missing_counts > 0).sum()
            ),
            "total_missing_cells": int(
                missing_counts.sum()
            )
        }

    # ── DIMENSION 2: UNIQUENESS ───────────────────────
    def check_duplicates(self) -> dict:
        """Detect duplicate rows"""
        total = len(self.df)
        dupe_count = int(self.df.duplicated().sum())
        dupe_pct = round(dupe_count / total * 100, 2)

        return {
            "duplicate_rows": dupe_count,
            "duplicate_pct": dupe_pct,
            "uniqueness_score": round(
                100 - dupe_pct, 2
            ),
            "unique_rows": total - dupe_count
        }

    # ── DIMENSION 3: OUTLIERS ─────────────────────────
    def check_outliers(self) -> dict:
        """Detect outliers using IQR method"""
        numeric_cols = self.df.select_dtypes(
            include=[np.number]
        ).columns
        report = {}

        for col in numeric_cols:
            col_data = self.df[col].dropna()
            if len(col_data) == 0:
                continue
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outliers = self.df[
                (self.df[col] < lower) |
                (self.df[col] > upper)
            ]
            report[col] = {
                "count": len(outliers),
                "pct": round(
                    len(outliers) / len(self.df) * 100,
                    2
                ),
                "lower_bound": round(float(lower), 4),
                "upper_bound": round(float(upper), 4),
                "min_value": round(
                    float(col_data.min()), 4
                ),
                "max_value": round(
                    float(col_data.max()), 4
                )
            }
        return report

    # ── DIMENSION 4: CONSISTENCY ──────────────────────
    def check_consistency(
        self, rules: dict = None
    ) -> dict:
        """
        Check values against defined rules.
        Example rules:
        {
          "age":   {"min": 0, "max": 120},
          "score": {"min": 0, "max": 100}
        }
        """
        if not rules:
            return {
                "message": "No rules provided",
                "consistency_score": 100
            }
        violations = {}
        total_violations = 0

        for col, rule in rules.items():
            if col not in self.df.columns:
                continue
            bad = self.df[
                (self.df[col] < rule.get(
                    "min", -np.inf)
                ) |
                (self.df[col] > rule.get(
                    "max", np.inf)
                )
            ]
            count = len(bad)
            total_violations += count
            violations[col] = {
                "violation_count": count,
                "violation_pct": round(
                    count / len(self.df) * 100, 2
                ),
                "rule": rule
            }

        score = round(
            100 - (
                total_violations / len(self.df) * 100
            ),
            2
        )
        return {
            "violations": violations,
            "total_violations": total_violations,
            "consistency_score": max(score, 0)
        }

    # ── DIMENSION 5: DATA TYPES ───────────────────────
    def check_dtypes(self) -> dict:
        """Summarise column data types"""
        return {
            "dtypes": {
                col: str(dtype)
                for col, dtype
                in self.df.dtypes.items()
            },
            "numeric_columns": list(
                self.df.select_dtypes(
                    include=[np.number]
                ).columns
            ),
            "text_columns": list(
                self.df.select_dtypes(
                    include=["object"]
                ).columns
            ),
            "datetime_columns": list(
                self.df.select_dtypes(
                    include=["datetime"]
                ).columns
            )
        }

    # ── OVERALL QUALITY SCORE ─────────────────────────
    def calculate_score(
        self, consistency_rules: dict = None
    ) -> dict:
        """Calculate weighted overall quality score"""
        completeness = self.check_completeness()
        duplicates = self.check_duplicates()
        consistency = self.check_consistency(
            consistency_rules
        )

        c_score = completeness["completeness_score"]
        u_score = duplicates["uniqueness_score"]
        con_score = consistency.get(
            "consistency_score", 100
        )

        # Weighted: Completeness 40%,
        # Uniqueness 30%, Consistency 30%
        overall = round(
            c_score * 0.40 +
            u_score * 0.30 +
            con_score * 0.30,
            1
        )

        grade = (
            "A" if overall >= 90 else
            "B" if overall >= 75 else
            "C" if overall >= 60 else
            "D" if overall >= 45 else "F"
        )
        status = (
            "Excellent" if overall >= 90 else
            "Good" if overall >= 75 else
            "Needs Attention" if overall >= 60 else
            "Poor" if overall >= 45 else "Critical"
        )

        return {
            "dataset_name": self.dataset_name,
            "run_timestamp": self.run_timestamp,
            "total_rows": len(self.df),
            "total_columns": len(self.df.columns),
            "overall_score": overall,
            "grade": grade,
            "status": status,
            "completeness_score": c_score,
            "uniqueness_score": u_score,
            "consistency_score": con_score,
            "recommendation": self._get_recommendation(
                overall, c_score, u_score
            )
        }

    def _get_recommendation(
        self, score, completeness, uniqueness
    ) -> str:
        """Generate plain-English recommendation"""
        issues = []
        if completeness < 80:
            issues.append(
                f"address missing values — "
                f"{round(100 - completeness, 1)}% "
                f"of data is incomplete"
            )
        if uniqueness < 95:
            issues.append(
                f"remove duplicate rows — "
                f"{round(100 - uniqueness, 1)}% "
                f"duplicates found"
            )
        if not issues:
            return (
                "Data quality is acceptable. "
                "Continue monitoring regularly."
            )
        return (
            "Priority actions: " +
            "; ".join(issues) + "."
        )