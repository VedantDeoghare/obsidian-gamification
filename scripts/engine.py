#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import yaml

from utils import load_config, absolute_path


# ------------------------------------------------------------
# Markdown Helpers
# ------------------------------------------------------------

def read_markdown_with_frontmatter(path):
    """Read a markdown file with YAML frontmatter."""

    text = Path(path).read_text(encoding="utf-8")

    if not text.startswith("---"):
        raise Exception(f"No YAML frontmatter found in {path}")

    _, yaml_text, body = text.split("---", 2)

    data = yaml.safe_load(yaml_text)

    return data, body.lstrip()


def generate_dashboard(data):
    """Generate XP dashboard."""

    dashboard = f"""# XP Ledger

> 🤖 This file is automatically managed by the Obsidian Gamification Engine.

---

# 📊 Current Stats

| Stat | Value |
|------|------:|
| Current XP | {data['currentXP']} |
| Lifetime XP | {data['lifetimeXP']} |
| XP Spent | {data['xpSpent']} |
| Level | {data['level']} |
| Tasks Completed | {data['tasksCompleted']} |
| Rewards Redeemed | {data['rewardsRedeemed']} |
| Current Streak | {data['currentStreak']} |
| Longest Streak | {data['longestStreak']} |

---

# 📝 Activity Log

*(This section will be generated automatically from XP Transactions later.)*
"""

    return dashboard


def write_markdown_with_frontmatter(path, data):
    """Write YAML frontmatter + dashboard."""

    content = (
        "---\n"
        + yaml.safe_dump(
            data,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        )
        + "---\n\n"
        + generate_dashboard(data)
    )

    Path(path).write_text(content, encoding="utf-8")


# ------------------------------------------------------------
# XP Ledger
# ------------------------------------------------------------

def add_xp(amount):
    """Add XP to the ledger."""

    config = load_config()

    ledger_path = absolute_path(config["ledger_file"])

    ledger, _ = read_markdown_with_frontmatter(ledger_path)

    ledger["currentXP"] += amount
    ledger["lifetimeXP"] += amount

    ledger["lastUpdated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    write_markdown_with_frontmatter(ledger_path, ledger)

    print("\n-----------------------------------")
    print(f"Added XP      : {amount}")
    print(f"Current XP    : {ledger['currentXP']}")
    print(f"Lifetime XP   : {ledger['lifetimeXP']}")
    print("-----------------------------------\n")


# ------------------------------------------------------------
# Task Processing
# ------------------------------------------------------------

def calculate_xp(task):
    """Calculate earned XP after overdue penalties."""

    base_xp = int(task.get("xp") or 10)
    penalty = int(task.get("penalty") or 1)

    due = task.get("due")

    if not due:
        return base_xp

    try:
        due_date = datetime.strptime(str(due), "%Y-%m-%d").date()
    except Exception:
        return base_xp

    today = datetime.now().date()

    overdue_days = (today - due_date).days

    if overdue_days <= 0:
        return base_xp

    earned = base_xp - (overdue_days * penalty)

    return max(earned, 0)


def process_task(task_path):
    """Read a task and award XP."""

    task, _ = read_markdown_with_frontmatter(task_path)

    # Normalize all property names to lowercase
    task = {str(k).lower(): v for k, v in task.items()}

    print(task)

    earned = calculate_xp(task)

    print("\n========== TASK ==========")
    print(f"Task       : {Path(task_path).stem}")
    print(f"Base XP    : {task.get('xp', 10)}")
    print(f"Penalty    : {task.get('penalty', 1)}")
    print(f"Due Date   : {task.get('due')}")
    print(f"Earned XP  : {earned}")
    print("==========================\n")

    add_xp(earned)

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    config = load_config()

    test_task = absolute_path(
        config["tasks_folder"] + "/Test XP.md"
    )

    if not test_task.exists():
        print(f"Test task not found:\n{test_task}")
        return

    process_task(test_task)


if __name__ == "__main__":
    main()