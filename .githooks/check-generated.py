#!/usr/bin/env python3
"""check-generated.py -- refuse a tree this repo's generator did not produce.

This repository is a BUILD OUTPUT. `bridge/` is generated from the Dogany
source and every other tracked file is staged there and copied in by the same
release step. A fix made directly here never reaches the source, so the next
release silently reverts it -- which is how a fix once lived only in this repo
for weeks.

Each release commit carries `.generated-manifest`: one line per tracked file,
"<git blob id>  <path>", written by the release step from the tree it
committed. This check recomputes that list for a commit and fails on any
added, removed, or changed file. It runs in CI on every push and pull request,
and as the clone's pre-push hook (.githooks/pre-push).

Want to change something here? Change it at the source; the next release
carries it.

Usage:
  check-generated.py [--rev REV]      verify REV (default HEAD)
  check-generated.py --write [--rev REV]
                                      (release step only) write the manifest
                                      for REV to the working tree

Exit: 0 tree matches its manifest, 1 it does not, 2 unrunnable.
"""
import subprocess
import sys

MANIFEST = ".generated-manifest"


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def tree_of(rev):
    out = {}
    for rec in git("ls-tree", "-r", "-z", "--full-tree", rev).split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        _mode, kind, oid = meta.split(b" ")
        path = path.decode("utf-8", "surrogateescape")
        if kind != b"blob" or path == MANIFEST:
            continue
        out[path] = oid.decode()
    return out


def render(tree):
    return "".join("%s  %s\n" % (tree[p], p) for p in sorted(tree))


def parse(text):
    out = {}
    for line in text.splitlines():
        if line.strip():
            oid, path = line.split("  ", 1)
            out[path] = oid
    return out


def main(argv):
    rev, write = "HEAD", False
    it = iter(argv)
    for a in it:
        if a == "--write":
            write = True
        elif a == "--rev":
            rev = next(it, "")
        else:
            print(__doc__, file=sys.stderr)
            return 2
    try:
        git("rev-parse", "--verify", "-q", rev + "^{commit}")
    except subprocess.CalledProcessError:
        print("check-generated: '%s' is not a commit" % rev, file=sys.stderr)
        return 2
    tree = tree_of(rev)
    if write:
        with open(MANIFEST, "w", encoding="utf-8") as fh:
            fh.write(render(tree))
        print("check-generated: wrote %s (%d files)" % (MANIFEST, len(tree)))
        return 0
    try:
        recorded = parse(git("show", "%s:%s" % (rev, MANIFEST)).decode("utf-8", "surrogateescape"))
    except subprocess.CalledProcessError:
        print("check-generated: FAIL -- %s has no %s; this tree was not produced"
              " by the release generator" % (rev, MANIFEST))
        return 1
    added = sorted(set(tree) - set(recorded))
    removed = sorted(set(recorded) - set(tree))
    changed = sorted(p for p in set(tree) & set(recorded) if tree[p] != recorded[p])
    if not (added or removed or changed):
        print("check-generated: OK -- %d files match %s" % (len(tree), MANIFEST))
        return 0
    print("check-generated: FAIL -- this commit edits files the generator owns:")
    for label, paths in (("added", added), ("removed", removed), ("changed", changed)):
        for p in paths:
            print("  %-8s %s" % (label, p))
    print("This repository is generated. Make the change at the source; the next"
          " release carries it here.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
