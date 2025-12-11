# not needed any more as per recent changes
import subprocess

scripts = [
    "main\\nse_lib_bhav.py",
    "main\\swing_screener.py",
    "main\\additions.py",
    "main\\addition_del_spike.py"
]

for script in scripts:
    print(f"\nRunning {script} ...")
    result = subprocess.run(["python", script])
    if result.returncode != 0:
        print(f"{script} failed with exit code {result.returncode}. Stopping execution.")
        break
    else:
        print(f"{script} completed successfully.\n")

print("All scripts executed sequentially.")
