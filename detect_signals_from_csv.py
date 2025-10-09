import pandas as pd
from ml.disproportionality_analysis import AlertAggregator
from ml.report_severity_model import AICaseSeverityClassifier

# Load dataset
df = pd.read_csv('data/synthetic_reports.csv')

# Map columns to match model input
df.rename(columns={'sex': 'SEX', 'drug_name': 'drugname', 'indication': 'indi_pt', 'adverse_event': 'pt'}, inplace=True)

# Initialize detector
detector = AICaseSeverityClassifier()
if not detector.model_path.exists():
    detector.train_model()
else:
    detector.load_model()

aggregator = AlertAggregator()

# Process each report
for _, row in df.iterrows():
    report = row.to_dict()
    prediction = detector.predict(report)
    aggregator.add_report(report, prediction)

# Aggregate signals
agg_df = aggregator.aggregate_signals()
print("Aggregated signals:")
print(agg_df)

# Get top risk drugs
if not agg_df.empty:
    top_risk = aggregator.get_top_risk_drugs(top_n=5)
    print("\nTop risk drugs:")
    print(top_risk)
else:
    print("No alerts detected.")
