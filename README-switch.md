# claude-switch.py

Consolidated Python script for switching [Claude Code](https://docs.anthropic.com/en/docs/claude-code) between API providers — Anthropic's native API and GLM-5 via Z.AI.

Combines status checking, Anthropic switching, and GLM switching into a single file. Non-provider settings (voice, keybindings, etc.) are preserved across switches.

## Usage

### Interactive mode

Run without arguments to see the current profile and pick a new one:

```bash
python claude-switch.py
```

```
=== Claude Code Profile Status ===
Active Profile: Anthropic
API Endpoint: Default (https://api.anthropic.com)
Models: Default (managed by CLI)

Switch to:
  1) Anthropic
  2) GLM (Z.AI)
  q) Quit

>
```

### CLI mode

Pass a subcommand directly — useful for shell aliases and scripting:

```bash
python claude-switch.py status     # show current profile
python claude-switch.py anthropic  # switch to Anthropic
python claude-switch.py glm        # switch to GLM / Z.AI
```

## Setup

1. **No profile files needed.** Profiles are built into the script. On first switch to GLM, the script writes the GLM config directly into `settings.json`.

   > **Note:** The GLM profile uses a placeholder API key (`ADD-ZAI-TOKEN-HERE`). Replace it with your actual Z.AI token in `~/.claude/settings.json` after the first switch. The script will warn you if the placeholder is still present.
   >
   > If you switch back to GLM later and a valid token already exists in your settings, it is preserved automatically.

2. **Optional: add a shell alias** for faster access from any directory:

   ```bash
   # add to ~/.zshrc or ~/.bash_profile
   alias claude-switch='python /path/to/claude-switch.py'
   ```

   Then:

   ```bash
   claude-switch            # interactive
   claude-switch status
   claude-switch glm
   ```

## Behaviour

- **Atomic writes** — settings are written via a temp file and renamed into place, so a crash mid-write never corrupts `settings.json`
- **Selective merging** — only provider keys (`apiKey`, `apiUrl`, `env`) are modified; all other settings (voice, keybindings, etc.) are untouched
- **Token preservation** — if a valid Z.AI token already exists in settings, it is reused instead of being overwritten with the placeholder
- **Already-active detection** — switching to the currently active profile prints a notice instead of writing unnecessarily
- **Shell env awareness** — `status` checks `ANTHROPIC_BASE_URL` in your shell environment first, so it reflects what the CLI actually uses

## File Layout

```
~/.claude/
├── settings.json            # active config (managed by the script)
└── settings-backup.json     # auto-created before each switch
```

## Requirements

- Python 3.6+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
