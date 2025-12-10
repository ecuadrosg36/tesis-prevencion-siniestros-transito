import json
import sys

nb_path = "notebooks/normalizacion_nb.ipynb"

try:
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    found = False
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            if "OUTPUT_PATH = \"dbfs:/" in source:
                print("Found target cell with DBFS path. Replacing...")
                # Replace the DBFS path with a local path
                new_source = []
                for line in cell['source']:
                    if "OUTPUT_PATH = \"dbfs:/" in line:
                        new_source.append("OUTPUT_PATH = \"gold_local/feat_model_clean_v2\"  # Fixed for local execution\n")
                    else:
                        new_source.append(line)
                cell['source'] = new_source
                found = True
                break
    
    if found:
        with open(nb_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        print("Notebook patched successfully: DBFS path replaced with local path.")
    else:
        print("Target cell with DBFS path not found.")

except Exception as e:
    print(f"Error patching notebook: {e}")
