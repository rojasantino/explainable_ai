"""
MASTER PIPELINE SCRIPT
========================
Run this ONE script to execute all phases in order:
  Phase 00 → Generate synthetic dataset
  Phase 02 → Clean data
  Phase 03 → Feature engineering
  Phase 04 → Customer segmentation
  Phase 05 → Purchase prediction model
  Phase 06 → Recommendation system
  Phase 07 → SHAP explainable AI

After this completes, run the Flask API:
  python api/app.py
"""

import subprocess, sys, time, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

steps = [
    ("Phase 00 — Generate Dataset",      "python data/generate_data.py"),
    ("Phase 02 — Data Cleaning",         "python ml/phase02_data_cleaning.py"),
    ("Phase 03 — Feature Engineering",   "python ml/phase03_feature_engineering.py"),
    ("Phase 04 — Customer Segmentation", "python ml/phase04_segmentation.py"),
    ("Phase 05 — Purchase Prediction",   "python ml/phase05_prediction.py"),
    ("Phase 06 — Recommendation System", "python ml/phase06_recommendation.py"),
    ("Phase 07 — SHAP Explainable AI",   "python explain/phase07_shap_explain.py"),
]

print("=" * 55)
print(" EXPLAINABLE AI PERSONALIZATION SYSTEM — PIPELINE")
print("=" * 55)

start_total = time.time()
for i, (name, cmd) in enumerate(steps, 1):
    print(f"\n[{i}/{len(steps)}] {name}")
    print("-" * 45)
    t0  = time.time()
    ret = subprocess.run(cmd.split(), capture_output=False)
    elapsed = time.time() - t0
    if ret.returncode != 0:
        print(f"\nERROR in step {i}. Stopping pipeline.")
        sys.exit(1)
    print(f"  Completed in {elapsed:.1f}s")

total = time.time() - start_total
print("\n" + "=" * 55)
print(f"PIPELINE COMPLETE  ({total:.0f}s total)")
print("=" * 55)
print("\nNext step — start the Flask API:")
print("  python api/app.py")
print("\nThen open Angular frontend:")
print("  cd frontend && ng serve")
print("\nTest API endpoints:")
print("  http://localhost:5000/api/health")
print("  http://localhost:5000/api/customer/101")
print("  http://localhost:5000/api/predict/101")
print("  http://localhost:5000/api/recommend/101")
print("  http://localhost:5000/api/explain/101")
print("  http://localhost:5000/api/dashboard/stats")
