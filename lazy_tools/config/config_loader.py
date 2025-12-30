import os
import json


def get_config_path():
    """Get the path to the common.json configuration file"""
    config_dir = os.path.dirname(__file__)
    return os.path.join(config_dir, "common.json")


def get_default_config():
    """Get the default configuration settings

    Returns:
        dict: Default configuration with all scripts enabled
    """
    return {
        "screen_color_picker": {
            "enabled": True
        },
        "disable_top_menu_shortcuts": {
            "enabled": True
        }
    }


def ensure_config_exists():
    """Ensure the configuration file exists, create with defaults if not

    Returns:
        bool: True if config exists or was created successfully, False on error
    """
    config_path = get_config_path()
    config_dir = os.path.dirname(config_path)

    # Create config directory if it doesn't exist
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)
        except OSError:
            return False

    # Create default config file if it doesn't exist
    if not os.path.exists(config_path):
        default_config = get_default_config()
        if not save_config(default_config):
            return False

    # Create name_color_list.txt if it doesn't exist
    name_color_list_path = os.path.join(config_dir, "name_color_list.txt")
    if not os.path.exists(name_color_list_path):
        try:
            with open(name_color_list_path, "w", encoding="utf-8") as f:
                pass  # Create empty file
        except IOError:
            return False

    return True


def load_config():
    """Load settings from the common.json file"""
    config_path = get_config_path()

    if not os.path.exists(config_path):
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(config_data):
    """Save settings to the common.json file

    Args:
        config_data (dict): Configuration data to save
    """
    config_path = get_config_path()

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except IOError:
        return False


def get_script_enabled(script_name):
    """Get the enabled status of a specific script

    Args:
        script_name (str): Name of the script (e.g., "screen_color_picker")

    Returns:
        bool: True if enabled, False if disabled or not found
    """
    config = load_config()

    if script_name not in config:
        return False

    return config[script_name].get("enabled", False)


def set_script_enabled(script_name, enabled):
    """Set the enabled status of a specific script

    Args:
        script_name (str): Name of the script
        enabled (bool): True to enable, False to disable

    Returns:
        bool: True if save was successful, False otherwise
    """
    config = load_config()

    if script_name not in config:
        config[script_name] = {}

    config[script_name]["enabled"] = enabled

    return save_config(config)


def get_all_scripts_status():
    """Get the enabled status of all scripts

    Returns:
        dict: Dictionary with script names as keys and enabled status as values
    """
    config = load_config()
    status = {}

    for script_name, script_data in config.items():
        status[script_name] = script_data.get("enabled", False)

    return status


def get_name_color_list_path():
    """Get the path to the name_color_list.txt file

    Returns:
        str: Absolute path to the name_color_list.txt file
    """
    config_dir = os.path.dirname(__file__)
    return os.path.join(config_dir, "name_color_list.txt")


def load_name_color_list():
    """Load the content of name_color_list.txt file

    Returns:
        str: Content of the file as text, empty string if file doesn't exist or on error
    """
    file_path = get_name_color_list_path()

    if not os.path.exists(file_path):
        return ""

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except IOError:
        return ""


def save_name_color_list(content):
    """Save content to the name_color_list.txt file

    Args:
        content (str): Text content to save

    Returns:
        bool: True if save was successful, False otherwise
    """
    file_path = get_name_color_list_path()

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except IOError:
        return False
