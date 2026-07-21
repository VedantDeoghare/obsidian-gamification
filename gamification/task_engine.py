from datetime import date, datetime

from gamification.utils import (
    read_markdown,
    write_markdown,
    load_config,
)


config = load_config()


# ------------------------------------------------------------
# Date Helpers
# ------------------------------------------------------------

def to_date(value):
    """
    Convert Obsidian/PyYAML date values to a Python date object.
    """

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
# XP Calculation
# ------------------------------------------------------------

def calculate_base_xp(task):
    """
    Calculate XP before penalties.

    If the task has an XP property, use it.
    Otherwise calculate XP from importance and urgency.
    """

    manual_xp = task.get("xp")

    if manual_xp not in (None, "", " "):
        return float(manual_xp)

    importance = float(task.get("importance", 5))
    urgency = float(task.get("urgency", 5))

    base = config["xp"]["base"]
    importance_mult = config["xp"]["importance_multiplier"]
    urgency_mult = config["xp"]["urgency_multiplier"]

    xp = (
        base
        + (importance * importance_mult)
        + (urgency * urgency_mult)
    )

    return round(xp, 2)

def ensure_xp(task_path, task, body, keymap):
    """
    If XP is empty, calculate it and save it back to the task.
    """

    manual_xp = task.get("xp")

    if manual_xp not in (None, "", " "):
        return float(manual_xp)

    importance = float(task.get("importance", 5))
    urgency = float(task.get("urgency", 5))

    xp = (
        config["xp"]["base"]
        + importance * config["xp"]["importance_multiplier"]
        + urgency * config["xp"]["urgency_multiplier"]
    )

    xp = round(xp, 2)

    task["xp"] = xp

    write_markdown(
        task_path,
        task,
        body,
        keymap,
    )

    return xp

def calculate_penalty(task):
    """
    Calculate overdue penalty.
    """

    due = to_date(task.get("due"))

    if due is None:
        return 0

    today = date.today()

    overdue_days = (today - due).days

    if overdue_days <= 0:
        return 0

    penalty_per_day = float(
        task.get(
            "penalty",
            config["default_penalty"]
        )
    )

    return round(overdue_days * penalty_per_day, 2)


def calculate_final_xp(task):
    """
    Returns a dictionary containing all XP information.
    """

    base_xp = calculate_base_xp(task)

    penalty = calculate_penalty(task)

    final_xp = max(base_xp - penalty, 0)

    return {
        "base_xp": base_xp,
        "penalty": penalty,
        "earned_xp": round(final_xp, 2),
    }


# ------------------------------------------------------------
# Public API
# ------------------------------------------------------------

def process_task(task_path):
    """
    Read an Obsidian task and calculate XP.
    """

    task, body, keymap = read_markdown(task_path)

    ensure_xp(
        task_path,
        task,
        body,
        keymap,
    )

    xp_data = calculate_final_xp(task)

    return {
    "properties": task,
    "body": body,
    "xp": xp_data["earned_xp"],
    "xp_data": xp_data,
    }

# ------------------------------------------------------------
# Standalone Test
# ------------------------------------------------------------

if __name__ == "__main__":

    from gamification.utils import absolute_path

    task = absolute_path(
        "Personal Collections/Tasks/Test XP.md"
    )

    result = process_task(task)

    print("\n========== TASK ==========")

    print(f"Task            : {task.stem}")
    print(f"Importance      : {result['properties'].get('importance')}")
    print(f"Urgency         : {result['properties'].get('urgency')}")
    print(f"Manual XP       : {result['properties'].get('xp')}")
    print(f"Penalty / Day   : {result['properties'].get('penalty')}")

    print()

    print(f"Base XP         : {result['xp']['base_xp']}")
    print(f"Penalty         : {result['xp']['penalty']}")
    print(f"Earned XP       : {result['xp']['earned_xp']}")

    print("==========================\n")