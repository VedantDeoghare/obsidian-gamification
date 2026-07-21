"""
Transaction Engine

Creates transaction records and prevents duplicate XP awards.
"""

from pathlib import Path
from datetime import datetime
import yaml

from gamification.utils import (
    load_config,
    absolute_path,
)

config = load_config()

TRANSACTION_FOLDER = absolute_path(
    config["transactions_folder"]
)


def ensure_folder():
    TRANSACTION_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )


def transaction_exists(task_path):
    """
    Returns True if this task has already been rewarded.
    """

    ensure_folder()

    task_path = str(Path(task_path).resolve())

    for file in TRANSACTION_FOLDER.glob("*.md"):

        try:
            text = file.read_text(encoding="utf-8")

            if not text.startswith("---"):
                continue

            _, yaml_text, _ = text.split("---", 2)

            data = yaml.safe_load(yaml_text) or {}

            if data.get("taskPath") == task_path:
                return True

        except Exception:
            continue

    return False


def create_transaction(
    task_path,
    task_name,
    xp,
    penalty=0,
    transaction_type="XP",
):
    """
    Create a transaction markdown file.
    """

    ensure_folder()

    now = datetime.now()

    filename = (
        now.strftime("%Y-%m-%d_%H-%M-%S")
        + "_"
        + task_name.replace("/", "-")
        + ".md"
    )

    file_path = TRANSACTION_FOLDER / filename

    properties = {
        "type": transaction_type,
        "task": task_name,
        "taskPath": str(Path(task_path).resolve()),
        "xpAwarded": xp,
        "penalty": penalty,
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
    }

    content = (
        "---\n"
        + yaml.safe_dump(
            properties,
            sort_keys=False,
            allow_unicode=True,
        )
        + "---\n\n"
        + f"# {task_name}\n\n"
        + f"Earned **{xp} XP**\n"
    )

    file_path.write_text(content, encoding="utf-8")

    return file_path