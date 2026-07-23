"""
Habit Engine

Scans the Habits folder and awards XP for completed habits.
"""

from datetime import datetime, date, timedelta

from gamification.utils import (
    load_config,
    absolute_path,
    read_markdown,
    write_markdown,
    to_date,
)

from gamification.ledger import award_xp

from gamification.transaction_engine import (
    create_transaction,
)

config = load_config()


def should_log(body):
    """
    Returns True if the habit is marked for logging.
    """
    return "- [x] Log Habit" in body

def update_log(body, value, unit, xp):
    """
    Add a new activity at the top of Activity Log.
    """

    heading = "## Activity Log"

    entry = (
        f"- {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
        f"{value} {unit} | +{xp} XP"
    )

    lines = body.splitlines()

    # Find Activity Log heading
    for i, line in enumerate(lines):
        if line.strip() == heading:
            # Insert immediately after heading
            lines.insert(i + 1, "")
            lines.insert(i + 2, entry)
            break
    else:
        # Heading not found
        lines.append("")
        lines.append(heading)
        lines.append("")
        lines.append(entry)

    return "\n".join(lines)

def calculate_habit_xp(habit):
    """
    Calculate XP earned for this habit.
    """

    value = float(habit.get("value", 0))
    xp_per_unit = float(habit.get("xpperunit", 1))

    return round(value * xp_per_unit, 2)


def update_habit_streak(habit):
    """
    Update the streak for an individual habit.

    Rules:
        - First completion -> streak = 1
        - Same day -> no change
        - Yesterday -> streak + 1
        - Missed one or more days -> streak = 1
    """

    today = date.today()

    last_completed = to_date(
        habit.get("lastcompleted")
    )

    current = int(
        habit.get("currentstreak", 0)
    )

    longest = int(
        habit.get("longeststreak", 0)
    )

    # First ever completion
    if last_completed is None:
        current = 1

    # Already logged today
    elif last_completed == today:
        return habit

    # Consecutive day
    elif last_completed == today - timedelta(days=1):
        current += 1

    # Missed one or more days
    else:
        current = 1

    longest = max(longest, current)

    habit["currentstreak"] = current
    habit["longeststreak"] = longest
    habit["lastcompleted"] = today.isoformat()

    return habit

def process_habit(habit_path):
    """
    Process a single habit.
    """

    habit, body, keymap = read_markdown(habit_path)

    if habit.get("type", "").lower() != "habit":
        return

    if not should_log(body):
        return

    value = float(habit.get("value", 0))

    if value <= 0:
        print(f"Skipping {habit_path.stem}: value is 0")
        return

    xp = calculate_habit_xp(habit)

    # Award XP
    award_xp(xp)

    # Update statistics
    habit["totalvalue"] = round(float(habit.get("totalvalue", 0)) + value,2)
    habit["timescompleted"] = int(habit.get("timescompleted", 0)) + 1
    habit= update_habit_streak(habit)

    # Reset today's value
    habit["value"] = 0

    # Untick checkbox
    body = update_log(body,value,habit.get("unit", ""),xp)
    body = body.replace("- [x] Log Habit","- [ ] Log Habit",1)

    # Save habit
    write_markdown(
        habit_path,
        habit,
        body,
        keymap,
    )

    # Create transaction
    create_transaction(
        task_path=habit_path,
        task_name=habit.get("title", habit_path.stem),
        xp=xp,
        penalty=0,
        transaction_type="Habit",
    )

    print("--------------------------------")
    print(f"Habit : {habit_path.stem}")
    print(f"Value : {value}")
    print(f"XP    : {xp}")
    print("--------------------------------")


def scan_habits():
    """
    Scan every habit in the Habits folder.
    """

    habits_folder = absolute_path(
        config["habits_folder"]
    )

    print(f"Scanning Habits: {habits_folder}")

    for habit_file in habits_folder.rglob("*.md"):

        try:
            process_habit(habit_file)

        except Exception as e:
            print(f"Skipped {habit_file.name}: {e}")


if __name__ == "__main__":
    scan_habits()