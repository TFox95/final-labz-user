#!/usr/bin/env python3.9

import os
import subprocess

if __name__ == "__main__":

    args = ["--reload"]
    app_file = os.getenv("FASTAPI_APP", "app.main")
    print(app_file)
    print(args)
    subprocess.call(["uvicorn", f"{app_file}:app", *args])
