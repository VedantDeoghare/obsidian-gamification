from datetime import date, timedelta

from gamification.utils import to_date


def update_streak(ledger):
    """
    Updates the current and longest streak.

    Rules
    -----
    First task ever:
        streak = 1

    Same day:
        do nothing

    Yesterday:
        streak += 1

    Older:
        streak = 1
    """

    today = date.today()

    last_active = to_date(
        ledger.get("lastactivedate")
    )

    current = int(
        ledger.get("currentstreak", 0)
    )

    longest = int(
        ledger.get("longeststreak", 0)
    )

    if last_active is None:

        current = 1

    elif last_active == today:
        return ledger

    elif last_active == today - timedelta(days=1):

        current += 1

    else:

        current = 1

    longest = max(
        longest,
        current
    )

    ledger["currentstreak"] = current
    ledger["longeststreak"] = longest
    ledger["lastactivedate"] = today.isoformat()

    return ledger