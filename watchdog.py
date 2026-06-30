import subprocess
import time
import os
import signal
import sys


FLAG = "restart.flag"
SERVER = "run_multipleTags.py"
process = None


def start_server():
    return subprocess.Popen(
        ["venv\\Scripts\\python.exe", SERVER],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )


def shutdown(sig, frame):
    print("Watchdog shutting down...")
    if process:
        process.terminate()
        process.wait()
    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)


print("Watchdog started. Launching server...")
process = start_server()


while True:
    time.sleep(1)


    # only restart when Flask writes the flag
    if os.path.exists(FLAG):
        print("Restart flag detected. Restarting server...")
        os.remove(FLAG)
        process.terminate()
        process.wait()
        time.sleep(1)
        process = start_server()
        print("Server relaunched.")


