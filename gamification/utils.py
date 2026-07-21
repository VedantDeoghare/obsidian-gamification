from pathlib import Path
from datetime import date, datetime
import yaml

# ------------------------------------------------------------
# Project Configuration
# ------------------------------------------------------------

PROJECT_ROOT = Path.home() / "Projects" / "obsidian-gamification"
CONFIG_FILE = PROJECT_ROOT / "config.yaml"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


CONFIG = load_config()

# ------------------------------------------------------------
# Vault Helpers
# ------------------------------------------------------------

def vault_path():
    return Path(CONFIG["vault_path"])


def absolute_path(relative_path):
    return vault_path() / relative_path

# ------------------------------------------------------------
# Date Helpers
# ------------------------------------------------------------

def to_date(value):
    """Convert YAML values into datetime.date"""

    if value is None:
        return None

    if isinstance(value, date) and not isinstance(value, datetime):
        return value

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                return None

    return None

# ------------------------------------------------------------
# Frontmatter Helpers
# ------------------------------------------------------------

def normalize_properties(properties):
    """
    Converts keys to lowercase while remembering original names.
    """

    normalized = {}
    keymap = {}

    for key, value in properties.items():
        lower = str(key).lower()
        normalized[lower] = value
        keymap[lower] = key

    return normalized, keymap


def restore_property_names(properties, keymap):
    """
    Restores original property names before writing.
    """

    restored = {}

    for key, value in properties.items():
        restored[keymap.get(key, key)] = value

    return restored


def read_markdown(path):
    """
    Returns:
        properties,
        body,
        keymap
    """

    text = Path(path).read_text(encoding="utf-8")

    if not text.startswith("---"):
        raise Exception(f"{path} has no YAML frontmatter.")

    _, yaml_text, body = text.split("---", 2)

    properties = yaml.safe_load(yaml_text) or {}

    properties, keymap = normalize_properties(properties)

    return properties, body.lstrip(), keymap


def write_markdown(path, properties, body, keymap=None):
    """
    Writes markdown with preserved property names.
    """

    if keymap:
        properties = restore_property_names(properties, keymap)

    content = (
        "---\n"
        + yaml.safe_dump(
            properties,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        )
        + "---\n\n"
        + body
    )

    Path(path).write_text(content, encoding="utf-8")