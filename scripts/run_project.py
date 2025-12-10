#!/usr/bin/env python3
"""
run_project.py - Unified Project Execution Script

This script automates the entire project pipeline:
1. (Optional) Normalize raw Excel data to Parquet
2. Execute the training notebook (normalizacion_nb.ipynb)
3. Prepare dashboard data (dashboard_data.json)
4. Start local web server and open dashboard

Usage:
    python scripts/run_project.py           # Run full pipeline
    python scripts/run_project.py --no-train  # Skip training, just serve
"""

import subprocess
import os
import sys
import time
import webbrowser
import socket
import signal
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DASHBOARD_URL = "http://localhost:8000/notebooks/dashboard_enhanced.html"
PREDICTION_URL = "http://localhost:8000/notebooks/prediction_standalone.html"
SERVER_PORT = 8000

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def print_step(step_num, total, description):
    """Print a formatted step header."""
    print(f"\n{'='*60}")
    print(f"[{step_num}/{total}] {description}")
    print(f"{'='*60}")


def run_command(command, description, exit_on_fail=True):
    """Execute a shell command with error handling."""
    print(f"  → {description}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            cwd=str(PROJECT_ROOT),
            capture_output=False
        )
        print(f"  ✅ {description} completed.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error: {e}")
        if exit_on_fail:
            sys.exit(1)
        return False


def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def kill_process_on_port(port):
    """Kill any process using the specified port (macOS/Linux)."""
    try:
        result = subprocess.run(
            f"lsof -ti :{port} | xargs kill -9 2>/dev/null || true",
            shell=True,
            capture_output=True
        )
        time.sleep(0.5)  # Give time for port to be released
        return True
    except Exception:
        return False


def check_prerequisites():
    """Verify that required tools are available."""
    print("Checking prerequisites...")
    
    # Check .venv exists
    if not VENV_PYTHON.exists():
        print(f"  ❌ Virtual environment not found at {VENV_PYTHON}")
        print("     Run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt")
        sys.exit(1)
    print(f"  ✓ Virtual environment found: {VENV_PYTHON}")
    
    # Check nbconvert is installed
    result = subprocess.run(
        f"{VENV_PYTHON} -m jupyter nbconvert --version",
        shell=True,
        capture_output=True
    )
    if result.returncode != 0:
        print("  ⚠️  nbconvert not found. Installing...")
        subprocess.run(f"{VENV_PYTHON} -m pip install nbconvert", shell=True)
    else:
        print("  ✓ nbconvert available")
    
    # Check Java (required for PySpark)
    result = subprocess.run("java -version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("  ❌ Java not found. PySpark requires Java 11 or 17.")
        sys.exit(1)
    print("  ✓ Java available")
    
    print()


# ============================================================
# PIPELINE STEPS
# ============================================================

def step_normalize_data():
    """Step 0: Normalize Excel data to Parquet (if needed)."""
    parquet_file = DATA_PROCESSED / "siniestros_normalizado.parquet"
    
    if parquet_file.exists():
        print("  ℹ️  Normalized data already exists. Skipping.")
        return
    
    excel_file = PROJECT_ROOT / "data" / "raw" / "PERU. SINIESTROS DE TRANSITO POR AÑO 2008-2023.xlsx"
    if not excel_file.exists():
        print(f"  ⚠️  Excel file not found: {excel_file}")
        print("     Skipping normalization step.")
        return
    
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    
    cmd = (
        f'{VENV_PYTHON} -m tesis_prevencion_siniestros_transito.normalize '
        f'"{excel_file}" -o "{DATA_PROCESSED}/siniestros_normalizado.csv" '
        f'--parquet "{parquet_file}"'
    )
    run_command(cmd, "Normalizing Excel to Parquet", exit_on_fail=False)


def step_train_model():
    """Step 1: Execute the training notebook."""
    notebook = NOTEBOOKS_DIR / "normalizacion_nb.ipynb"
    
    if not notebook.exists():
        print(f"  ❌ Notebook not found: {notebook}")
        sys.exit(1)
    
    cmd = (
        f'{VENV_PYTHON} -m jupyter nbconvert '
        f'--to notebook --execute --inplace '
        f'--ExecutePreprocessor.kernel_name=tesis-venv '
        f'--ExecutePreprocessor.timeout=600 '
        f'"{notebook}"'
    )
    
    success = run_command(cmd, "Training Random Forest model (this may take 2-5 minutes)", exit_on_fail=False)
    
    if not success:
        print("\n  ⚠️  Notebook execution failed.")
        print("     The model may still work if previously trained.")
        print("     To debug, run the notebook manually in VS Code/Jupyter.")


def step_prepare_dashboard():
    """Step 2: Generate dashboard_data.json."""
    script = NOTEBOOKS_DIR / "prepare_dashboard_data.py"
    
    if not script.exists():
        print(f"  ❌ Script not found: {script}")
        sys.exit(1)
    
    cmd = f'{VENV_PYTHON} "{script}"'
    run_command(cmd, "Generating dashboard_data.json")


def step_start_server():
    """Step 3: Start local web server and open dashboard."""
    
    # Check if port is in use
    if is_port_in_use(SERVER_PORT):
        print(f"  ⚠️  Port {SERVER_PORT} is in use.")
        response = input("     Kill existing process and restart? [Y/n]: ").strip().lower()
        if response in ('', 'y', 'yes'):
            kill_process_on_port(SERVER_PORT)
            print(f"  → Port {SERVER_PORT} freed.")
        else:
            print(f"  → Using existing server. Opening dashboards (cache-busted)...")
            timestamp = int(time.time())
            webbrowser.open(f"{DASHBOARD_URL}?v={timestamp}")
            time.sleep(1)
            webbrowser.open(f"{PREDICTION_URL}?v={timestamp}")
            return
    
    # Open browsers after delay with cache-busting
    def open_browsers():
        time.sleep(2)
        timestamp = int(time.time())
        print(f"\n  🌐 Opening Dashboard (cache-busted): {DASHBOARD_URL}")
        webbrowser.open(f"{DASHBOARD_URL}?v={timestamp}")
        time.sleep(1)
        print(f"  🎯 Opening Predictor (cache-busted): {PREDICTION_URL}")
        webbrowser.open(f"{PREDICTION_URL}?v={timestamp}")
    
    import threading
    threading.Thread(target=open_browsers, daemon=True).start()
    
    print(f"  → Starting server on port {SERVER_PORT}...")
    print(f"  → Press Ctrl+C to stop.\n")
    
    try:
        subprocess.run(
            f'{VENV_PYTHON} -m http.server {SERVER_PORT}',
            shell=True,
            cwd=str(PROJECT_ROOT)
        )
    except KeyboardInterrupt:
        print("\n\n  🛑 Server stopped.")


# ============================================================
# MAIN
# ============================================================

def main():
    print("\n" + "="*60)
    print("🚀 TESIS - Pipeline de Ejecución Automatizado")
    print("="*60)
    
    # Parse arguments
    skip_train = "--no-train" in sys.argv
    
    check_prerequisites()
    
    total_steps = 3 if skip_train else 4
    step = 0
    
    if not skip_train:
        # Step 0: Normalize data (optional)
        step += 1
        print_step(step, total_steps, "Verificar/Normalizar Datos")
        step_normalize_data()
        
        # Step 1: Train model
        step += 1
        print_step(step, total_steps, "Entrenar Modelo (Random Forest)")
        step_train_model()
    
    # Step 2: Prepare dashboard
    step += 1
    print_step(step, total_steps, "Preparar Datos del Dashboard")
    step_prepare_dashboard()
    
    # Step 3: Start server
    step += 1
    print_step(step, total_steps, "Iniciar Servidor Web")
    step_start_server()


if __name__ == "__main__":
    main()
