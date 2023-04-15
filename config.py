import json

def load_language(lang: str = "en") -> dict:
    """Load language file from disk.

    Args:
        lang (str, optional): Language code. Defaults to "en".

    Raises:
        FileNotFoundError: Raised if language file is not found.

    Returns:
        dict: Dictionary containing language strings.
    """    
    try:
        with open(f"languages/{lang}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        if lang != "en":
            return load_language("en")
        else:
            raise FileNotFoundError("Language file not found.")
        
def load_config() -> dict:
    """Load config file from disk.

    Raises:
        FileNotFoundError: Raised if config file is not found.

    Returns:
        dict: Dictionary containing config values.
    """    
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("Config file not found.")
    
def save_config(config: dict) -> None:
    """Save config file to disk.

    Args:
        config (dict): Dictionary containing config values.
    """
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
