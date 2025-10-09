from ml.disproportionality_analysis import AlertAggregator
from ml.report_severity_model import AICaseSeverityClassifier

sample_reports = [
    {"SEX": "M", "age": 45, "drugname": "DUTASTERIDE", "indi_pt": "Prostate", "pt": "Anaphylactic reaction"},
    {"SEX": "F", "age": 62, "drugname": "METHOTREXATE SODIUM", "indi_pt": "Rheumatoid arthritis", "pt": "Seizure"},
    {"SEX": "M", "age": 33, "drugname": "HYDROMORPHONE", "indi_pt": "Pain", "pt": "Injury"},
    {"SEX": "F", "age": 70, "drugname": "COSENTYX", "indi_pt": "Psoriasis", "pt": "Dizziness"},
]

detector = AICaseSeverityClassifier()
if not detector.model_path.exists():
    detector.train_model()
else:
    detector.load_model()


aggregator = AlertAggregator()

for report in sample_reports:
    prediction = detector.predict(report)
    print(f"Report: {report}")
    print(f"Prediction: {prediction}")
    aggregator.add_report(report, prediction)

agg_df = aggregator.aggregate_signals()
print("Aggregated signals:")
print(agg_df)

if not agg_df.empty:
    prr = aggregator.compute_prr(agg_df, drugname="DUTASTERIDE", pt="Hypoaesthesia")
    print(f"PRR for DUTASTERIDE - Overdose: {prr:.2f}" if prr else "PRR not computable")
else:
    print("No alerts detected, skipping PRR calculation")
