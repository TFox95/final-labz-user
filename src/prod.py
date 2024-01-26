import os
import subprocess

if __name__ == "__main__":

    app_file = os.getenv("FASTAPI_APP", "app.main")
    subprocess.call(["uvicorn", f"{app_file}:app"])
