# DGN-1385 -- measurement (canonical bridge/bot.py, bridge/sdk_bridge.py)

Ticket line numbers are from the vendored (metal-workspace) copy of `bridge/`,
which has drifted from this canonical repo. All references below are
re-found in canonical and cited as `file:line` at the state of this repo
before the fix (commit `09c2054`).

## Question: does typing stop during an in-flight turn's tail, when a new message arrives?

**Yes -- confirmed, two independent gaps, both real, different windows.**

### Gap 1 (the one this ticket fixes): the buffer-append path sends no typing at all

`bridge/bot.py:1469-1489` (`_enqueue_text_task`, in-flight branch): when a
turn is already running for `user_id`, an arriving REGULAR message is
appended to `_debounce_texts` (default, DGN-911) or `_user_pending_texts`
(`/queue`, coalesce=True) and the coroutine returns. Neither branch calls
`send_action` / `chat.send_action` anywhere in this block (grep for
`send_action` in the file before the fix: it appears only at
`bot.py:2935`, `3552` inside slash-command / idle-dispatch code paths, never
in `_enqueue_text_task`). So the moment a message lands in the buffer --
which is exactly the "접수" (receipt) event the owner cannot see -- zero
feedback is emitted. This matches the ticket's own grep note verbatim.

The buffered message is not lost (`_drain_pending_texts`, `bot.py:1764`,
pops both buffers on every turn completion path -- confirmed by the existing
regression suite `tests/test_dgn911_inflight_debounce.py`), but nothing marks
its arrival, so the wait (bounded by `BRIDGE_INFLIGHT_DEBOUNCE_S`, default
5s from `bridge/config.py:534-535`, but effectively "however long the
current turn plus any deferred-interrupt window take" -- up to
`BRIDGE_INFLIGHT_DEFER_CAP_S` = 300s, `bridge/config.py:560-561`) is
indistinguishable from a dropped message.

### Gap 2 [추정, secondary, not this ticket's scope but relevant to "does the CURRENT turn's own typing already cover the tail"]

The currently-running turn already has its own typing refresh, independent
of buffering: `bridge/sdk_bridge.py:1330-1350` (`_typing_keepalive_loop`)
re-sends `typing_callback()` every `TYPING_INTERVAL` = 4s
(`sdk_bridge.py:196`) as long as `state.pending` is non-empty, and
`sdk_bridge.py:1503-1530` (`_reader_loop`) additionally refreshes on every
inbound SDK message. Both gates are keyed on `state.pending` being
non-empty for that user's stream.

`state.pending.popleft()` fires at `sdk_bridge.py:1665`, **after**
`_finalize_result` (line 1662) has already resolved the request's response
-- i.e. `state.pending` goes empty (typing keepalive now silent) at the
instant the SDK-side turn is logically done, but **before** control returns
to `bot.py`'s caller to format and actually `reply_text`/`send_message` the
answer to Telegram. If that formatting/send tail (`_reply_smart`, options
classifier, session-id save, HTML balancing/splitting) takes longer than the
~1s of residual Telegram typing-status life left over from the last 4s-cadence
refresh, typing visibly goes dark for that tail window -- this is plausibly
the "말하고 딱 끝내서 브릿지에 날아갈때" moment the owner described, layered
on top of Gap 1. **[추정]**: this repo has no timing instrumentation on that
tail, so the exact duration is not measured here; only the code-level gate
(`state.pending` empty -> keepalive silent) is confirmed by reading, not
timed. This gap is orthogonal to the buffer-append gap: it affects the
CURRENT turn's own trailing typing, not the buffered-message receipt signal.
This ticket's fix (Gap 1) does not touch Gap 2 and does not need to -- a
message arriving in that exact sub-second window now gets its own explicit
`send_action` on buffer-append regardless of whether the outgoing turn's own
indicator has already gone dark.

## Conclusion feeding the fix

Gap 1 is real, root-caused, and precisely where the ticket's "수리 방향"
points (`_enqueue_text_task`'s two buffer branches). The fix adds an
immediate `send_action("typing")` on every successful buffer-append, plus a
per-user refresh loop (4s cadence, reusing `sdk_bridge.TYPING_INTERVAL`) that
keeps the indicator alive for as long as the message sits buffered,
cancelled the instant the buffer drains (turn ends, /stop discards it, or --
implicitly, no new task is ever started -- the coalesce-cap notice fires
instead of an append).
