# core/reporter.py
import pandas as pd
import json
from datetime import datetime
from .quality_checks import DataQualityChecker


class QualityReporter:

    def __init__(self, checker: DataQualityChecker):
        self.checker = checker

    def export_json(
        self,
        output_path: str,
        consistency_rules: dict = None
    ):
        """Export full report as JSON"""
        report = {
            "score": self.checker.calculate_score(
                consistency_rules
            ),
            "completeness": (
                self.checker.check_completeness()
            ),
            "duplicates": (
                self.checker.check_duplicates()
            ),
            "outliers": (
                self.checker.check_outliers()
            ),
            "dtypes": (
                self.checker.check_dtypes()
            )
        }
        with open(output_path, "w") as f:
            json.dump(
                report, f, indent=2, default=str
            )
        print(f"✅ JSON report saved: {output_path}")
        return report

    def export_csv_for_powerbi(
        self, output_path: str
    ):
        """Export flat CSV optimised for Power BI"""
        completeness = (
            self.checker.check_completeness()
        )
        outliers = self.checker.check_outliers()
        score = self.checker.calculate_score()
        timestamp = datetime.now().isoformat()

        rows = []
        for col in self.checker.df.columns:
            rows.append({
                "run_timestamp": timestamp,
                "dataset_name": (
                    self.checker.dataset_name
                ),
                "column_name": col,
                "missing_count": completeness[
                    "missing_counts"
                ].get(col, 0),
                "missing_pct": completeness[
                    "missing_pct"
                ].get(col, 0),
                "outlier_count": outliers.get(
                    col, {}
                ).get("count", 0),
                "outlier_pct": outliers.get(
                    col, {}
                ).get("pct", 0),
                "overall_score": (
                    score["overall_score"]
                ),
                "grade": score["grade"],
                "status": score["status"],
                "duplicate_rows": score.get(
                    "duplicate_rows", 0
                ),
                "total_rows": score["total_rows"],
                "total_columns": (
                    score["total_columns"]
                ),
                "completeness_score": (
                    score["completeness_score"]
                ),
                "uniqueness_score": (
                    score["uniqueness_score"]
                ),
                "recommendation": (
                    score["recommendation"]
                )
            })

        df_out = pd.DataFrame(rows)
        df_out.to_csv(output_path, index=False)
        print(
            f"✅ Power BI CSV saved: {output_path}"
        )
        return df_out