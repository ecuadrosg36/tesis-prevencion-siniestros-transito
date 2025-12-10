import json
import sys

nb_path = "notebooks/normalizacion_nb.ipynb"

new_code = [
    "from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder\n",
    "from pyspark.ml.regression import RandomForestRegressor\n",
    "from pyspark.ml.evaluation import RegressionEvaluator\n",
    "from pyspark.ml import Pipeline\n",
    "\n",
    "# 1. Indexar y codificar la región\n",
    "indexer = StringIndexer(inputCol=\"region\", outputCol=\"region_idx\", handleInvalid=\"keep\")\n",
    "encoder = OneHotEncoder(inputCols=[\"region_idx\"], outputCols=[\"region_vec\"])\n",
    "\n",
    "# 2. Ensamblar features (incluyendo la región codificada)\n",
    "# Asegúrate de que 'feature_cols' NO incluya 'region' (ya lo excluimos antes)\n",
    "assembler = VectorAssembler(inputCols=[\"region_vec\"] + feature_cols, outputCol=\"features\", handleInvalid=\"keep\")\n",
    "\n",
    "# 3. Definir el modelo Random Forest\n",
    "rf = RandomForestRegressor(featuresCol=\"features\", labelCol=\"label\", \n",
    "                           numTrees=100, maxDepth=10, seed=42)\n",
    "\n",
    "# 4. Crear Pipeline\n",
    "pipeline = Pipeline(stages=[indexer, encoder, assembler, rf])\n",
    "\n",
    "# Split temporal\n",
    "train = df.filter(\"year <= 2021\").withColumn(\"label\", F.col(TOTAL_COL))\n",
    "test  = df.filter(\"year >= 2022\").withColumn(\"label\", F.col(TOTAL_COL))\n",
    "\n",
    "print(f\"[INFO] train={train.count()}, test={test.count()}, feats={len(feature_cols)} + region_vec\")\n",
    "\n",
    "# Entrenar\n",
    "model = pipeline.fit(train)\n",
    "\n",
    "# Predecir\n",
    "pred = model.transform(test)\n",
    "\n",
    "# Evaluar\n",
    "rmse = RegressionEvaluator(labelCol=\"label\", predictionCol=\"prediction\", metricName=\"rmse\").evaluate(pred)\n",
    "mae  = RegressionEvaluator(labelCol=\"label\", predictionCol=\"prediction\", metricName=\"mae\").evaluate(pred)\n",
    "r2   = RegressionEvaluator(labelCol=\"label\", predictionCol=\"prediction\", metricName=\"r2\").evaluate(pred)\n",
    "\n",
    "print(f\"[RANDOM FOREST] RMSE={rmse:.2f} | MAE={mae:.2f} | R2={r2:.2f}\")\n",
    "\n",
    "# Feature Importance (un poco más complejo de extraer con Pipeline, pero posible)\n",
    "print(f\"[INFO] Feature Importances available via model.stages[-1].featureImportances\")\n",
    "\n",
    "# Vista de predicción\n",
    "pred.select(\"year\",\"region\",\"label\",\"prediction\")\\\n",
    "    .orderBy(\"year\",\"region\").show(30, truncate=False)\n"
]

try:
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    found = False
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            if "GeneralizedLinearRegression" in source and "family=\"poisson\"" in source:
                print("Found target cell. Replacing code...")
                cell['source'] = new_code
                found = True
                break
    
    if found:
        with open(nb_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        print("Notebook patched successfully.")
    else:
        print("Target cell not found.")

except Exception as e:
    print(f"Error patching notebook: {e}")
