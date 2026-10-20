# FarmLens repository release plan

> **For agentic workers:** Use superpowers:executing-plans inline. Checkboxes track the release.

**Goal:** Audit, polish, commit and publish the local showcase as public
`tuannm3812/FarmLens`, using MIT for original code.
**Architecture:** Preserve the existing Python engine and local frontend.
Improve the repository entry point and release hygiene; fix substantive audit
findings with regression evidence. No public app deployment.
**Tech stack:** Python 3.11, pytest, Node test runner, Git and GitHub CLI.
**Spec:** The user's audit/commit/push request and explicit public-repository/MIT
choices in this conversation.

## Constraints and review focus

- Preserve local work, historical plans and third-party attribution.
- Exclude runtime caches, credentials, virtual environments and build outputs.
- The app remains loopback-only; a GitHub URL is not a hosted interactive demo.
- Do not imply calibrated crop accuracy or observed farm conditions.
- Confirm a fresh clone can install and run the checks without private paths.
- Check async state, missing data, API boundaries and output escaping.

## Tasks

- [x] Audit runtime code with a fresh read-only reviewer; fix important findings
  using a failing regression before the fix, then targeted passing checks.
- [x] Replace the build-history-heavy README with a concise public entry point;
  preserve the old detail in `docs/technical-reference.md` with working links.
- [x] Add MIT licence, third-party notice, contribution notes and documentation
  index; strengthen ignore rules and remove machine-specific tooling paths.
- [x] Run the full check command, asset/link/credential checks, and clean-copy
  installation smoke tests. Record the actual results.
- [x] Stage and inspect intended files, make the initial commit, create the
  authorized public GitHub repo, push, and inspect its CI result.
- [x] Report the repo URL and recommend a screenshot/video plus repository link
  for today. Public interactive hosting is a separate milestone.

## Ledger

- Ruling: continue in the existing no-HEAD checkout. This is the user's complete
  prototype, and moving it to a worktree before its first commit adds no isolation.
- Ruling: user explicitly approved public `tuannm3812/FarmLens` and MIT for original
  code. No additional publishing or licence approval gate is needed.
- Initial inventory: 242 candidate files, 12.9 MB; no file over 3 MB and no known
  credential-pattern matches. Runtime caches and `.venv` are excluded.
- Initial GitHub check: authenticated as `tuannm3812`, no FarmLens repository
  returned, and no local remote configured.

- Runtime review: 2 Important and 2 Minor findings reproduced and fixed. Added red→green cases for island imagery, optional image exception containment, stale-evidence explanation, zero-margin break-even and invalid texture fractions. Full local checks: 307 Python / 47 Node passed.
- Ruling: the user's repo-wide polish request includes the two small correctness edges; fixed them without expanding the model or UI scope.
- Documentation: concise public README, technical-history reference, doc index, MIT, third-party notice and contribution guide added. Fifteen photo hashes/credits checked; entry-point links resolve.
- Hygiene: preserve Markdown hard breaks and verbatim font licences through explicit Git attributes; normalize incidental HTML whitespace. Credential patterns absent; environment/cache/build outputs ignored.

- Clean-copy verification: only staged paths copied; no caches or env files. Editable-install metadata succeeds with no network; full 307 Python / 47 Node suite passes from the copy. Staged diff whitespace check passes.
- Publication complete: initial commit `74f7e00`, public repository `https://github.com/tuannm3812/FarmLens`, origin/main verified equal to HEAD. GitHub recognizes MIT. CI run `39388715220` succeeded on a fresh Ubuntu/Python 3.11/Node 22 environment.
- Share recommendation delivered: use the showcase image or short recording with the repository link today. No public app hosting or LinkedIn posting was performed.
