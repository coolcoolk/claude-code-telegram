"""DGN-1021: the [[OPTIONS]] GATES must route through the canonical recognizer.

The concept "is a marker present?" had multiple hand-rolled `OPTIONS_MARKER
in content` substring checks in sdk_bridge next to the line-based strip/render
seats (strip_options_marker). Each independent recognizer drifts the moment a
new marker form is added: downstream (dogany-agent) a labeled marker form was
added, two substring gates never learned it, and buttons died with ZERO
warnings -- the fail-loud lived INSIDE the skipped `if force_options:` block.

This suite locks the upstream fix:
  - all sdk_bridge gates route through options.has_options_marker (the ONE
    canonical line-based recognizer);
  - an AST-level guard keeps substring recognizers from returning;
  - the render seats WARN (fail-loud) when an armable marker arrives with the
    gate off, instead of silently dropping the buttons.

Tests are per delivery PATH (not per recognizer):
  1. model-turn finalize  (_finalize_result -> ChatResponse.has_options)
  2. proactive push       (_flush_proactive -> proactive_push(has_options))
  3. classifier           (_maybe_mark_options marker-present suppression)
"""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock

from bridge.sdk_bridge import SdkBridge, _PendingRequest, _UserStreamState
from claude_agent_sdk import ResultMessage


BARE_NUMBERED_BODY = "Pick one:\n1. proceed\n2. hold\n[[OPTIONS]]"

NUMBERED_ONLY_BODY = "Pick one:\n1. proceed\n2. hold"

MARKER_ONLY_BODY = "Done. Waiting for direction.\n[[OPTIONS]]"

MIDLINE_MENTION_BODY = "About the [[OPTIONS]] marker syntax.\n1. one\n2. two"

PLAIN_BODY = "A plain status report with no marker and no list."


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------


def _load_bot():
    import bridge.bot as bot_mod
    return bot_mod


def _make_chat_bot(bot_mod, sent):
    bot = bot_mod.TelegramBot.__new__(bot_mod.TelegramBot)
    bot.application = MagicMock()

    async def _send_message(chat_id, text, *args, reply_markup=None, **kwargs):
        sent.append({"text": text, "reply_markup": reply_markup})

    bot.application.bot = MagicMock()
    bot.application.bot.send_message = AsyncMock(side_effect=_send_message)
    bot.application.bot.delete_message = AsyncMock()
    return bot


def _run(coro):
    return asyncio.run(coro)


def _make_state() -> _UserStreamState:
    client = MagicMock()
    client.query = AsyncMock()
    st = _UserStreamState(client=client, model=None)
    st.last_chat_id = 42
    st.proactive_push = AsyncMock()
    st.last_session_id = "sess-dgn1021"
    return st


def _make_req(synthetic=None) -> _PendingRequest:
    loop = asyncio.new_event_loop()
    fut = loop.create_future()
    loop.close()
    req = _PendingRequest(
        user_id=42,
        chat_id=42,
        model=None,
        requested_session_id=None,
        permission_callback=None,
        typing_callback=None,
        future=fut,
        user_message="please decide",
    )
    if synthetic is not None:
        req.synthetic_response = synthetic
    return req


def _make_result_msg() -> ResultMessage:
    return ResultMessage(
        subtype="success",
        duration_ms=50,
        duration_api_ms=40,
        is_error=False,
        num_turns=1,
        session_id="sess-dgn1021",
        result=None,
    )


def _finalize(content: str, monkeypatch, synthetic=None, classifier=False):
    """Run the REAL model-turn finalize path and return its ChatResponse.

    classify_is_choice is patched (no Haiku CLI in tests); its return value
    drives the classifier-injection axis for numbered-only content.
    """
    import bridge.sdk_bridge as sdk_mod

    monkeypatch.setattr(
        sdk_mod, "classify_is_choice", lambda *a, **k: classifier
    )
    bridge = SdkBridge()
    state = _make_state()
    req = _make_req(synthetic=synthetic)
    req.last_assistant_texts = [content] if content is not None else []
    _run(bridge._finalize_result(req.user_id, state, req, _make_result_msg()))
    assert req.future.done(), "finalize must resolve the future"
    return req.future.result()


def _keyboard_sends(sent):
    return [e for e in sent if e["reply_markup"] is not None]


# ---------------------------------------------------------------------------
# Path 1: model-turn finalize (sdk_bridge._finalize_result has_options gate)
# ---------------------------------------------------------------------------


class TestFinalizePathGate:
    def test_bare_marker_numbered_run_gate_true_keyboard(self, monkeypatch):
        """A marker + numbered run turn must open the gate AND, fed into the
        real render seat exactly as bot.py does
        (force_options=response.has_options), attach an actual keyboard."""
        resp = _finalize(BARE_NUMBERED_BODY, monkeypatch)
        assert resp.has_options is True

        bot_mod = _load_bot()
        sent = []
        bot = _make_chat_bot(bot_mod, sent)
        _run(bot._send_smart(42, resp.content, force_options=resp.has_options))
        kb = _keyboard_sends(sent)
        assert len(kb) == 1, f"no keyboard attached: {sent}"
        rows = kb[0]["reply_markup"].inline_keyboard
        assert [r[0].text for r in rows] == ["1. proceed", "2. hold"]

    def test_numbered_only_gate_true_source_preserved(self, monkeypatch):
        """No-regression: a numbered run WITHOUT any marker must still open
        the gate -- the `has_numbered_list` arm carries the
        classifier-injection path and must survive the recognizer swap."""
        resp = _finalize(NUMBERED_ONLY_BODY, monkeypatch, classifier=False)
        assert resp.has_options is True

    def test_numbered_only_classifier_injects_keyboard(self, monkeypatch):
        """Classifier end-to-end: Haiku says pick-one -> marker injected ->
        keyboard renders."""
        resp = _finalize(NUMBERED_ONLY_BODY, monkeypatch, classifier=True)
        assert resp.has_options is True

        bot_mod = _load_bot()
        sent = []
        bot = _make_chat_bot(bot_mod, sent)
        _run(bot._send_smart(42, resp.content, force_options=resp.has_options))
        assert len(_keyboard_sends(sent)) == 1

    def test_plain_body_gate_false(self, monkeypatch):
        """No-regression: marker-less, list-less turns keep the gate closed."""
        resp = _finalize(PLAIN_BODY, monkeypatch)
        assert resp.has_options is False

    def test_synthetic_response_gate_true(self, monkeypatch):
        """No-regression: synthetic responses always force options."""
        resp = _finalize(None, monkeypatch, synthetic="Pick:\n1. a\n2. b\n[[OPTIONS]]")
        assert resp.has_options is True


# ---------------------------------------------------------------------------
# Path 2: proactive push (sdk_bridge._flush_proactive has_options gate)
# ---------------------------------------------------------------------------


def _flush_proactive(content: str, monkeypatch, classifier=False):
    """Run the REAL proactive flush wired to the REAL render seat, mirroring
    bot._proactive_push (which forwards has_options as force_options into
    _send_smart). Returns (sent, push_calls)."""
    import bridge.sdk_bridge as sdk_mod

    monkeypatch.setattr(
        sdk_mod, "classify_is_choice", lambda *a, **k: classifier
    )
    bot_mod = _load_bot()
    sent = []
    bot = _make_chat_bot(bot_mod, sent)
    push_calls = []

    async def _push(chat_id, text, has_options):
        push_calls.append({"has_options": has_options})
        await bot._send_smart(chat_id, text, force_options=has_options)

    bridge = SdkBridge()
    state = _make_state()
    state.proactive_push = _push
    state.proactive_texts = [content]
    _run(bridge._flush_proactive(42, state))
    return sent, push_calls


class TestProactivePathGate:
    def test_bare_marker_numbered_proactive_keyboard(self, monkeypatch):
        """A proactive push carrying a marker + numbered run must arrive with
        buttons, through the canonical recognizer."""
        sent, calls = _flush_proactive(BARE_NUMBERED_BODY, monkeypatch)
        assert calls and calls[0]["has_options"] is True
        kb = _keyboard_sends(sent)
        assert len(kb) == 1, f"no keyboard attached: {sent}"
        rows = kb[0]["reply_markup"].inline_keyboard
        assert [r[0].text for r in rows] == ["1. proceed", "2. hold"]

    def test_numbered_only_proactive_gate_true(self, monkeypatch):
        """No-regression: numbered run without a marker must keep the
        proactive gate open (classifier may still decline injection)."""
        sent, calls = _flush_proactive(NUMBERED_ONLY_BODY, monkeypatch,
                                       classifier=False)
        assert calls and calls[0]["has_options"] is True

    def test_midline_mention_only_gate_false(self, monkeypatch):
        """DGN-1021 intent lock: a MID-LINE prose mention of "[[OPTIONS]]"
        with no numbered run is not an armable marker -- it never builds
        buttons, never strips -- so it must not open the gate. Under the old
        substring check it incidentally did (gate open, zero buttons)."""
        sent, calls = _flush_proactive(
            "Note: the [[OPTIONS]] marker arms buttons.", monkeypatch
        )
        assert calls and calls[0]["has_options"] is False
        assert not _keyboard_sends(sent)

    def test_plain_proactive_gate_false_no_keyboard(self, monkeypatch):
        sent, calls = _flush_proactive(PLAIN_BODY, monkeypatch)
        assert calls and calls[0]["has_options"] is False
        assert not _keyboard_sends(sent)


# ---------------------------------------------------------------------------
# Path 3: classifier suppression (sdk_bridge._maybe_mark_options)
# ---------------------------------------------------------------------------


class TestClassifierPathGate:
    def _mark(self, content, monkeypatch, classifier=True):
        import bridge.sdk_bridge as sdk_mod

        monkeypatch.setattr(
            sdk_mod, "classify_is_choice", lambda *a, **k: classifier
        )
        return _run(SdkBridge._maybe_mark_options("prev", content))

    def test_bare_marker_suppresses_injection(self, monkeypatch):
        content = "1. one\n2. two\n[[OPTIONS]]"
        out = self._mark(content, monkeypatch)
        assert out == content

    def test_numbered_only_injects_when_choice(self, monkeypatch):
        out = self._mark(NUMBERED_ONLY_BODY, monkeypatch)
        assert out.endswith("[[OPTIONS]]")

    def test_fenced_marker_example_still_suppresses(self, monkeypatch):
        """A standalone marker line inside a code fence still counts as
        marker-present for the classifier (the canonical recognizer is
        line-based, fence-unaware) -- unchanged from the substring era."""
        content = "Example:\n```\n[[OPTIONS]]\n```\n1. one\n2. two"
        out = self._mark(content, monkeypatch)
        assert out == content

    def test_inline_mention_no_longer_suppresses(self, monkeypatch):
        """DGN-1021 intent lock: a MID-LINE prose mention of "[[OPTIONS]]"
        is not an armable marker (it never builds buttons, never strips) --
        it must not suppress classifier injection over a genuine pick-one
        run. Under the old substring check it incidentally did."""
        out = self._mark(MIDLINE_MENTION_BODY, monkeypatch)
        assert out.endswith("[[OPTIONS]]")


# ---------------------------------------------------------------------------
# Recognizer unification: no hand-rolled substring gate may return
# ---------------------------------------------------------------------------


class TestRecognizerUnification:
    def test_no_substring_marker_recognizer_in_sdk_bridge(self):
        """The concept "is a marker present?" has ONE implementation
        (options.has_options_marker). `OPTIONS_MARKER in content` /
        `OPTIONS_MARKER not in content` substring recognizers are what let a
        new marker form silently miss gates downstream -- they must never
        come back."""
        import inspect
        import re
        import bridge.sdk_bridge as sdk_mod

        src = inspect.getsource(sdk_mod)
        offenders = [
            ln.strip() for ln in src.splitlines()
            if re.search(r"OPTIONS_MARKER\s+(not\s+)?in\s", ln)
            and not ln.lstrip().startswith("#")
        ]
        assert offenders == [], (
            f"hand-rolled substring marker recognizers found: {offenders}"
        )


# ---------------------------------------------------------------------------
# Fail-loud: gate-off + marker present must WARN (DGN-1021)
# ---------------------------------------------------------------------------


class TestGateMismatchFailLoud:
    def test_send_smart_marker_gate_off_warns(self, caplog):
        """An armable marker line reaching _send_smart with the gate off must
        WARN (recognizer drift telemetry), body delivered intact."""
        bot_mod = _load_bot()
        sent = []
        bot = _make_chat_bot(bot_mod, sent)

        with caplog.at_level(logging.WARNING, logger="bridge.bot"):
            _run(bot._send_smart(42, MARKER_ONLY_BODY, force_options=False))

        assert any(
            "options gate" in rec.message for rec in caplog.records
        ), f"no gate-mismatch warning: {[r.message for r in caplog.records]}"
        assert not _keyboard_sends(sent)

    def test_send_content_artifacts_marker_gate_off_warns(self, caplog):
        """Same tripwire on the reply-path artifact seat."""
        bot_mod = _load_bot()
        sent = []
        bot = _make_chat_bot(bot_mod, sent)
        message = MagicMock()
        message.chat.id = 42
        message.reply_text = AsyncMock()

        with caplog.at_level(logging.WARNING, logger="bridge.bot"):
            _run(bot._send_content_artifacts(
                message, MARKER_ONLY_BODY, force_options=False
            ))

        assert any(
            "options gate" in rec.message for rec in caplog.records
        )
        message.reply_text.assert_not_awaited()

    def test_plain_body_gate_off_no_warning(self, caplog):
        """Normal marker-less messages must stay silent -- the tripwire may
        not spam every ordinary send."""
        bot_mod = _load_bot()
        sent = []
        bot = _make_chat_bot(bot_mod, sent)

        with caplog.at_level(logging.WARNING, logger="bridge.bot"):
            _run(bot._send_smart(42, PLAIN_BODY, force_options=False))

        assert not any(
            "options gate" in rec.message for rec in caplog.records
        )
