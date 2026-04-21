#!/usr/bin/env python3
# Claude Code Provider Switcher
# Usage: python claude-switch.py [status|anthropic|glm]
#        Run without arguments for interactive menu

import copy
import json
import os
import shutil
import sys
from pathlib import Path

CYAN   = "\033[96m"
GREEN  = "\033[92m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

CLAUDE_DIR    = Path.home() / ".claude"
SETTINGS_PATH = CLAUDE_DIR / "settings.json"
BACKUP_PATH   = CLAUDE_DIR / "settings-backup.json"

PROVIDER_KEYS = ("apiKey", "apiUrl", "env")

PROFILES = {
    "glm": {
        "name": "GLM (Z.AI)",
        "apiKey": "ADD-ZAI-TOKEN-HERE",
        "apiUrl": "https://api.z.ai/api/anthropic",
        "env": {
            "ANTHROPIC_AUTH_TOKEN":           "ADD-ZAI-TOKEN-HERE",
            "ANTHROPIC_BASE_URL":             "https://api.z.ai/api/anthropic",
            "API_TIMEOUT_MS":                 "3000000",
            "ANTHROPIC_DEFAULT_OPUS_MODEL":   "glm-5",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-5",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL":  "glm-5",
        },
    },
    "anthropic": {
        "name": "Anthropic (Default)",
        "env": {},
    },
}


def load_settings():
    if not SETTINGS_PATH.exists():
        return {}
    try:
        with open(SETTINGS_PATH) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"{YELLOW}settings.json is malformed: {e}{RESET}")
        raise SystemExit(1)
    except PermissionError:
        print(f"{YELLOW}Permission denied reading: {SETTINGS_PATH}{RESET}")
        raise SystemExit(1)


def save_settings(data):
    # Atomic write via temp file — prevents corruption if process crashes mid-write
    temp_path = SETTINGS_PATH.with_suffix(".tmp")
    try:
        if SETTINGS_PATH.exists():
            shutil.copy2(SETTINGS_PATH, BACKUP_PATH)
            print(f"{GREEN}✓ Backed up current settings{RESET}")
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)
        temp_path.replace(SETTINGS_PATH)
    except IOError as e:
        if temp_path.exists():
            temp_path.unlink()
        print(f"{YELLOW}⚠ Error saving settings: {e}{RESET}")
        raise SystemExit(1)


def current_state():
    """Returns (base_url, env, source, raw_settings). Shell env takes priority over settings.json."""
    settings = load_settings()
    env = settings.get("env", {})
    if "ANTHROPIC_BASE_URL" in os.environ:
        base_url = os.environ["ANTHROPIC_BASE_URL"]
        source = "shell env"
    elif env.get("ANTHROPIC_BASE_URL"):
        base_url = env["ANTHROPIC_BASE_URL"]
        source = "settings.json"
    else:
        base_url = ""
        source = None
    return base_url, env, source, settings


def status():
    base_url, env, source, settings = current_state()
    json_env = settings.get("env")

    print(f"\n{CYAN}=== Claude Code Profile Status ==={RESET}")

    if "z.ai" in base_url.lower():
        def model_name(key):
            return env.get(key) or os.environ.get(key) or "Not Configured"

        print(f"{GREEN}Active Profile: GLM (Z.AI){RESET}")
        print(f"{WHITE}API Endpoint: {base_url}{RESET}")
        if source:
            print(f"{GRAY}Config source: {source}{RESET}")
        print(f"{WHITE}Models:{RESET}")
        print(f"{GRAY}  Opus:   {model_name('ANTHROPIC_DEFAULT_OPUS_MODEL')}{RESET}")
        print(f"{GRAY}  Sonnet: {model_name('ANTHROPIC_DEFAULT_SONNET_MODEL')}{RESET}")
        print(f"{GRAY}  Haiku:  {model_name('ANTHROPIC_DEFAULT_HAIKU_MODEL')}{RESET}")
    else:
        print(f"{GREEN}Active Profile: Anthropic{RESET}")
        print(f"{WHITE}API Endpoint: Default (https://api.anthropic.com){RESET}")
        print(f"{GRAY}Models: Default (managed by CLI){RESET}")


def switch(profile_key):
    base_url, _, _, settings = current_state()
    profile = copy.deepcopy(PROFILES[profile_key])  # deepcopy prevents mutating the global dict

    # Already-active check
    is_glm = "z.ai" in base_url.lower()
    if profile_key == "glm" and is_glm:
        print(f"{CYAN}ℹ GLM profile is already active.{RESET}")
    elif profile_key == "anthropic" and not is_glm:
        print(f"{CYAN}ℹ Anthropic profile is already active.{RESET}")

    # Token preservation: reuse existing valid Z.AI token rather than overwriting with placeholder
    if profile_key == "glm":
        existing_token = settings.get("env", {}).get("ANTHROPIC_AUTH_TOKEN")
        if existing_token and existing_token != "ADD-ZAI-TOKEN-HERE":
            print(f"{CYAN}ℹ Preserving existing Z.AI token.{RESET}")
            profile["env"]["ANTHROPIC_AUTH_TOKEN"] = existing_token
            profile["apiKey"] = existing_token

    # Strip provider keys from current settings then apply profile
    for key in PROVIDER_KEYS:
        settings.pop(key, None)
    settings.update({k: v for k, v in profile.items() if k != "name"})

    # Remove empty env to keep settings.json clean
    if settings.get("env") == {}:
        settings.pop("env")

    CLAUDE_DIR.mkdir(exist_ok=True)
    save_settings(settings)
    print(f"{GREEN}✓ Switched to {profile['name']}{RESET}")

    if profile_key == "glm":
        print(f"{WHITE}Models: GLM-5 (Opus/Sonnet/Haiku) via Z.AI{RESET}")
        if settings.get("env", {}).get("ANTHROPIC_AUTH_TOKEN") == "ADD-ZAI-TOKEN-HERE":
            print(f"{YELLOW}⚠ Replace 'ADD-ZAI-TOKEN-HERE' in {SETTINGS_PATH} with your actual Z.AI token{RESET}")
        print(f"\n{WHITE}Run 'claude' to start with GLM-5 via Z.AI{RESET}")
    else:
        print(f"{WHITE}Models: Default (managed by CLI){RESET}")
        print(f"\n{WHITE}Run 'claude' to start with Anthropic models{RESET}")


def interactive_menu():
    status()
    print(f"\n{CYAN}Switch to:{RESET}")
    print(f"{WHITE}  1) Anthropic{RESET}")
    print(f"{WHITE}  2) GLM (Z.AI){RESET}")
    print(f"{WHITE}  q) Quit{RESET}")

    try:
        choice = input(f"\n{CYAN}> {RESET}").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print()
        raise SystemExit(0)

    print()
    if choice == "1":
        switch("anthropic")
    elif choice == "2":
        switch("glm")
    elif choice in ("q", "quit", "exit", ""):
        raise SystemExit(0)
    else:
        print(f"{YELLOW}Invalid choice: {choice!r}{RESET}")
        raise SystemExit(1)


COMMANDS = {"status": status, "anthropic": lambda: switch("anthropic"), "glm": lambda: switch("glm")}

if __name__ == "__main__":
    if len(sys.argv) == 1:
        interactive_menu()
    elif len(sys.argv) == 2 and sys.argv[1] in COMMANDS:
        COMMANDS[sys.argv[1]]()
    else:
        valid = ", ".join(COMMANDS)
        print(f"{YELLOW}Usage: {sys.argv[0]} [{valid}]{RESET}")
        raise SystemExit(1)
