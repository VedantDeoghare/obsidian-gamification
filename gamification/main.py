"""
Main Entry Point

Scans the Tasks folder for completed tasks and awards XP.
"""

from pathlib import Path

from gamification.reward_engine import scan_rewards
from gamification.utils import load_config, absolute_path, read_markdown
from gamification.task_engine import process_task
from gamification.ledger import award_xp
from gamification.habit_dashboard import generate_dashboard
from gamification.habit_engine import scan_habits
from gamification.transaction_engine import (
    transaction_exists,
    create_transaction,
)


config = load_config()


def process_completed_task(task_path):
    result = process_task(task_path)

    task = result["properties"]

    task_name = task.get("title", task_path.stem)

    xp = result["xp"]
    xp_data = result["xp_data"]

    penalty = xp_data["penalty"]

    if transaction_exists(task_path):
        print(f"✓ Skipping {task_path} (already rewarded)")
        return

    award_xp(xp)

    create_transaction(
    task_path=task_path,
    task_name=task_name,
    xp=xp,
    penalty=penalty,
    )

    print(f"✓ Awarded {xp} XP -> {task_name}")


def scan_tasks():
    tasks_folder = absolute_path(config["tasks_folder"])

    print(f"Scanning: {tasks_folder}\n")

    count = 0

    for task_file in tasks_folder.rglob("*.md"):

        try:
            properties, body, keymap = read_markdown(task_file)

            completed = (
                properties.get("iscompleted", False)
                or str(properties.get("status", "")).lower() == "completed"
            )

            if completed:
                process_completed_task(task_file)
                count += 1

        except Exception as e:
            print(f"Skipped {task_file.name}: {e}")

    print(f"\nFinished. Processed {count} completed task(s).")


def main():
    print("\n========== TASK SCAN ==========\n")
    scan_tasks()
    print("\n========== HABITS SCAN ==========\n")
    scan_habits()
    print("\n========== REWARDS SCAN ==========\n")
    scan_rewards()
    print("\n========== GENERATE HABIT DASHBOARD ==========\n")
    generate_dashboard()


if __name__ == "__main__":
    main()