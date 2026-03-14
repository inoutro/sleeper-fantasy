#!/usr/bin/env python3
import os
print("LEAGUE1_ID:", os.getenv("LEAGUE1_ID"))
print("LEAGUE2_ID:", os.getenv("LEAGUE2_ID"))

from src.monitor import run_once
run_once()
