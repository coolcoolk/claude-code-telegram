"""Korean string catalog.

One entry per messages.py constant, keyed by the snake_case of the constant
name. Values mirror en.STRINGS but in polite, concise Korean (product tone).
Every {placeholder}, command literal (e.g. /skills, /stop, /claim), and
code-like token (send_file::, PROJECT_ROOT, ffmpeg, faster-whisper) is preserved
verbatim -- only human-readable prose is translated.

Model-facing prompts are NOT in this catalog. Anything sent to Claude (photo/doc
prompts, resume continuation, system prompt fragment, tool denials) lives as
plain English constants in bridge/messages.py and is never translated.
"""

STRINGS = {
    # --- Access control ---
    "no_permission": (
        "죄송합니다. 이 봇을 사용할 권한이 없습니다.\n"
        "이용하시려면 관리자에게 문의해 주세요."
    ),
    "no_permission_callback": "이 기능을 사용할 권한이 없습니다",
    # --- Born-locked ownership / claim flow ---
    "claim_success": "이 봇의 소유자가 되셨습니다.",
    "claim_code_log": (
        "CLAIM CODE: {code} -- 소유자가 되려면 텔레그램 계정에서 이 봇에게 "
        "'/claim {code}' 를 보내세요."
    ),
    "owner_lock_missing_log": (
        "owner.lock missing but instance already claimed; reclaim required"
    ),
    # --- Commands ---
    "welcome": (
        "안녕하세요, {name}님! 메시지를 보내 대화를 시작해주세요."
    ),
    "new_session": (
        "새 세션으로 전환했습니다."
    ),
    "model_switched": "전환 완료: {label}",
    "model_select": (
        "Claude 모델을 선택하세요:\n"
        "주의: 모델을 전환하면 새 세션이 시작됩니다."
    ),
    "model_switch_warning": "주의: 모델을 전환하면 새 세션이 시작됩니다.",
    "model_unknown": "알 수 없는 모델 '{name}'. 사용 가능한 모델: {allowed}",
    "model_state_fallback": "저장된 모델 설정을 읽지 못해 기본값으로 시작합니다.",
    "stop_paused": "세션을 중단했습니다.",
    "stop_nothing": "실행 중인 작업이 없습니다.",
    "no_session": "활성 세션이 없습니다. 먼저 대화를 시작해 주세요.",
    "task_terminated": "작업을 종료했습니다.",
    # --- Help ---
    "help_text": (
        "사용 가능한 명령:\n"
        "/start - 시작 / 인사\n"
        "/new - 새 세션 시작\n"
        "/stop - 현재 작업 중단\n"
        "/model - 모델 전환 (세션이 새로 시작됩니다)\n"
        "/resume - 이전 세션 이어가기\n"
        "/history - 최근 기록 보기\n"
        "/skills - 설치된 스킬 목록\n"
        "/usage - Claude 사용량/한도\n"
        "/help - 이 도움말 보기\n\n"
        "임의의 /이름 을 보내면 해당 스킬이 실행됩니다.\n"
        "최초 설정: /claim <code> 로 소유자가 되세요. "
        "PROJECT_ROOT 바깥 파일 접근은 일회성 확인을 요청합니다."
    ),
    # --- Skills listing (read from SKILL.md frontmatter) ---
    "skills_none": "설치된 스킬이 없습니다.",
    "skills_header_project": "프로젝트 스킬",
    "skills_header_global": "전역 스킬",
    # --- BotCommand menu descriptions ---
    "cmd_desc_new": "새 세션 시작",
    "cmd_desc_stop": "실행 중단",
    "cmd_desc_model": "모델 전환 (새 세션)",
    "cmd_desc_resume": "세션 이어가기",
    "cmd_desc_history": "메시지 기록 보기",
    "cmd_desc_skills": "스킬 목록",
    "cmd_desc_usage": "Claude 사용량/한도",
    "cmd_desc_help": "도움말 보기",
    # --- Usage report (/usage -> routines/claude-usage.sh) ---
    "usage_script_missing": "사용량 스크립트를 찾을 수 없습니다 (routines/claude-usage.sh).",
    "usage_timeout": "사용량 조회가 시간 내에 끝나지 않았습니다. 잠시 후 다시 시도해 주세요.",
    "usage_failed": "사용량 조회 실패: {error}",
    # --- Resume (session history) ---
    "no_session_history": "세션 기록을 찾을 수 없습니다.",
    "session_history_header": "세션 기록",
    "resume_hint": "전환할 세션의 번호를 입력해 주세요:",
    "resume_switched": "세션으로 전환했습니다: {msg}",
    "resume_invalid_number": "잘못된 번호입니다. 다시 시도해 주세요.",
    # --- History ---
    "no_history": "이 세션에는 표시할 기록이 없습니다.",
    "history_header": "최근 기록 (최근 5개 메시지)",
    # --- Queue / overflow ---
    "queue_busy": (
        "이전 메시지를 처리하고 있습니다. 잠시 기다리시거나 /stop 으로 중단해 주세요."
    ),
    # --- Slash command usage ---
    "usage_skill": "사용법: /skill <name> [args]",
    "usage_command": "사용법: /command <name> [args]",
    # --- Options keyboard ---
    "select_prompt": "선택해 주세요:",
    "selected": "선택: {choice}",
    # --- External file confirmation ---
    "external_file_prompt": (
        "PROJECT_ROOT 바깥의 파일 경로가 감지되었습니다. 전송하려면 확인이 "
        "필요합니다."
    ),
    "external_file_send": "외부 파일 전송",
    "external_file_cancel": "취소",
    "external_file_cancelled": "외부 파일 전송을 취소했습니다.",
    "external_file_none": "대기 중인 외부 파일이 없습니다.",
    "external_file_confirmed": "확인했습니다. 외부 파일을 전송합니다...",
    # --- Timeout / resume ---
    "timeout_paused": (
        "{timeout}초가 지나 한 번 끊었습니다. 이어서 진행하려면 아래 버튼을 "
        "누르세요."
    ),
    "timeout_no_resume": (
        "타임아웃으로 작업이 멈췄는데, 이어갈 세션을 찾지 못했습니다. 요청을 다시 "
        "보내주세요."
    ),
    "tap_to_continue": "이어서 진행하기",
    "timeout_tap_notice": "타임아웃으로 멈췄습니다. 이어서 진행하려면 누르세요.",
    "resume_expired": (
        "이미 처리됐거나 만료된 버튼입니다. 다시 요청해 주세요."
    ),
    "resume_continuing": "이어서 진행합니다...",
    "still_working": (
        "시간이 좀 걸리고 있습니다. 자동으로 계속 진행 중입니다."
    ),
    "resume_failed": "이어가기 실패: {error}",
    # --- Voice ---
    "voice_too_long": "음성 메시지가 너무 깁니다. 최대 길이는 {seconds}초입니다.",
    "voice_download_failed": "음성 메시지를 받지 못했습니다. 다시 시도해 주세요.",
    "photo_download_failed": "사진을 받지 못했습니다. 다시 보내주세요.",
    "doc_download_failed": "파일을 받지 못했습니다. 다시 보내주세요.",
    "voice_convert_failed": (
        "음성 변환에 실패했습니다. ffmpeg 가 설치되어 있는지 확인한 뒤 다시 "
        "시도해 주세요."
    ),
    "voice_unavailable": (
        "음성 인식이 설정되어 있지 않습니다 (로컬 whisper 를 사용할 수 없습니다). "
        "faster-whisper 를 설치해 주세요."
    ),
    "voice_empty": "음성 메시지에서 말소리를 인식하지 못했습니다. 다시 시도해 주세요.",
    "voice_transcribe_failed": (
        "음성 메시지를 텍스트로 변환하지 못했습니다. 잠시 후 다시 시도해 주세요."
    ),
    # --- Errors ---
    "internal_error": "내부 오류: {error}",
    "processing_failed": "처리 실패: {error}",
    "generic_error": (
        "죄송합니다. 메시지를 처리하는 중 오류가 발생했습니다.\n오류: {error}"
    ),
    "network_timeout": "네트워크 연결이 잠시 불안정했습니다. 잠시 후 다시 시도해 주세요.",
    # --- Outage / failure notices ---
    "outage_recovered": (
        "약 {minutes}분간 오프라인이었다가 텔레그램에 다시 연결되었습니다. "
        "그동안 보내신 내용이 누락되었을 수 있으니 필요하면 다시 보내주세요."
    ),
    "proactive_turn_failed": (
        "백그라운드 작업이 응답 없이 종료되었습니다 (모델 과부하 또는 재시도 후 "
        "API 오류). 전달된 내용이 없으니 다시 요청해 주세요."
    ),
}
