import subprocess
import sys
import time
import os

PROJECT = os.path.dirname(os.path.abspath(__file__))
PYTHON = os.path.join(PROJECT, ".venv", "Scripts", "python.exe")


def main():
    # Fix encoding for Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    print("=" * 50)
    print("  ASTRA Desktop Launcher v4.0")
    print("=" * 50)

    # 1. Stop old Python processes
    print("\n[1/4] Stopping old processes...")
    subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], capture_output=True)
    subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe", "/T"], capture_output=True)
    time.sleep(2)

    # 2. Start API server
    print("[2/4] Starting API server...")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    api = subprocess.Popen(
        [PYTHON, "astra_api.py"],
        cwd=PROJECT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    print("[ASTRA] Waiting 8 seconds for API to start...")
    time.sleep(8)

    # 3. Check API
    print("[3/4] Checking API...")
    try:
        import requests
        r = requests.get("http://localhost:8764/api/status", timeout=5)
        if r.status_code == 200:
            print("[ASTRA] API is ONLINE!")
        else:
            print(f"[ASTRA] API warning: status {r.status_code}")
    except Exception as e:
        print(f"[ASTRA] API check: {e}")
        print("[ASTRA] Continuing anyway...")

    # 4. Start Desktop
    print("[4/4] Starting ASTRA Desktop...")
    print("=" * 50)
    desktop = subprocess.Popen(
        [PYTHON, "-m", "astra_desktop.app"],
        cwd=PROJECT,
        env=env,
    )

    # Wait for Desktop to close
    desktop.wait()

    # Cleanup
    print("\n[ASTRA] Desktop closed. Stopping API...")
    api.terminate()
    try:
        api.wait(timeout=5)
    except:
        api.kill()
    print("[ASTRA] Goodbye!")
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
