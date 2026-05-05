# test_run.py
import pandas as pd
from core.quality_checks import DataQualityChecker
from core.reporter import QualityReporter

# ── LOAD SAMPLE DATA ──────────────────────────────────
print("Loading data...")
df = pd.read_csv("sample_data/titanic.csv")
print(f"✅ Loaded {len(df):,} rows, "
      f"{len(df.columns)} columns")

# ── RUN QUALITY CHECKS ────────────────────────────────
print("\nRunning quality checks...")
checker = DataQualityChecker(df, "Titanic Dataset")
score = checker.calculate_score()

# ── PRINT RESULTS ─────────────────────────────────────
print("\n" + "="*50)
print("   DATAQUALITY PRO — AUDIT REPORT")
print("="*50)
print(f"  Dataset   : {score['dataset_name']}")
print(f"  Rows      : {score['total_rows']:,}")
print(f"  Columns   : {score['total_columns']}")
print(f"  Score     : {score['overall_score']}/100")
print(f"  Grade     : {score['grade']}")
print(f"  Status    : {score['status']}")
print("="*50)
print(f"\n  Completeness : "
      f"{score['completeness_score']}/100")
print(f"  Uniqueness   : "
      f"{score['uniqueness_score']}/100")
print(f"  Consistency  : "
      f"{score['consistency_score']}/100")
print("\n  RECOMMENDATION:")
print(f"  {score['recommendation']}")
print("="*50)

# ── DETAILED CHECKS ───────────────────────────────────
print("\nMISSING VALUES:")
completeness = checker.check_completeness()
for col, pct in completeness[
    "missing_pct"
].items():
    if pct > 0:
        print(f"  {col}: {pct}% missing")

print("\nDUPLICATES:")
dupes = checker.check_duplicates()
print(f"  {dupes['duplicate_rows']} duplicate rows "
      f"({dupes['duplicate_pct']}%)")

print("\nOUTLIERS:")
outliers = checker.check_outliers()
for col, info in outliers.items():
    if info['count'] > 0:
        print(f"  {col}: {info['count']} outliers "
              f"({info['pct']}%)")

# ── EXPORT REPORTS ────────────────────────────────────
print("\nExporting reports...")
reporter = QualityReporter(checker)
reporter.export_json("outputs/report.json")
reporter.export_csv_for_powerbi(
    "outputs/powerbi_data.csv"
)

print("\n✅ All done! Check your outputs/ folder.")