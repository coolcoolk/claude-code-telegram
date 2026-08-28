# Changelog

All notable changes to this project are documented here.

This project follows [Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-08-28

First versioned release since the initial publication. `__version__` had stayed at
`1.0.0` through 58 commits of fixes and additions; this release stamps the actual
state and starts a real version line.

Grouped by what changed for a user of the bridge.

### Message rendering

- Tag-safe HTML split and balancing, with tag-stripped plain-text fallbacks, so a
  long formatted reply can no longer be cut mid-tag into broken markup.
- Markdown sanitize backstop: headers stripped, tables wrapped, stray labels removed
  before send.
- Prose and fenced code are sent as separate messages instead of one mixed bubble.

### Interactive buttons

- Option labels keep their body text when a separator starts the label (previously
  the button could degrade to a bare number with the text lost).
- Button output redesign: separator handling, hard cap on label width, body text
  preserved on overflow.

### Long-running turns

- Countdown done-marker: a completed long turn is now marked complete explicitly
  rather than inferred.
- Interim streaming default raised from suppress to fold.

### Reliability

- Session-inbox UTF-8 quarantine: a malformed byte sequence in the session inbox is
  isolated instead of poisoning the whole read path (2026-08-23 incident).
- `/kill` command removed. It overlapped with the normal interrupt path and its
  failure mode was worse than the problem it solved.

### Privacy

- Owner device identifiers scrubbed from comments that ship publicly.

### Tests

- Dashboard test coverage carried over from the vendored instance (pre-existing gap).

## [1.0.0] - initial publication

Run Claude Code as a Telegram bot.
