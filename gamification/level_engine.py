"""
Level Engine

Calculates:
- Current Level
- XP to next level
- Progress percentage
- Progress bar
"""

import math


# ------------------------------------------------------------
# XP Formula
# ------------------------------------------------------------

def xp_required(level):
    """
    Total lifetime XP required to reach a level.

    Formula:
        XP = 50 × level × (level - 1)
    """

    if level <= 1:
        return 0

    return 50 * level * (level - 1)


# ------------------------------------------------------------
# Determine Current Level
# ------------------------------------------------------------

def get_level(total_xp):
    """
    Determine the player's level from lifetime XP.
    """

    level = 1

    while xp_required(level + 1) <= total_xp:
        level += 1

    return level


# ------------------------------------------------------------
# Progress Information
# ------------------------------------------------------------

def level_info(total_xp):
    """
    Returns all level information.
    """

    level = get_level(total_xp)

    current_level_xp = xp_required(level)
    next_level_xp = xp_required(level + 1)

    xp_into_level = total_xp - current_level_xp
    xp_needed = next_level_xp - current_level_xp

    progress = (
        (xp_into_level / xp_needed) * 100
        if xp_needed > 0 else 100
    )

    xp_remaining = next_level_xp - total_xp

    return {
        "level": level,
        "current_level_xp": current_level_xp,
        "next_level_xp": next_level_xp,
        "xp_remaining": xp_remaining,
        "progress": round(progress, 2),
    }


# ------------------------------------------------------------
# Progress Bar
# ------------------------------------------------------------

def progress_bar(progress, width=20):
    """
    Returns a text progress bar.
    """

    filled = math.floor((progress / 100) * width)

    return (
        "█" * filled
        + "░" * (width - filled)
    )


# ------------------------------------------------------------
# Standalone Test
# ------------------------------------------------------------

if __name__ == "__main__":

    xp = 425

    info = level_info(xp)

    print()

    print("========== LEVEL ==========")

    print(f"Lifetime XP     : {xp}")
    print(f"Level           : {info['level']}")
    print(f"Current LevelXP : {info['current_level_xp']}")
    print(f"Next Level XP   : {info['next_level_xp']}")
    print(f"XP Remaining    : {info['xp_remaining']}")
    print(f"Progress        : {info['progress']}%")

    print(progress_bar(info["progress"]))

    print("===========================\n")