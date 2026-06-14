"""
ml_pipeline.py
--------------
V4 — ML Pipeline Orchestrator
Coordinates: Train Models → Generate Predictions → Store Predictions

Called by run_pipeline.py as a single step.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from models.train_model import train_all_models
from models.predict import predict_all_coins, store_predictions


def run_ml_pipeline() -> dict:
    """
    Runs the full ML pipeline: train → predict → store.
    Returns a summary dict for logging.
    """
    print("\n  🤖 ML Pipeline started...")

    # Step 1: Train / retrain models on latest historical data
    print("  🏋️  Training Random Forest models...")
    train_results = train_all_models()

    trained  = [r for r in train_results if r["status"] == "trained"]
    skipped  = [r for r in train_results if r["status"] != "trained"]

    # Step 2: Generate predictions using freshly trained models
    print("  🔮 Generating predictions...")
    pred_df = predict_all_coins()

    # Step 3: Store predictions
    store_predictions(pred_df)

    summary = {
        "models_trained":  len(trained),
        "models_skipped":  len(skipped),
        "predictions_made": (pred_df["status"] == "predicted").sum() if not pred_df.empty else 0
    }

    if trained:
        avg_accuracy = sum(r["accuracy"] for r in trained) / len(trained)
        summary["avg_model_accuracy"] = round(avg_accuracy, 2)
        print(f"  📊 Avg model accuracy: {avg_accuracy:.1f}%")

    print(f"  ✅ ML pipeline complete — "
          f"{summary['models_trained']} models trained, "
          f"{summary['predictions_made']} predictions stored.")

    return summary


if __name__ == "__main__":
    summary = run_ml_pipeline()
    print(f"\nSummary: {summary}")
