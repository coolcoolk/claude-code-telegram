"""DGN-1256: the vendor doc has two readers; only one of them costs tokens.

`vendors/telegram.md` rode every session's system prompt in full, so the
framework-ownership warning, the overlay how-to and the rationale index --
all addressed to the human editing the file -- were paid for on every turn.
The fix is a receiver split, not a deletion: an invisible marker line ends
the editor preamble and the loader injects only what is below it.

These tests pin the three cases the split has to get right (marker present /
marker absent / overlay), the two failure directions when the marker is there
but the body under it is not, and the observability line that makes the
saving measurable at all.
"""

import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bridge import sdk_bridge

MARKER = sdk_bridge._VENDOR_INJECT_MARKER

EDITOR_HALF = (
    "# telegram.md -- vendor contract\n\n"
    "FRAMEWORK-OWNED: hand edits are REVERTED.\n"
    "Rationale index: DGN-1224 / DGN-1254.\n\n"
)
MODEL_HALF = "# Telegram vendor contract\n\n## Sample fidelity\n\n- rule\n"
MARKED_CONTRACT = EDITOR_HALF + MARKER + "\n" + MODEL_HALF
UNMARKED_CONTRACT = EDITOR_HALF + MODEL_HALF

OVERLAY_EDITOR = "# custom overlay\n\nnotes for whoever edits this\n\n"
OVERLAY_MODEL = "## Local judgment\n\n- instance rule\n"
MARKED_OVERLAY = OVERLAY_EDITOR + MARKER + "\n" + OVERLAY_MODEL


def _vendors(contract=MARKED_CONTRACT, overlay=None):
    d = Path(tempfile.mkdtemp(prefix="dgn1256-vendors-"))
    if contract is not None:
        (d / "telegram.md").write_text(contract, encoding="utf-8")
    if overlay is not None:
        (d / "custom.telegram.md").write_text(overlay, encoding="utf-8")
    return d


class SplitHelperTest(unittest.TestCase):
    def test_marker_present_drops_everything_above_and_the_marker_line(self):
        self.assertEqual(
            sdk_bridge._injectable_vendor_text(MARKED_CONTRACT), MODEL_HALF
        )

    def test_marker_absent_returns_the_text_unchanged(self):
        # Back-compat: a vendor file written before the marker existed (or one
        # shipped by a third party) must inject exactly as it did before.
        self.assertEqual(
            sdk_bridge._injectable_vendor_text(UNMARKED_CONTRACT),
            UNMARKED_CONTRACT,
        )

    def test_only_the_first_marker_ends_the_preamble(self):
        text = f"a\n{MARKER}\nb\n{MARKER}\nc\n"
        self.assertEqual(
            sdk_bridge._injectable_vendor_text(text), f"b\n{MARKER}\nc\n"
        )

    def test_marker_must_be_its_own_line(self):
        # A mention inside prose is not a boundary -- otherwise the paragraph
        # that DOCUMENTS the marker would cut the file in half.
        text = f"the marker is `{MARKER}` and it goes on its own line\n"
        self.assertEqual(sdk_bridge._injectable_vendor_text(text), text)


class CanonicalContractTest(unittest.TestCase):
    def test_marked_contract_injects_only_the_model_half(self):
        with patch.object(sdk_bridge, "_VENDOR_DIR", _vendors()):
            out = sdk_bridge._load_vendor_contract()
        self.assertIn("## Sample fidelity", out)
        self.assertNotIn("FRAMEWORK-OWNED", out)
        self.assertNotIn("Rationale index", out)

    def test_unmarked_contract_injects_in_full(self):
        with patch.object(
            sdk_bridge, "_VENDOR_DIR", _vendors(contract=UNMARKED_CONTRACT)
        ):
            self.assertEqual(
                sdk_bridge._load_vendor_contract(), UNMARKED_CONTRACT
            )

    def test_marker_with_empty_body_fails_closed(self):
        # Same wiring error as an empty file: a contract-less session must
        # never be silent, so it boot-dies rather than degrading.
        with patch.object(
            sdk_bridge,
            "_VENDOR_DIR",
            _vendors(contract=EDITOR_HALF + MARKER + "\n\n   \n"),
        ):
            with self.assertRaises(sdk_bridge.VendorContractMissing) as cm:
                sdk_bridge._load_vendor_contract()
        self.assertIn("marker", str(cm.exception))

    def test_log_bytes_is_the_injected_size_not_the_file_size(self):
        # Without this the shrink is unobservable: the old line printed the
        # on-disk size, which does not move when the editor half stops riding.
        with patch.object(sdk_bridge, "_VENDOR_DIR", _vendors()):
            with self.assertLogs("bridge.sdk_bridge", level="INFO") as cm:
                sdk_bridge._load_vendor_contract()
        line = next(x for x in cm.output if "vendor=telegram" in x)
        got = int(re.search(r"\bbytes=(\d+)", line).group(1))
        file_bytes = int(re.search(r"file_bytes=(\d+)", line).group(1))
        self.assertEqual(got, len(MODEL_HALF.encode("utf-8")))
        self.assertEqual(file_bytes, len(MARKED_CONTRACT.encode("utf-8")))
        self.assertLess(got, file_bytes)


class OverlayTest(unittest.TestCase):
    def test_marked_overlay_injects_only_the_model_half(self):
        with patch.object(
            sdk_bridge, "_VENDOR_DIR", _vendors(overlay=MARKED_OVERLAY)
        ):
            out = sdk_bridge._load_vendor_overlay()
        self.assertEqual(out, OVERLAY_MODEL)
        self.assertNotIn("notes for whoever edits", out)

    def test_unmarked_overlay_injects_in_full(self):
        body = OVERLAY_EDITOR + OVERLAY_MODEL
        with patch.object(sdk_bridge, "_VENDOR_DIR", _vendors(overlay=body)):
            self.assertEqual(sdk_bridge._load_vendor_overlay(), body)

    def test_overlay_marker_with_empty_body_warns_and_fails_open(self):
        # Opposite direction from the canonical contract on purpose: an
        # instance-owned file may never brick the bot (DGN-818 C2).
        with patch.object(
            sdk_bridge,
            "_VENDOR_DIR",
            _vendors(overlay=OVERLAY_EDITOR + MARKER + "\n\n"),
        ):
            with self.assertLogs("bridge.sdk_bridge", level="WARNING") as cm:
                self.assertEqual(sdk_bridge._load_vendor_overlay(), "")
        self.assertIn("marker", "\n".join(cm.output))

    def test_composition_still_canonical_first_overlay_second(self):
        with patch.object(
            sdk_bridge, "_VENDOR_DIR", _vendors(overlay=MARKED_OVERLAY)
        ):
            with patch.object(sdk_bridge, "OUTPUT_LANG_GUARD", False):
                out = sdk_bridge._compose_system_prompt()
        self.assertLess(
            out.index("## Sample fidelity"), out.index("## Local judgment")
        )
        self.assertNotIn("FRAMEWORK-OWNED", out)
        self.assertNotIn("notes for whoever edits", out)




if __name__ == "__main__":
    unittest.main()
