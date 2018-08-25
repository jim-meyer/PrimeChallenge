#!/bin/bash
set -euxo pipefail

if [[ $# -lt 1 ]]; then
   echo "Usage: ${0} <IP address of redis server>"
   exit 1
fi

export REDIS_SERVER_IP="${1}"
python -m unittest discover -p "*Test.py"

