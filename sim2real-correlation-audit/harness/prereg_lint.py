#!/usr/bin/env python3
"""Check that every preregistered requirement is claimed as implemented, and verified at runtime.

WHY THIS EXISTS
---------------
This project silently dropped its own preregistered requirements three times in one session:

  1. PREREG.md §4b said the hard-pair gate "must NOT be used to justify a decision" while
     analyze.py made it NECESSARY for a GO. Document and code said opposite things.
  2. PREREG.md §7's interpretation rule was described as re-arming "automatically"; nothing
     armed it, so a twin failing every hard pair could still return GO.
  3. PREREG-noise-floor §3 mandated a comparison arm and 15/16 robustness rows. The script
     implemented neither and reported an EMPTY halt list -- a clean bill of health for a run
     that skipped two mandated arms.

All three have one shape: prose written, code written, never diffed.

DESIGN NOTE -- why this is not a prose parser
---------------------------------------------
The first version of this tool scraped requirement-shaped sentences from the prereg and looked for
matching identifiers in the code. Run retrospectively against the script that ACTUALLY dropped two
requirements, it reported "ok" -- a false negative on the exact failure it existed to catch. The
reason is fundamental: "Both are run" contains no distinctive token, so any heuristic loose enough
to flag it also flags everything else.

So the prereg must carry an explicit machine-readable register, and the code must explicitly claim
each ID. That converts a silent omission into a loud one, which is the only property that matters.

USAGE
-----
In the prereg, add a REQUIREMENTS block:

    <!-- REQUIREMENTS
    R1: comparison arm -- both datasets are analysed
    R2: toy 15/16/17 robustness rows
    R3: reproduction gate halts if r deviates > 0.001
    -->

In the code, claim each one where it is implemented:

    # IMPLEMENTS R1
    def comparison_arm(...): ...

Then:

    python harness/prereg_lint.py --prereg <prereg.md> --code <script.py> [--results <out.json>]

If --results is given, each requirement ID must also appear somewhere in the results file, so a
requirement that is coded but silently skipped at runtime is caught too. That is failure mode 3.

This is a lint, not a proof: it verifies a requirement is claimed and exercised, never that it is
implemented correctly. Human review is still required.
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

BLOCK = re.compile(r"<!--\s*REQUIREMENTS(.*?)-->", re.S | re.I)
ENTRY = re.compile(r"^\s*(R\d+)\s*:\s*(.+?)\s*$", re.M)
CLAIM = re.compile(r"IMPLEMENTS\s+(R\d+)", re.I)

# A markdown table row pinning a repo path to a SHA-256, e.g.
#   | `harness/analyze.py` | `c34ebf5b...` | collect + metrics |
# Deliberately permissive: any table row containing a path-ish cell and a 64-hex cell, in either
# order, backticked or not, any extension. A narrow regex that silently skips rows would reproduce
# this tool's own failure mode -- silence reading as a pass.
HASHROW = re.compile(
    r"^\s*\|\s*`?([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)`?[^|]*\|\s*`?(?:sha256:)?([0-9a-fA-F]{64})`?\s*(?:\||$)",
    re.M)
# A table row that pins a path but whose hash cell is malformed (wrong length, non-hex) -- these
# must be reported, not skipped, or a typo'd lock silently stops being checked.
HASHROW_LOOSE = re.compile(r"^\s*\|\s*`?([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)`?\s*\|", re.M)

EMPTY_SHA = hashlib.sha256(b"").hexdigest()


def check_hashes(prereg_text, prereg_path, repo_root):
    """Verify every `path` | `sha256` row in the prereg against the file on disk.

    This is the class of claim that actually broke in this repo: PREREG-noise-floor.md locked
    measure_noise_floor.py at a hash that stopped matching when a later commit added comments,
    and separately locked a path that no longer exists at a hash matching nothing in history.
    Requirement-tracking alone would not have caught either.
    """
    rows = [(p, h.lower()) for p, h in HASHROW.findall(prereg_text)]
    # Rows that look like locks but whose hash did not parse: report loudly rather than skip.
    pinned = {p for p, _ in rows}
    suspect = [p for p in HASHROW_LOOSE.findall(prereg_text)
               if p not in pinned and "/" in p]
    if not rows:
        if suspect:
            print("hash locks:")
            print(f"  [FAIL]     no parsable `path | sha256` rows, but {len(suspect)} row(s) look "
                  f"like locks: {', '.join(suspect[:5])}")
            print( "             A lock table that stops parsing is silently unchecked.")
            print()
            return 0, 1
        return 0, 0
    print("hash locks:")
    bad = 0
    for rel, claimed in rows:
        p = (repo_root / rel)
        if not p.exists():
            print(f"  [MISSING]  {rel}")
            print(f"             locked at {claimed[:12]}... but the file does not exist.")
            print(f"             An unverifiable lock confers no reproducibility guarantee.")
            bad += 1
            continue
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        if actual == claimed:
            print(f"  [ok]       {rel}  {claimed[:12]}...")
        else:
            print(f"  [MISMATCH] {rel}")
            print(f"             locked : {claimed}")
            print(f"             actual : {actual}")
            if claimed == EMPTY_SHA or actual == EMPTY_SHA:
                print(f"             NOTE: one of these is the SHA-256 of empty input --")
                print(f"             usually a `git show <commit>:<missing-path> | shasum` artifact.")
            print(f"             Update the lock WITH an amendment note; never overwrite silently.")
            bad += 1
    for sp in suspect:
        print(f"  [UNPARSED] {sp} looks like a lock row but no valid sha256 was found in it.")
        bad += 1
    print()
    return len(rows), bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--code", required=True, nargs="+")
    ap.add_argument("--results", help="results file; each requirement ID must appear in it")
    ap.add_argument("--repo-root", default=".", help="root for resolving hash-locked paths")
    args = ap.parse_args()

    prereg = Path(args.prereg).read_text()
    m = BLOCK.search(prereg)
    if not m:
        print(f"[FAIL] {args.prereg} has no <!-- REQUIREMENTS ... --> block.")
        print("       Without one there is nothing to check, and requirements can be dropped")
        print("       silently -- which is the failure this tool exists to prevent.")
        return 2

    reqs = dict(ENTRY.findall(m.group(1)))
    if not reqs:
        print(f"[FAIL] REQUIREMENTS block in {args.prereg} is empty or malformed.")
        return 2

    code = "\n".join(Path(c).read_text() for c in args.code)
    claimed = set(CLAIM.findall(code))
    results = Path(args.results).read_text() if args.results else None

    print(f"prereg  : {args.prereg}")
    print(f"code    : {', '.join(args.code)}")
    print(f"results : {args.results or '(not checked)'}")
    print()

    n_hashes, bad = check_hashes(prereg, args.prereg, Path(args.repo_root))

    for rid, desc in sorted(reqs.items(), key=lambda kv: int(kv[0][1:])):
        if rid not in claimed:
            print(f"  [MISSING]  {rid}: {desc}")
            print(f"             no '# IMPLEMENTS {rid}' anywhere in the code.")
            bad += 1
        elif results is not None and rid not in results:
            print(f"  [NOT RUN]  {rid}: {desc}")
            print(f"             claimed in code but {rid} never reaches the results file --")
            print(f"             i.e. implemented but skipped at runtime.")
            bad += 1
        else:
            print(f"  [ok]       {rid}: {desc}")

    orphans = claimed - set(reqs)
    for o in sorted(orphans):
        print(f"  [ORPHAN]   {o} claimed in code but not listed in the prereg.")
        bad += 1

    print()
    if bad:
        print(f"[FAIL] {bad} problem(s). A preregistration that silently evaporates is worse than")
        print("       none -- it manufactures confidence. Resolve each explicitly.")
        return 1
    print(f"[ok] all {len(reqs)} requirements are claimed in code"
          f"{' and present in results' if results else ''}"
          f"{f'; all {n_hashes} hash locks verify' if n_hashes else ''}.")
    print("     This does NOT verify correctness -- only that nothing was silently dropped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
