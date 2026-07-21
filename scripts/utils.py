from pathlib import Path
import yaml


CONFIG_PATH = Path.home() / "Projects" / "obsidian-gamification" / "config.yaml"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def vault_path():
    return Path(load_config()["vault_path"])


def absolute_path(relative_path: str):
    return vault_path() / relative_path


def check_structure():
    config = load_config()

    required = [
        config["tasks_folder"],
        config["archive_folder"],
        config["gamification_folder"],
        config["transactions_folder"],
        config["rewards_folder"],
    ]

    print("Checking vault structure...\n")

    missing = False

    for folder in required:
        p = absolute_path(folder)
        if p.exists():
            print(f"✓ {folder}")
        else:
            print(f"✗ {folder}")
            missing = True

    return not missing


if __name__ == "__main__":
    check_structure()
