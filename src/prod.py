#!/usr/bin/env python3.9

import uvicorn

if __name__ == "__main__":

    uvicorn.run("app.main:app", host="localhost", port=4000)
