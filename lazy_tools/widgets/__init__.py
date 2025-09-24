"""
Configuration and utilities for Krita Lazy Tools widgets.

This module contains shared configuration variables and utilities used across
the widget modules.
"""

import os
import tempfile


# Project paths configuration
PROJECT_DIR = r"C:\Users\udtre\Projects\krita-plugin\krita-lazy-tools"
VENV_PYTHON_PATH = os.path.join(PROJECT_DIR, ".venv", "Scripts", "python.exe")
LAZY_SEGMENT_SCRIPT_PATH = os.path.join(PROJECT_DIR, "lazy_tools", "lazy_segment.py")

# Temporary file configuration
TEMP_DIR = tempfile.gettempdir()
TEMP_INPUT_FILENAME = "krita_segment_input.png"
TEMP_OUTPUT_CUTOUT_FILENAME = "krita_segment_output.png"  # PNG for transparency
TEMP_OUTPUT_OVERLAY_FILENAME = "krita_segment_output.jpg"  # JPG for overlay

# Environment configuration for subprocess
SUBPROCESS_ENV_VARS = {
    'PYTHONIOENCODING': 'utf-8',
    'PYTHONUTF8': '1'
}

# UI Configuration
DEFAULT_OUTPUT_TYPE = 'overlay'
SUPPORTED_OUTPUT_TYPES = ['overlay', 'cutout']

# File extensions by output type
OUTPUT_FILE_EXTENSIONS = {
    'overlay': '.jpg',
    'cutout': '.png'
}


def get_temp_input_path():
    """Get the full path for temporary input file."""
    return os.path.join(TEMP_DIR, TEMP_INPUT_FILENAME)


def get_temp_output_path(output_type='overlay'):
    """Get the full path for temporary output file based on output type."""
    if output_type == 'cutout':
        return os.path.join(TEMP_DIR, TEMP_OUTPUT_CUTOUT_FILENAME)
    else:
        return os.path.join(TEMP_DIR, TEMP_OUTPUT_OVERLAY_FILENAME)


def validate_paths():
    """Validate that required paths exist."""
    errors = []
    
    if not os.path.exists(VENV_PYTHON_PATH):
        errors.append(f"Virtual environment not found at: {VENV_PYTHON_PATH}")
    
    if not os.path.exists(LAZY_SEGMENT_SCRIPT_PATH):
        errors.append(f"Segmentation script not found at: {LAZY_SEGMENT_SCRIPT_PATH}")
    
    return errors


def get_clean_subprocess_env():
    """Get a clean environment for subprocess execution."""
    clean_env = os.environ.copy()
    
    # Remove Python-specific variables to avoid conflicts with Krita
    clean_env.pop('PYTHONPATH', None)
    clean_env.pop('PYTHONHOME', None)
    
    # Add our custom environment variables
    clean_env.update(SUBPROCESS_ENV_VARS)
    
    return clean_env
