# claude-code-telegram

Run **Claude Code** as a Telegram bot. Chat with your Claude Code workspace from your
phone — streaming replies, voice input, inline approvals, and resilient long-running turns.

> Unofficial community project. Not affiliated with or endorsed by Anthropic.
> "Claude" and "Claude Code" are products of Anthropic. This bridge just drives the
> Claude Code CLI/SDK over Telegram.

## Features
- Streaming replies (live-edited Telegram messages as the model thinks).
- Voice input (local faster-whisper transcription; input only).
- Permission gating with inline buttons (approve/deny tool use from chat).
- Session management (per-chat sessions, auto-new after an idle gap, resume).
- Health checks + polling-conflict recovery (won't zombie on getUpdates conflicts).
- Two-layer polling watchdog (in-process stall detection + external heartbeat file monitor).
- Self-restart script (graceful drain + relaunch + completion ping).
- Media/album handling and message formatting for Telegram.
- Timeout resilience (guaranteed notification instead of silent stalls).

## Requirements
- Claude Code CLI installed and on PATH (`claude`).
- Python 3.11+.
- A Telegram bot token (from @BotFather).

## Quick start
```sh
git clone https://github.com/coolcoolk/claude-code-telegram
cd claude-code-telegram
python3 -m venv bridge/venv
bridge/venv/bin/pip install -r bridge/requirements.txt

cp bridge/.env.example <your-workspace>/.telegram_bot/.env
# edit that .env: set TELEGRAM_BOT_TOKEN (and ALLOWED_USER_IDS to lock it down)

PROJECT_ROOT=<your-workspace> bridge/venv/bin/python -m bridge --path <your-workspace>
```
`<your-workspace>` is the directory Claude Code runs in (its CLAUDE.md, files, sessions
live there). The bridge reads its token from `<workspace>/.telegram_bot/.env`.

## Run as a service (macOS launchd)
`examples/claude-code-telegram.plist.example` is a launchd template. Replace the
placeholders (`__PROJECT_ROOT__`, `__HOME__`, `__AGENT_NAME__`), drop it in
`~/Library/LaunchAgents/`, and `launchctl bootstrap`. `bridge/self_restart.sh` does a
graceful drain + relaunch (also placeholder-based).

## Polling watchdog
The bridge ships a two-layer zombie-polling watchdog for macOS and Linux:

- Layer 1 (in-process): `bot.py` beats a monotonic heartbeat on every `getUpdates`
  round trip. If the beat goes silent for 120 s while the process is alive (zombie
  polling after laptop sleep/wake), the polling task is restarted from inside.
- Layer 2 (external): `bridge/watchdog.sh` reads the heartbeat file's mtime every
  2 minutes. A two-strike design absorbs false alarms from sleep/wake; a confirmed
  stall triggers a full service restart via launchctl (macOS) or systemctl (Linux).

To register the watchdog as a launchd service:
1. Copy `examples/claude-code-telegram.watchdog.plist.example`, substitute the
   same `__PROJECT_ROOT__` and `__AGENT_NAME__` placeholders as the main plist,
   drop it in `~/Library/LaunchAgents/`, and `launchctl bootstrap`.
2. Or run `bridge/watchdog_setup.sh` from the project root -- it finds the
   watchdog plist in `bridge/`, substitutes it, and registers it idempotently.
   On Linux it writes a systemd user timer instead.

Watchdog activity is logged to `.telegram_bot/logs/watchdog.log`.
Notifications on restart degrade gracefully to log-only in this repo (no bundled
push script). Supply `routines/push.sh --text <msg>` at the project root to
receive Telegram alerts.

## Configuration
See `bridge/.env.example` for all keys — token, allowed users, optional Claude CLI path,
session/timeout knobs, streaming cadence, and voice settings.

## Authentication & Anthropic policy
Run Claude Code with **API-key authentication** (Claude Console). As of 2026, Anthropic's
terms do not permit using Free/Pro/Max **subscription OAuth** with the Agent SDK or
third-party harnesses; programmatic use is governed by the Commercial Terms and draws from
the Agent SDK credit pool. This project ships code only — you run it with your own account
and your own API key. It does not proxy or resell access to anyone else's account.
See Anthropic's [Agent SDK docs](https://code.claude.com/docs/en/agent-sdk/overview) and
[Usage Policy](https://www.anthropic.com/legal/aup).

## License
MIT — see [LICENSE](LICENSE). Originally built for the Dogany agent project.
