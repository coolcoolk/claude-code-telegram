"""DGN-1843: a complete plan with blocked items is a plan, not a lookup
failure.

The planner exits 2 both for "an item is blocked, the rest was planned"
and for "aborted, no plan"; only the former ends its emit with PLAN-END.
Measured 2026-10-04: one instance's pack receipt read EVIDENCE-MISMATCH and
every agent's session-start notice said the update list could not be
loaded.  Here the planner is a stub that writes exactly those two emits.
"""

