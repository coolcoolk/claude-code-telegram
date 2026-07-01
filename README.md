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

## Configuration
See `bridge/.env.example` for all keys — token, allowed users, optional Claude CLI path,
session/timeout knobs, streaming cadence, and voice settings.

## License
MIT — see [LICENSE](LICENSE). Originally built for the Dogany agent project.
