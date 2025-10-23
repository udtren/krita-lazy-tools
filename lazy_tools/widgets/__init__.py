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
SUBPROCESS_ENV_VARS = {"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

# UI Configuration
DEFAULT_OUTPUT_TYPE = "overlay"
SUPPORTED_OUTPUT_TYPES = ["overlay", "cutout"]

# SAM2 Model Configuration
SAM2_MODELS = {
    "base_plus": {
        "name": "SAM2.1 Base Plus",
        "checkpoint": "sam2.1_hiera_base_plus.pt",
        "config": "sam2.1_hiera_b+.yaml",
        "description": "Faster, good quality (recommended)",
    },
    "large": {
        "name": "SAM2.1 Large",
        "checkpoint": "sam2.1_hiera_large.pt",
        "config": "sam2.1_hiera_l.yaml",
        "description": "Slower, best quality",
    },
}

DEFAULT_SAM2_MODEL = "base_plus"

# File extensions by output type
OUTPUT_FILE_EXTENSIONS = {"overlay": ".jpg", "cutout": ".png"}


def get_temp_input_path():
    """Get the full path for temporary input file."""
    return os.path.join(TEMP_DIR, TEMP_INPUT_FILENAME)


def get_temp_output_path(output_type="overlay"):
    """Get the full path for temporary output file based on output type."""
    if output_type == "cutout":
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
    clean_env.pop("PYTHONPATH", None)
    clean_env.pop("PYTHONHOME", None)

    # Add our custom environment variables
    clean_env.update(SUBPROCESS_ENV_VARS)

    return clean_env


def get_sam2_model_options():
    """Get list of available SAM2 models for UI dropdown."""
    options = []
    for model_key, model_info in SAM2_MODELS.items():
        display_name = f"{model_info['name']}"
        options.append((model_key, display_name))
    return options


def get_sam2_model_key(display_name):
    """Get model key from display name."""
    for model_key, model_info in SAM2_MODELS.items():
        expected_display = f"{model_info['name']}"
        if display_name == expected_display:
            return model_key
    return DEFAULT_SAM2_MODEL
