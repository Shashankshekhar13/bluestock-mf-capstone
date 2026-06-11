import subprocess
import sys
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    etl_script = os.path.join(script_dir, "scripts", "etl_pipeline.py")
    
    print(f"Launching Bluestock MF ETL Pipeline from root entrypoint...")
    print(f"Script path: {etl_script}")
    print(f"Python interpreter: {sys.executable}")
    print("-" * 80)
    
    # Run using the same python interpreter to preserve dependencies
    result = subprocess.run([sys.executable, etl_script], check=False)
    
    print("-" * 80)
    if result.returncode == 0:
        print("[SUCCESS] Pipeline completed successfully!")
        sys.exit(0)
    else:
        print(f"[ERROR] Pipeline failed with return code {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
