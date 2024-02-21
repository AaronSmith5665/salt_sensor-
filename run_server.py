import subprocess
import time
import os
import signal

def run_server():
    """Start the server process"""
    return subprocess.Popen(["python3", "./sensor.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def git_pull():
    """Execute git pull and return its output"""
    result = subprocess.run(["git", "pull"], capture_output=True, text=True)
    return result.stdout

def server_needs_restart(git_output):
    """Check if the git pull output indicates that there are new changes"""
    return "Already up to date." not in git_output

def main():
    server_process = run_server()
    print("Server started...")

    try:
        while True:
            time.sleep(5)  # Wait for 30 seconds before checking for updates
            git_output = git_pull()
            print("Checking for updates...")
            if server_needs_restart(git_output):
                print("New version detected, restarting the server...")
                # Terminate the current server process
                server_process.terminate()
                try:
                    server_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print("Server shutdown timed out. Forcing termination...")
                    server_process.kill()
                # Restart the server
                server_process = run_server()
                print("Server restarted successfully.")
            else:
                print("No updates found.")

            # Check if server process has crashed
            if server_process.poll() is not None:
                print("Server crashed, restarting...")
                server_process = run_server()
                print("Server restarted successfully.")

    except KeyboardInterrupt:
        print("Shutting down...")
        server_process.terminate()
        try:
            server_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print("Server shutdown timed out. Forcing termination...")
            server_process.kill()

if __name__ == "__main__":
    main()
