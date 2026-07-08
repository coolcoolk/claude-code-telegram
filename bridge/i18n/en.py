"""English string catalog.

One entry per messages.py constant, keyed by the snake_case of the constant
name. Values are RAW templates: any {placeholder}, command literal (e.g.
/skills), or code-like token is preserved verbatim so call sites can .format().
This is the canonical fallback catalog: every key MUST exist here.

Model-facing prompts are NOT in this catalog. Anything sent to Claude (photo/doc
prompts, resume continuation, system prompt fragment, tool denials) lives as
plain English constants in bridge/messages.py and is never translated.
"""

STRINGS = {
    # --- Access control ---
    "no_permission": (
        "Sorry, you don't have permission to use this bot.\n"
        "Please contact the admin for access."
    ),
    "no_permission_callback": "No permission to use this feature",
    # --- Born-locked ownership / claim flow ---
    "claim_success": "You are now the owner of this bot.",
    "claim_code_log": (
        "CLAIM CODE: {code} -- send '/claim {code}' to this bot from your Telegram "
        "account to become the owner."
    ),
    "owner_lock_missing_log": (
        "owner.lock missing but instance already claimed; reclaim required"
    ),
    # --- Commands ---
    "welcome": (
        "Hello, {name}! Send a message to start chatting."
    ),
    "new_session": (
        "Switched to a new session."
    ),
    "model_switched": "Switched: {label}",
    "model_select": (
        "Select a Claude model:\n"
        "Note: switching models starts a new session."
    ),
    "model_switch_warning": "Note: switching models starts a new session.",
    "model_unknown": (
        "Unknown model '{name}'. Allowed models: {allowed}"
    ),
    "stop_paused": "Session stopped.",
    "stop_nothing": "Nothing running.",
    "no_session": "No active session. Start a conversation first.",
    "task_terminated": "Task terminated.",
    # --- Help ---
    "help_text": (
        "Available commands:\n"
        "/start - Start / greeting\n"
        "/new - Start a new session\n"
        "/stop - Stop the current run\n"
        "/model - Switch model (starts a new session)\n"
        "/resume - Resume a previous session\n"
        "/history - Show recent history\n"
        "/skills - List installed skills\n"
        "/usage - Claude usage / limits\n"
        "/help - Show this help\n\n"
        "Any /name runs the matching skill.\n"
        "First-time setup: send /claim <code> to become the owner. "
        "File access outside PROJECT_ROOT asks for one-time confirmation."
    ),
    # --- Skills listing (read from SKILL.md frontmatter) ---
    "skills_none": "No skills installed.",
    "skills_header_project": "Project skills",
    "skills_header_global": "Global skills",
    # --- BotCommand menu descriptions ---
    "cmd_desc_new": "Start new session",
    "cmd_desc_stop": "Stop execution",
    "cmd_desc_model": "Switch model (new session)",
    "cmd_desc_resume": "Resume session",
    "cmd_desc_history": "View message history",
    "cmd_desc_skills": "List skills",
    "cmd_desc_usage": "Claude usage / limits",
    "cmd_desc_help": "Show help",
    # --- Usage report (/usage -> routines/claude-usage.sh) ---
    "usage_script_missing": "Usage script not found (routines/claude-usage.sh).",
    "usage_timeout": "The usage lookup did not finish in time. Please try again shortly.",
    "usage_failed": "Usage lookup failed: {error}",
    # --- Resume (session history) ---
    "no_session_history": "No session history found.",
    "session_history_header": "Session History",
    "resume_hint": "Reply with a number to switch to that session:",
    "resume_switched": "Switched to session: {msg}",
    "resume_invalid_number": "Invalid number, please try again.",
    # --- History ---
    "no_history": "No history available for this session.",
    "history_header": "Recent History (last 5 messages)",
    # --- Queue / overflow ---
    "queue_busy": "Processing previous messages, please wait or send /stop to terminate.",
    # --- Slash command usage ---
    "usage_skill": "Usage: /skill <name> [args]",
    "usage_command": "Usage: /command <name> [args]",
    # --- Options keyboard ---
    "select_prompt": "Please select:",
    "selected": "Selected: {choice}",
    # --- External file confirmation ---
    "external_file_prompt": (
        "File paths outside PROJECT_ROOT detected. Confirmation required before "
        "sending."
    ),
    "external_file_send": "Send external files",
    "external_file_cancel": "Cancel",
    "external_file_cancelled": "External file sending cancelled.",
    "external_file_none": "No pending external files.",
    "external_file_confirmed": "Confirmed. Sending external files...",
    # --- Timeout / resume ---
    "timeout_paused": (
        "Paused after {timeout} seconds. Tap the button below to continue."
    ),
    "timeout_no_resume": (
        "Work stopped on timeout, but no session was found to resume. "
        "Please send your request again."
    ),
    "tap_to_continue": "Continue",
    "timeout_tap_notice": "Stopped on timeout. Tap to continue.",
    "resume_expired": (
        "This button was already handled or has expired. Please request again."
    ),
    "resume_continuing": "Continuing...",
    "still_working": (
        "Taking a little while. Still working, continuing automatically."
    ),
    "resume_failed": "Resume failed: {error}",
    # --- Voice ---
    "voice_too_long": "Voice message is too long. Max duration is {seconds} seconds.",
    "voice_download_failed": "Failed to download your voice message. Please retry.",
    "photo_download_failed": "Failed to receive the photo. Please send it again.",
    "doc_download_failed": "Failed to receive the file. Please send it again.",
    "voice_convert_failed": (
        "Failed to convert audio for transcription. "
        "Please ensure ffmpeg is installed and try again."
    ),
    "voice_unavailable": (
        "Voice transcription is not configured (local whisper unavailable). "
        "Install faster-whisper."
    ),
    "voice_empty": "No speech was detected in your voice message. Please try again.",
    "voice_transcribe_failed": (
        "Failed to transcribe your voice message. Please try again later."
    ),
    # --- Errors ---
    "internal_error": "Internal error: {error}",
    "processing_failed": "Processing failed: {error}",
    "generic_error": (
        "Sorry, an error occurred while processing your message.\nError: {error}"
    ),
    "network_timeout": "Network connection timed out. Please try again shortly.",
    # --- File send failure (send_file:: retry exhausted) ---
    "send_file_failed": (
        "Warning: failed to send file '{filename}' (network error). "
        "Please try again in a moment."
    ),
    # --- Outage / failure notices ---
    "outage_recovered": (
        "Reconnected to Telegram after about {minutes} min offline. "
        "Anything you sent during that window may have been missed - please resend "
        "if needed."
    ),
    "proactive_turn_failed": (
        "A background turn ended without a reply (model overloaded or an API error "
        "after retries). Nothing was delivered - please ask again."
    ),
}
