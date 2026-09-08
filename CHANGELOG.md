# Changelog

All notable changes to this project are documented here.

This project follows [Semantic Versioning](https://semver.org/).

## [2.0.0] - 2026-09-09

The bridge is no longer maintained by hand-copying fixes from a private tree
into this one. This release is the first one GENERATED from that tree, so it
lands in one step everything that had accumulated on the other side of that
manual copy. Everything below is a change you can feel while chatting; the major
version marks the size of the jump and the removed commands, not a rewrite.

### Breaking changes

- **`/history` and `/usage` are gone.** `/history` is removed outright; the chat
  itself is the transcript. `/usage` depended on a reporting script that was never
  bundled here, so on a plain clone it only ever answered "script not found". The
  example script that fed it is still in `routines/` and now has no caller.
- **A message sent while a turn is running now interrupts that turn.** Previously
  it queued and ran afterwards. The bridge pauses what it is doing, folds your new
  message into the running work, and tells you it did ("Paused what I was doing to
  handle your new message."). Use the new `/queue <message>` when you want the old
  behaviour -- append without interrupting.
- **`python-telegram-bot >= 20.8`** (was `>= 20.7`), needed for link-preview
  suppression. Re-run the install line in the quick start after updating.

**No manual migration.** Service and timer names are unchanged, and on Linux
`watchdog_setup.sh` now adopts whichever unit naming is already registered on
the host before falling back to the published default, so an in-place update
cannot orphan your timer. Override with `DOGANY_BRIDGE_UNIT` /
`DOGANY_WATCHDOG_UNIT` if you renamed them yourself.

### New commands

- `/btw <question>` -- ask something on the side. It forks the current session,
  answers in an isolated 💭 bubble, and never writes to your main history.
  Replying to that bubble continues the fork.
- `/queue <message>` -- append a message to the running turn instead of
  interrupting it (the pre-2.0 default).
- `/restart` -- restart the bridge from chat: graceful drain, relaunch, and a
  completion ping when it is back.

### Long-running turns

- Progress folding: interim output is collapsed into one labelled log block
  instead of scrolling the chat, with separate captions for a normal finish, a
  stop, and a timeout.
- A turn that ends early now says so ("That reply may be incomplete...") instead
  of silently returning a short answer.
- A turn cut off by a time limit gets an explicit continuation prompt on resume,
  so the model finishes the remaining work rather than starting over.
- Countdown messages end with a "Continue" button instead of just stopping.

### Errors and retries

- Failures are classified instead of all reading "network error": transient
  failure, authentication, and generic errors each get their own message, and
  transient ones come with a **Retry** button.
- Authentication failures tell you to re-login with the Claude CLI rather than
  leaving the bot silently dead.
- Background subagents killed with the turn are reported instead of vanishing.

### Images and files

- Images too large for Telegram's photo limits are downscaled and still arrive as
  photos (with Pillow installed), or are delivered as documents with the original
  pixels when no aspect-preserving downscale is legal.
- When a send does fail, the message states the real reason -- dimensions, file
  size, or API -- instead of blaming the network.
- Photo and document uploads get a clearer prompt, including the album case, and
  your caption is passed through as part of the request.

### Safety and access

- Access to paths outside your working folder asks for a one-time confirmation in
  chat, and the approval expires so a stale grant cannot authorize a much later
  call.
- On delivery paths with no live turn to confirm through, an external file is
  withheld with an explicit notice instead of being sent unchecked.
- Internal machine-formatted lines that reach your screen unregistered now raise
  a one-per-day notice instead of appearing as unexplained noise.

### Sessions and models

- The model a session actually used is remembered, so a new session starts where
  you left off instead of snapping back to a static default.
- Switching to the model already in use says so rather than silently restarting
  the session.
- An output-language instruction is attached to the turn, so long tool-using
  turns answer in your configured language instead of drifting back to English.

### Optional: fast-path handler

- A new opt-in `FASTPATH_HANDLER` lets you point the bridge at your own
  executable. Short numeric-looking messages are offered to it before a model
  turn starts; if it handles one, its output is posted and no model turn runs.
  Default off -- with the key unset the bridge behaves exactly as before. See
  `bridge/.env.example` for the contract.

### Retired

- `/authsync` still answers, but only to say it is retired: its file-to-keychain
  sync was itself what kept revoking credentials, and the CLI refreshes them on
  its own. The reply points you at `claude auth login`.

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
