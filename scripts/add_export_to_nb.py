import json
import os

nb_path = "notebooks/normalizacion_nb.ipynb"

export_code = [
    "# ============================================\n",
    "# EXPORT FOR DASHBOARD\n",
    "# ============================================\n",
    "import os\n",
    "from pathlib import Path\n",
    "\n",
    "DIR_MODELS = Path(\"models\")\n",
    "DIR_MODELS.mkdir(exist_ok=True)\n",
    "\n",
    "# Prepare predictions for export\n",
    "export_df = pred.withColumn(\"siniestros_total__total\", F.col(\"label\")) \\\n",
    "    .withColumn(\"absolute_error\", F.abs(F.col(\"prediction\") - F.col(\"label\"))) \\\n",
    "    .withColumn(\"relative_error\", F.col(\"absolute_error\") / F.col(\"label\"))\n",
    "\n",
    "# Save to models/predictions_best_model\n",
    "out_path = DIR_MODELS / \"predictions_best_model\"\n",
    "print(f\"Exporting predictions to {out_path}...\")\n",
    "\n",
    "export_df.select(\"year\", \"region\", \"siniestros_total__total\", \"prediction\", \"absolute_error\", \"relative_error\") \\\n",
    "    .coalesce(1) \\\n",
    "    .write.mode(\"overwrite\") \\\n",
    "    .option(\"header\", True) \\\n",
    "    .csv(str(out_path))\n",
    "\n",
    "print(\"Export complete!\")\n"
]

try:
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # Create a new code cell
    new_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": export_code
    }

    # Append to the end of the notebook
    nb['cells'].append(new_cell)
    
    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print("Notebook updated with export logic.")

except Exception as e:
    print(f"Error updating notebook: {e}")
