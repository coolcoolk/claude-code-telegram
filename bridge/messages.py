"""Centralized user-facing strings (i18n shim).

Truly-additive shim over bridge/i18n: each constant below is bound at import
time to the active-locale template via t("<key>"). Call sites keep using these
constants exactly as before (as module attributes, often with .format(...)) --
NOTHING at a call site changes. The actual catalogs live in bridge/i18n/en.py
and bridge/i18n/ko.py; the active locale comes from config.config.locale
(env LOCALE, ko/en, default en). t() returns the RAW template with any
{placeholders} intact, so call sites still do their own .format(...).

To add or change a string: edit the i18n catalogs (add the same key to both
en.py and ko.py), then add a matching constant here. Constant names and count
must stay in parity with the catalog keys.

EXCEPTION -- model-facing strings: anything sent to Claude (photo/doc prompts,
resume continuation, system prompt fragment, tool denials) is NOT i18n. It is
defined here directly as a plain English constant, single source, never
translated. Keep them short, direct, imperative.
"""

from bridge.i18n import t

# --- Access control ---
NO_PERMISSION = t("no_permission")
NO_PERMISSION_CALLBACK = t("no_permission_callback")

# --- Born-locked ownership / claim flow (see bridge/ownership.py) ---
CLAIM_SUCCESS = t("claim_success")
CLAIM_CODE_LOG = t("claim_code_log")
OWNER_LOCK_MISSING_LOG = t("owner_lock_missing_log")

# --- Commands ---
WELCOME = t("welcome")
NEW_SESSION = t("new_session")
MODEL_SWITCHED = t("model_switched")
MODEL_SELECT = t("model_select")
MODEL_SWITCH_WARNING = t("model_switch_warning")
MODEL_UNKNOWN = t("model_unknown")
MODEL_STATE_FALLBACK = t("model_state_fallback")
STOP_PAUSED = t("stop_paused")
STOP_NOTHING = t("stop_nothing")
NO_SESSION = t("no_session")
TASK_TERMINATED = t("task_terminated")

# --- Help ---
HELP_TEXT = t("help_text")

# --- Skills listing ---
SKILLS_NONE = t("skills_none")
SKILLS_HEADER_PROJECT = t("skills_header_project")
SKILLS_HEADER_GLOBAL = t("skills_header_global")

# --- BotCommand menu descriptions ---
CMD_DESC_NEW = t("cmd_desc_new")
CMD_DESC_STOP = t("cmd_desc_stop")
CMD_DESC_MODEL = t("cmd_desc_model")
CMD_DESC_RESUME = t("cmd_desc_resume")
CMD_DESC_HISTORY = t("cmd_desc_history")
CMD_DESC_SKILLS = t("cmd_desc_skills")
CMD_DESC_USAGE = t("cmd_desc_usage")
CMD_DESC_HELP = t("cmd_desc_help")

# --- Usage report (/usage -> routines/claude-usage.sh) ---
USAGE_SCRIPT_MISSING = t("usage_script_missing")
USAGE_TIMEOUT = t("usage_timeout")
USAGE_FAILED = t("usage_failed")

# --- Slash command usage ---
USAGE_SKILL = t("usage_skill")
USAGE_COMMAND = t("usage_command")

# --- Inbound photo / document prompts (model-facing, English only) ---
PHOTO_PROMPT_SINGLE = (
    "User sent a photo. Read the image file at the path below, then respond."
)
PHOTO_PROMPT_PATH = "Image path: {path}"
PHOTO_PROMPT_ALBUM = (
    "User sent {count} photos as one album. Read ALL image files at the paths "
    "below, consider them together, answer in ONE response."
)
PHOTO_PROMPT_ALBUM_PATH = "Image {index} path: {path}"
DOC_PROMPT = (
    "User sent a file. Read the file at the path below, then respond."
)
DOC_PROMPT_PATH = "File path: {path}"
USER_CAPTION = "User caption: {caption}"

# --- Resume (session history) ---
NO_SESSION_HISTORY = t("no_session_history")
SESSION_HISTORY_HEADER = t("session_history_header")
RESUME_HINT = t("resume_hint")
RESUME_SWITCHED = t("resume_switched")
RESUME_INVALID_NUMBER = t("resume_invalid_number")

# --- History ---
NO_HISTORY = t("no_history")
HISTORY_HEADER = t("history_header")

# --- Queue / overflow ---
QUEUE_BUSY = t("queue_busy")

# --- Options keyboard ---
SELECT_PROMPT = t("select_prompt")
SELECTED = t("selected")

# --- External file confirmation ---
EXTERNAL_FILE_PROMPT = t("external_file_prompt")
EXTERNAL_FILE_SEND = t("external_file_send")
EXTERNAL_FILE_CANCEL = t("external_file_cancel")
EXTERNAL_FILE_CANCELLED = t("external_file_cancelled")
EXTERNAL_FILE_NONE = t("external_file_none")
EXTERNAL_FILE_CONFIRMED = t("external_file_confirmed")

# --- Timeout / resume (A4) ---
TIMEOUT_PAUSED = t("timeout_paused")
TIMEOUT_NO_RESUME = t("timeout_no_resume")
TAP_TO_CONTINUE = t("tap_to_continue")
TIMEOUT_TAP_NOTICE = t("timeout_tap_notice")
RESUME_EXPIRED = t("resume_expired")
RESUME_CONTINUING = t("resume_continuing")
STILL_WORKING = t("still_working")
RESUME_FAILED = t("resume_failed")

# A4 continuation prompt re-issued to Claude on resume (model-facing).
RESUME_CONTINUATION_PROMPT = (
    "Previous task was cut off by a time limit. Continue from where it "
    "stopped. Do NOT start over. Skip parts already done, finish only the "
    "remaining work."
)

# --- Voice ---
VOICE_TOO_LONG = t("voice_too_long")
VOICE_DOWNLOAD_FAILED = t("voice_download_failed")
PHOTO_DOWNLOAD_FAILED = t("photo_download_failed")
DOC_DOWNLOAD_FAILED = t("doc_download_failed")
VOICE_CONVERT_FAILED = t("voice_convert_failed")
VOICE_UNAVAILABLE = t("voice_unavailable")
VOICE_EMPTY = t("voice_empty")
VOICE_TRANSCRIBE_FAILED = t("voice_transcribe_failed")

# --- Errors ---
INTERNAL_ERROR = t("internal_error")
PROCESSING_FAILED = t("processing_failed")
GENERIC_ERROR = t("generic_error")

# --- Outage / failure notices ---
OUTAGE_RECOVERED = t("outage_recovered")
PROACTIVE_TURN_FAILED = t("proactive_turn_failed")

# --- System prompt fragment (model-facing, English only) ---
SYSTEM_PROMPT = (
    "\n\n## User Questions and Choices\n\n"
    "The AskUserQuestion tool is NOT available in this environment. "
    "When you need to ask the user a question with multiple choice options:\n"
    "1. Output the question and context clearly\n"
    "2. List options with numbers (1., 2., 3., ...)\n"
    "3. STOP and WAIT for the user's response\n"
    "4. Do NOT continue execution or make assumptions\n"
    "5. Do NOT try to use the AskUserQuestion tool\n\n"
    "## Sending Images and Files\n\n"
    "When the user asks you to send/show/deliver an image or file, do NOT read it "
    "with the Read tool. Instead, output a line that starts with 'send_file::' "
    "followed by the absolute path. One file per line. The system detects these "
    "lines and sends the files to the user.\n"
    "Example: send_file:: /path/to/image.png\n"
    "Supported image formats: .png, .jpg, .jpeg, .gif, .webp; other files are sent "
    "as documents. After generating a file, always include its send_file:: line."
)

# Denial message returned to Claude when it tries AskUserQuestion.
ASK_USER_QUESTION_DENY = (
    "AskUserQuestion is not available in this environment. "
    "Do NOT mention this to the user. Instead, output the question followed by "
    "numbered options (1., 2., 3., ...), then STOP and WAIT for the user's choice. "
    "The system converts the numbered options into clickable buttons."
)

# Denial message returned to Claude when an out-of-root path is detected.
OUTSIDE_PATH_DENY = (
    "Detected access to paths outside PROJECT_ROOT. Requires confirmation.\n"
    "{preview}\n"
    "Output these two options to the user and wait for a reply:\n"
    "1. {allow_token} (Allow this external path access)\n"
    "2. {deny_token} (Deny)"
)

# Denial returned to Claude for a protected/out-of-root path on a no-pending
# (background/proactive) turn, where no interactive confirm is possible.
OUTSIDE_PATH_DENY_NO_CONFIRM = (
    "Access to a protected or out-of-root path was denied. This is a "
    "background turn with no user available to confirm it. Skip this path or "
    "ask the user directly in their next message."
)
