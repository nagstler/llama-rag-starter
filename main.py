#!/usr/bin/env python3
# main.py - Main entry point for the RAG application

import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.api.app import run_server

if __name__ == "__main__":
    run_server()