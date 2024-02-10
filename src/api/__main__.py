import os
import sys
from pathlib import Path

import uvicorn

# Change dir to project root (three levels up from this file)
os.chdir(Path(__file__).parents[2])
# Get arguments from command
args = sys.argv[1:]

uvicorn.main.main(
    [
        "src.api.app:app",
        "--use-colors",
        "--proxy-headers",
        "--forwarded-allow-ips=*",
        *args,
    ]
)
