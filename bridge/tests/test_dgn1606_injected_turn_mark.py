"""DGN-1606: every machine-injected turn opens with the harness mark.

Measured incident (2026-09-20, dogany-health): a session-inbox injection
reached the SDK through the same client.query() as a real owner message and
was indistinguishable in the transcript (plain user entry, isMeta unset).
The onboarding machinery then ran to completion in that ownerless turn and
the agent named itself.  The mark is the machine signal downstream turn
classifiers (the host's onboarding hooks) key on.

Locks:
  * inject_background_turn prepends INJECTED_TURN_MARK as its own first
    line, preserving the spool text verbatim after it.
  * quiet flag behavior is untouched by the mark.
  * the literal is in LOCKSTEP with the host's onboarding Stop gate reader
    (its INJECTED_TURN_MARK) -- the reader and the writer must agree.
"""

import asyncio
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from bridge.sdk_bridge import INJECTED_TURN_MARK, SdkBridge, _UserStreamState



def _make_state(**kw):
    client = MagicMock()
    client.query = AsyncMock()
    st = _UserStreamState(client=client, model=None)
    st.last_chat_id = kw.get("chat_id", 111)
    st.proactive_push = kw.get("push", AsyncMock())
    st.last_session_id = kw.get("session_id", "sess-1")
    return st


class TestInjectedTurnMark(unittest.TestCase):
    def setUp(self):
        self.bridge = SdkBridge()

    def test_injected_turn_opens_with_the_mark(self):
        st = _make_state()
        self.bridge._streams[1] = st
        ok = asyncio.run(
            self.bridge.inject_background_turn(1, "[outbound-record] note")
        )
        self.assertTrue(ok)
        st.client.query.assert_awaited_once()
        sent = st.client.query.call_args[0][0]
        self.assertEqual(
            sent, INJECTED_TURN_MARK + "\n[outbound-record] note"
        )

    def test_quiet_flag_untouched_by_the_mark(self):
        st = _make_state()
        self.bridge._streams[1] = st
        ok = asyncio.run(
            self.bridge.inject_background_turn(1, "note", quiet=True)
        )
        self.assertTrue(ok)
        self.assertEqual(st.injected_turn_mode, "quiet")
        sent = st.client.query.call_args[0][0]
        self.assertTrue(sent.startswith(INJECTED_TURN_MARK + "\n"))



if __name__ == "__main__":
    unittest.main()
