# Claude Code Provider Switcher

> **Disclaimer:** Most content in this repository is generated with AI assistance — primarily Claude Code and Gemini — and reviewed by the author before each commit. While care is taken to verify correctness, nothing here is guaranteed to work for your setup. Use any content at your own risk.

PowerShell scripts for switching [Claude Code](https://docs.anthropic.com/en/docs/claude-code) between API providers — Anthropic's native API and GLM-5 via Z.AI.

## Why

Claude Code reads its configuration from `~\.claude\settings.json`. These scripts swap that file between pre-configured profiles so you can quickly toggle providers without manual editing.

## Scripts

| Script | Purpose |
|---|---|
| `claude-anthropic.ps1` | Switch to the **Anthropic** profile (default Claude models) |
| `claude-glm.ps1` | Switch to the **GLM** profile (GLM-5 models via Z.AI) |
| `claude-status.ps1` | Display the currently active profile and its configuration |

### `claude-anthropic.ps1`

Backs up your current `settings.json` to `settings-backup.json`, then copies `settings-anthropic.json` into place. If no Anthropic settings file exists yet, it creates a minimal default.

### `claude-glm.ps1`

Backs up your current `settings.json` to `settings-backup.json`, then copies `settings-glm.json` into place. If no GLM settings file exists yet, it creates one pre-configured for the Z.AI endpoint with GLM-5 mapped to all three model slots (Opus, Sonnet, Haiku).

> **Note:** The generated default uses a placeholder API key (`ADD-ZAI-TOKEN-HERE`). Replace it with your actual Z.AI token before use.

### `claude-status.ps1`

Reads `settings.json` and detects the active profile by checking for a Z.AI base URL. Displays the profile name, API endpoint, and configured model names.

## Setup

1. **Place profile files** in `~\.claude\`:
   - `settings-anthropic.json` — your Anthropic configuration
   - `settings-glm.json` — your Z.AI / GLM configuration

2. **Add the scripts to your PATH** (e.g. copy them to `~\.local\bin\`) so they can be called by name from any directory.

3. **Run a switcher** to activate a profile:

   ```powershell
   claude-anthropic   # switch to Anthropic
   claude-glm         # switch to GLM / Z.AI
   claude-status      # check which profile is active
   ```

## File Layout

```
~\.claude\
├── settings.json            # active config (managed by the scripts)
├── settings-backup.json     # auto-created backup of the previous profile
├── settings-anthropic.json  # Anthropic profile
└── settings-glm.json        # GLM / Z.AI profile
```

## Requirements

- Windows PowerShell 5.1+ or PowerShell 7+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
