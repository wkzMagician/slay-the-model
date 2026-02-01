from typing import Any


def parse(template: str, raw_format_dict: dict[str, Any]) -> str:
    """Parse a template string with given raw_format_dict. Supports nested dicts with ':' separator."""
    # Prepare formatting dict
    format_dict = {}
    for key, value in raw_format_dict.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                format_dict[f"{key}:{subkey}"] = subvalue
        else:
            format_dict[key] = value
    try:
        return template.format(**format_dict)
    except (KeyError, ValueError) as e:
        print(f"Error parsing template: {e}")
        return template