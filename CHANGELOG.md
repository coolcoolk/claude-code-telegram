# Changelog

All notable changes to this project are documented here.

This project follows [Semantic Versioning](https://semver.org/).

## [2.1.0] - 2026-10-06

Minor release: everything the bridge gained since 2.0.2, generated from the
canonical source for the first time (this tree is now produced, not hand-edited).

### Buttons and choices
- Option buttons sit under the message they belong to; a tap appends the chosen
  label to that message instead of sending a separate prompt. A single button
  carries no number.
- Tapping an expired button explains how long buttons last and asks you to type
  the request in the chat.
- Tapping the same option twice is ignored quietly instead of showing a
  processing error.

### Answers you might have missed
- An answer written in the middle of a long task is delivered as its own message
  instead of disappearing into the folded progress log.
- An answer held back by a blocking stop check is no longer delivered twice.
- Short working notes in another language than yours are kept off your chat.

### Stopping and timeouts
- `/stop` answers in one sentence; when work is stopped for you (interrupt or
  time limit), the stopped background jobs are listed by name.
- Every path that runs a turn -- messages, commands, button taps, retries --
  tries to resume after a timeout.
- A request is never left hanging when a turn closes.

### Models and login
- `/model` shows the model that is answering, with its real version; a restart
  notice names the model when it changed.
- The machine's Claude CLI is used when no explicit path is configured.
- When the Claude login expires, the bot says how to log in again instead of
  passing on the raw CLI error.

### Smaller fixes
- An @mention followed directly by non-ASCII text stays tappable.
- A first-run install with no allowed users configured no longer crashes at boot.

## [2.0.2] - 2026-09-14

### The agent no longer leaks its own next turn into your chat

Sometimes a reply arrived with an extra tail glued onto the end of it -- a
fragment the agent had written for the *next* turn, not for you: a role label
with text run directly onto it, mid-sentence, after the real answer had already
finished. You never asked for it and it was never meant to be sent.

- The outbound sanitizer now detects that shape and cuts it before the message
  leaves. The real answer is untouched; only the glued-on tail goes.
- Detection is conservative by design. It fires on the specific shape that was
  actually measured leaking, and a grammatical-particle check keeps it off
  ordinary text that merely resembles it -- dropping a word of your content is
  worse than leaving a stray fragment, so the cut is narrow on purpose.
- Known limit: the anchor needs the label and the text to be run together with
  no space between them. A leak that lands with a space after the label does
  not match this rule yet.
- When a strip happens, it is logged (with the label and how many characters
  were removed) so the behaviour is auditable rather than silent.

Nothing else changed in this release.

## [2.0.1] - 2026-09-09

### `/usage` is back

2.0.0 removed `/usage`. That was a mistake on our side, not a product decision:
the command works, and the reporting script it needs (`routines/claude-usage.sh`)
was in the box the whole time -- it just was not wired up when the bridge started
being generated instead of hand-copied. It is wired up again.

- **`/usage`** -- your current Claude rate-limit windows (5-hour, weekly, and the
  per-model weekly cap) with the reset time for each, read live from your own
  Claude Code login. It is back in the command menu and in `/help`.
- The script it runs is `routines/claude-usage.sh`, already in this repo. It is
  also usable on its own: `routines/claude-usage.sh` for the short report,
  `--full` to add the local stats cache summary, `--json` for the raw response.
- Credentials are read from whichever store your Claude CLI actually uses --
  `~/.claude/.credentials.json`, the macOS Keychain, or libsecret on Linux -- and
  are sent to Anthropic only, in the request header. Nothing is written anywhere
  and no token is ever printed, including in the failure messages.
- If you are not logged in, `/usage` now says which store it checked and what to
  do about it, instead of failing blankly.

Nothing else changed in this release. `/history` is still gone -- the chat itself
is the transcript.

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
