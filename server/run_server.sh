#!/bin/bash
cd /Users/fadil/repo/capstone/smart-caregiver/server
python3 -m uvicorn src.main:app --host 127.0.0.1 --port 8000