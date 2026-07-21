"""
Reward Engine

Redeems rewards using available XP.
"""

from datetime import datetime

from gamification.utils import (
    load_config,
    absolute_path,
    read_markdown,
    write_markdown,
)

from gamification.ledger import (
    current_xp,
    spend_xp,
)

from gamification.transaction_engine import (
    create_transaction,
)

config = load_config()


def update_history(body, cost):
    """
    Append a redemption entry to the
    Redemption History section.
    """

    entry = (
        f"- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
        f"— Redeemed ({cost} XP)"
    )

    heading = "## Redemption History"

    if heading not in body:
        body += f"\n\n{heading}\n\n"

    body += f"\n{entry}"

    return body


def redeem_reward(reward_path):

    reward, body, keymap = read_markdown(reward_path)

    cost = int(reward.get("cost", 0))

    if current_xp() < cost:
        raise Exception(
            f"Not enough XP ({current_xp()}/{cost})"
        )

    spend_xp(cost)

    count = int(reward.get("timesredeemed", 0))

    reward["timesredeemed"] = str(count + 1)
    reward["lastredeemed"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    body = update_history(body, cost)
    body = body.replace(
    "- [x] Redeem Reward",
    "- [ ] Redeem Reward",
    1,
    )
    reward_name = reward.get("title")

    if not reward_name:
        reward_name = reward_path.stem

    write_markdown(
        reward_path,
        reward,
        body,
        keymap,
    )

    create_transaction(
    task_path=reward_path,
    task_name=reward_name,
    xp=-cost,
    penalty=0,
    transaction_type="Reward",
)

    print()
    print("==============================")
    print("Reward Redeemed")
    print("==============================")
    print(f"Reward : {reward_name}")
    print(f"Cost   : {cost} XP")
    print(f"Left   : {current_xp()} XP")
    print()

    return reward

def should_redeem(body):
    return "- [x] Redeem Reward" in body

def scan_rewards():

    rewards_folder = absolute_path(
        config["rewards_folder"]
    )

    for reward_file in rewards_folder.rglob("*.md"):

        try:
            reward, body, keymap = read_markdown(reward_file)

            if reward.get("type", "").lower() != "reward":
                continue

            if should_redeem(body):
                redeem_reward(reward_file)

        except Exception as e:
            print(f"Skipped {reward_file.name}: {e}")

def main():

    scan_rewards()

    reward_name = input(
        "\nEnter reward filename (without .md): "
    ).strip()

    rewards_folder = absolute_path(
        config["rewards_folder"]
    )

    reward_file = rewards_folder / f"{reward_name}.md"

    if not reward_file.exists():
        print("Reward not found.")
        return

    try:
        redeem_reward(reward_file)

    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()