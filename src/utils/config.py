from pathlib import Path
import yaml


def load_config(config_path: str | Path) -> dict:
    """
    Load a YAML configuration file.

    Parameters
    ----------
    config_path : str or Path
        Path to YAML configuration file.

    Returns
    -------
    dict
        Parsed configuration dictionary.
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config