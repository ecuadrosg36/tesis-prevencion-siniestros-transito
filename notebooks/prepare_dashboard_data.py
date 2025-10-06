
#!/usr/bin/env python3
"""
Prepare data from model outputs for dashboard visualization
"""

import pandas as pd
import json
from pathlib import Path

def prepare_dashboard_data():
    """Load and prepare data from model outputs"""

    DIR_MODELS = Path("models")
    output_data = {
        "predictions": [],
        "future": [],
        "metrics": {},
        "regions": []
    }

    # Load prediction data
    pred_path = DIR_MODELS / "predictions_best_model"
    if pred_path.exists():
        csv_files = list(pred_path.glob("*.csv"))
        if csv_files:
            df = pd.read_csv(csv_files[0])

            # Rename columns for consistency
            column_mapping = {
                'siniestros_total__total': 'actual',
                'prediction': 'predicted',
                'absolute_error': 'abs_error',
                'relative_error': 'rel_error'
            }
            df = df.rename(columns=column_mapping)

            # Calculate error percentage if not present
            if 'rel_error' not in df.columns and 'actual' in df.columns and 'predicted' in df.columns:
                df['error_pct'] = abs(df['predicted'] - df['actual']) / df['actual'] * 100
            else:
                df['error_pct'] = df['rel_error'] * 100 if 'rel_error' in df.columns else 0

            # Convert to records
            output_data["predictions"] = df.to_dict('records')
            output_data["regions"] = df['region'].unique().tolist()

    # Load future predictions
    future_path = DIR_MODELS / "future_predictions_2024_2025"
    if future_path.exists():
        csv_files = list(future_path.glob("*.csv"))
        if csv_files:
            df_future = pd.read_csv(csv_files[0])
            output_data["future"] = df_future.to_dict('records')

    # Calculate metrics
    if output_data["predictions"]:
        df_pred = pd.DataFrame(output_data["predictions"])
        output_data["metrics"] = {
            "total_regions": len(output_data["regions"]),
            "mean_error": df_pred['error_pct'].mean(),
            "median_error": df_pred['error_pct'].median(),
            "accuracy": 100 - df_pred['error_pct'].mean(),
            "within_20pct": (df_pred['error_pct'] <= 20).mean() * 100,
            "within_50pct": (df_pred['error_pct'] <= 50).mean() * 100
        }

    # Save to JSON
    with open("dashboard_data.json", 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Dashboard data prepared: {len(output_data['predictions'])} predictions")
    print(f"Regions: {len(output_data['regions'])}")
    print(f"Mean accuracy: {output_data['metrics'].get('accuracy', 0):.1f}%")

    return output_data

if __name__ == "__main__":
    prepare_dashboard_data()
