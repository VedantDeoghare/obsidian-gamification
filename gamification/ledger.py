"""
Ledger Engine

Responsible for:
- Updating XP Ledger.md
- Awarding XP
- Spending XP
- Regenerating the dashboard
"""
from gamification.streak_engine import update_streak
from datetime import datetime

from gamification.utils import (
    load_config,
    absolute_path,
    read_markdown,
    write_markdown,
)

from gamification.level_engine import level_info


config = load_config()


# ------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------

def generate_dashboard(ledger):
    """
    Generate the markdown dashboard.
    """
    print("Lifetime XP:", ledger["lifetimexp"])
    print("Level Info:", level_info(ledger["lifetimexp"]))
    info = level_info(ledger["lifetimexp"])

    dashboard = f"""# XP Ledger

> 🤖 This file is automatically managed by the Obsidian Gamification Engine.

---

# 📊 Current Stats

| Stat | Value |
|------|------:|
| Current XP | {ledger["currentxp"]} |
| Lifetime XP | {ledger["lifetimexp"]} |
| XP Spent | {ledger["xpspent"]} |
| Level | {info["level"]} |
| Tasks Completed | {ledger["taskscompleted"]} |
| Rewards Redeemed | {ledger["rewardsredeemed"]} |
| Current Streak | {ledger["currentstreak"]} |
| Longest Streak | {ledger["longeststreak"]} |

---

## 🎮 Level Progress

- **Level:** {info["level"]}
- **Progress:** {info["progress"]:.2f}%
- **Current Level XP:** {info["current_level_xp"]}
- **Next Level XP:** {info["next_level_xp"]}
- **XP Remaining:** {info["xp_remaining"]}

---

# 📝 Activity Log

*(This section will be generated automatically from XP Transactions later.)*
"""

    return dashboard


# ------------------------------------------------------------
# Internal Helpers
# ------------------------------------------------------------

def load_ledger():
    """
    Load XP Ledger.md
    """

    ledger_path = absolute_path(config["ledger_file"])

    ledger, body, keymap = read_markdown(ledger_path)

    return ledger_path, ledger, body, keymap


def save_ledger(path, ledger, keymap):
    """
    Save XP Ledger.md
    """

    dashboard = generate_dashboard(ledger)

    write_markdown(
        path,
        ledger,
        dashboard,
        keymap,
    )

    # ------------------------------------------------------------
# Public API
# ------------------------------------------------------------

def award_xp(amount):
    """
    Award XP to the user.
    """

    path, ledger, body, keymap = load_ledger()

    ledger["currentxp"] = ledger.get("currentxp", 0) + amount
    ledger["lifetimexp"] = ledger.get("lifetimexp", 0) + amount
    ledger["taskscompleted"] = ledger.get("taskscompleted", 0) + 1
    update_streak(ledger)
    info = level_info(ledger["lifetimexp"])

    ledger["level"] = info["level"]
    ledger["lastupdated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_ledger(
        path,
        ledger,
        keymap,
    )

    print("-----------------------------------")
    print(f"Awarded XP      : {amount}")
    print(f"Current XP      : {ledger['currentxp']}")
    print(f"Lifetime XP     : {ledger['lifetimexp']}")
    print(f"Level           : {ledger['level']}")
    print("-----------------------------------")

    return ledger


def spend_xp(amount):
    """
    Spend XP when redeeming rewards.
    """

    path, ledger, body, keymap = load_ledger()

    current = ledger.get("currentxp", 0)

    if current < amount:
        raise Exception(
            f"Not enough XP. Current XP: {current}"
        )

    ledger["currentxp"] -= amount
    ledger["xpspent"] = ledger.get("xpspent", 0) + amount
    ledger["rewardsredeemed"] = ledger.get("rewardsredeemed", 0) + 1
    ledger["lastrewardredeemed"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ledger["lastupdated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_ledger(
        path,
        ledger,
        keymap,
    )

    print("-----------------------------------")
    print(f"Spent XP        : {amount}")
    print(f"Current XP      : {ledger['currentxp']}")
    print("-----------------------------------")

    return ledger

    # ------------------------------------------------------------
# Convenience Helpers
# ------------------------------------------------------------

def get_ledger():
    """
    Return the current ledger dictionary.
    """

    _, ledger, _, _ = load_ledger()
    return ledger


def current_xp():
    """
    Return current available XP.
    """

    return get_ledger()["currentxp"]


def lifetime_xp():
    """
    Return lifetime earned XP.
    """

    return get_ledger()["lifetimexp"]


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=== Ledger Test ===")
    print()

    ledger = award_xp(25)

    print()
    print("Updated Ledger")
    print("----------------------------")
    print(f"Current XP      : {ledger['currentxp']}")
    print(f"Lifetime XP     : {ledger['lifetimexp']}")
    print(f"XP Spent        : {ledger['xpspent']}")
    print(f"Level           : {ledger['level']}")
    print(f"Tasks Completed : {ledger['taskscompleted']}")
    print(f"Rewards         : {ledger['rewardsredeemed']}")
    print("----------------------------")