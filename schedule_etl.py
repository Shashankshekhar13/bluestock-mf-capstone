import os
import sys
import platform
import subprocess
import argparse

TASK_NAME = "Bluestock_MF_ETL"

def setup_windows_schedule(script_path):
    print("Detected OS: Windows. Using Windows Task Scheduler...")
    python_exe = sys.executable
    
    # Format the command to execute
    # Escape quotes inside the /tr command string
    cmd_to_run = f'"{python_exe}" "{script_path}"'
    
    # schtasks command to run weekly on Mon, Tue, Wed, Thu, Fri at 8:00 PM (20:00)
    schtasks_cmd = [
        "schtasks", "/create", 
        "/tn", TASK_NAME, 
        "/tr", cmd_to_run, 
        "/sc", "weekly", 
        "/d", "MON,TUE,WED,THU,FRI", 
        "/st", "20:00", 
        "/f"
    ]
    
    try:
        print(f"Running command: {' '.join(schtasks_cmd)}")
        result = subprocess.run(schtasks_cmd, capture_output=True, text=True, check=True)
        print("Success!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating scheduled task: {e}")
        print(f"Command stderr: {e.stderr}")
        print("Tip: If it failed due to permissions, try running this script from an Administrator terminal.")
        return False

def remove_windows_schedule():
    print("Detected OS: Windows. Removing Windows scheduled task...")
    schtasks_cmd = ["schtasks", "/delete", "/tn", TASK_NAME, "/f"]
    try:
        result = subprocess.run(schtasks_cmd, capture_output=True, text=True, check=True)
        print("Success!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        # If task does not exist, that's fine
        if "ERROR: The system cannot find the file specified" in e.stderr or "not found" in e.stderr.lower():
            print(f"Task '{TASK_NAME}' was not found (nothing to remove).")
            return True
        print(f"Error deleting scheduled task: {e}")
        print(f"Command stderr: {e.stderr}")
        return False

def setup_unix_schedule(script_path):
    print("Detected OS: Unix-like. Using crontab...")
    python_exe = sys.executable
    cron_comment = f"# {TASK_NAME}"
    cron_line = f'0 20 * * 1-5 "{python_exe}" "{script_path}" {cron_comment}'
    
    try:
        # Get existing crontab
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        existing_cron = result.stdout if result.returncode == 0 else ""
        
        # Filter out any existing line with our task name
        lines = [line for line in existing_cron.splitlines() if cron_comment not in line]
        
        # Add the new line
        lines.append(cron_line)
        new_cron = "\n".join(lines) + "\n"
        
        # Write to temporary file and load into crontab
        temp_file = "temp_cron_setup.txt"
        with open(temp_file, "w") as f:
            f.write(new_cron)
            
        subprocess.run(["crontab", temp_file], check=True)
        os.remove(temp_file)
        
        print("Success! Weekday 8:00 PM cron job scheduled.")
        print(f"Added line to crontab: {cron_line}")
        return True
    except Exception as e:
        print(f"Failed to automatically update crontab: {e}")
        print("\nPlease manually add the following line to your crontab (run `crontab -e`):")
        print(cron_line)
        return False

def remove_unix_schedule():
    print("Detected OS: Unix-like. Removing crontab entry...")
    cron_comment = f"# {TASK_NAME}"
    
    try:
        # Get existing crontab
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if result.returncode != 0:
            print("No crontab found (nothing to remove).")
            return True
            
        existing_cron = result.stdout
        
        # Filter out our line
        lines = [line for line in existing_cron.splitlines() if cron_comment not in line]
        new_cron = "\n".join(lines) + "\n"
        
        if not new_cron.strip():
            # If crontab is now empty, remove it completely
            subprocess.run(["crontab", "-r"], check=True)
            print("Crontab was emptied and removed.")
        else:
            temp_file = "temp_cron_setup.txt"
            with open(temp_file, "w") as f:
                f.write(new_cron)
            subprocess.run(["crontab", temp_file], check=True)
            os.remove(temp_file)
            print("Successfully removed the cron job entry.")
        return True
    except Exception as e:
        print(f"Failed to remove crontab entry: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Schedule the live NAV fetch script to run on weekdays at 8:00 PM.")
    parser.add_argument("--remove", action="store_true", help="Remove the scheduled task.")
    args = parser.parse_args()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_script = os.path.join(script_dir, "live_nav_fetch.py")
    
    if not os.path.exists(target_script):
        print(f"Error: Target script not found at {target_script}")
        sys.exit(1)
        
    is_windows = platform.system() == "Windows"
    
    if args.remove:
        success = remove_windows_schedule() if is_windows else remove_unix_schedule()
    else:
        success = setup_windows_schedule(target_script) if is_windows else setup_unix_schedule(target_script)
        
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
