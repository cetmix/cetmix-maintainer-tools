---
name: sync-oca-upstream
description: >-
  Sync cetmix/cetmix-maintainer-tools with upstream OCA/maintainer-tools while
  preserving Cetmix customizations. Use when updating from OCA, merging
  upstream, or refreshing this Cetmix fork of maintainer-tools.
---

# Sync OCA upstream into Cetmix maintainer-tools

## Facts (do not invent others)

- This repo: `https://github.com/cetmix/cetmix-maintainer-tools` (`origin`).
- Upstream: `https://github.com/OCA/maintainer-tools` (remote name: `OCA`, branch: `master`).
- **Never commit or push to OCA.** Only `origin` (Cetmix) is a write remote. Keep `OCA` fetch-only (`git remote set-url --push OCA DISABLE_PUSH_TO_OCA`).
- Prior sync pattern (PR #6): fetch OCA `master`, merge into Cetmix `master`, keep Cetmix customizations.
- OCA commit `71aa4ca` reverted an accidental merge of Cetmix into OCA. Those Cetmix commits remain in OCA history; the revert restored OCA file contents. A plain `git merge OCA/master` can **silently** replace Cetmix customization files with OCA versions (no conflict markers). Always re-apply customizations after the merge.

## Customizations to preserve

Authoritative inventory: [docs/CETMIX_CUSTOMIZATIONS.md](../../../docs/CETMIX_CUSTOMIZATIONS.md).

| Area | Files | Required end state |
|------|-------|--------------------|
| Icon | `template/module/static/description/icon.png` | Cetmix PNG (pre-sync blob) |
| Icon | `template/module/static/description/icon.svg` | Must not exist |
| No OCA banner | `tools/gen_addon_readme.rst.jinja` | No `readme-banner-image` block |
| No OCA banner | `tests/data/readme_tests/*/README.expected-oca.rst` | No banner lines |
| Towncrier issues | `tools/oca_towncrier.py` | `_make_issue_format` returns `"{issue}"` only |
| Towncrier layout | `tools/towncrier-template.md`, `tests/test_towncrier.py` | Inline `- Category: text (N)`; tests must assert Cetmix issue format and outputs (not OCA GitHub URLs) |

Not a Cetmix customization: `tools/ocb-sync.sh` still listing `14.0` — take OCA (no `14.0`).

## Workflow

Copy and track:

```
Sync progress:
- [ ] 1. Preconditions
- [ ] 2. Snapshot customizations
- [ ] 3. Fetch and merge OCA/master
- [ ] 4. Re-apply customizations
- [ ] 5. Verify inventory
- [ ] 6. Run tests
- [ ] 7. Stop for user review (commit/push only if asked)
```

### 1. Preconditions

```bash
git status   # must be clean
git remote get-url OCA || git remote add OCA https://github.com/OCA/maintainer-tools.git
git fetch OCA master
git merge-base HEAD OCA/master
git log --oneline HEAD..OCA/master
```

If working tree is dirty, stop.

### 2. Snapshot customizations

Record `PRESYNC=$(git rev-parse HEAD)`. Archive the preserve-list files from `HEAD` (or note blob SHAs) before merging.

### 3. Fetch and merge

```bash
git merge --no-ff OCA/master -m "$(cat <<'EOF'
Merge branch 'OCA-master'

EOF
)"
```

Resolve any real conflicts using OCA for non-custom files and Cetmix for the preserve-list.

### 4. Re-apply customizations

Restore preserve-list files from `$PRESYNC` (or the snapshot). Delete `icon.svg` if the merge re-added it:

```bash
git checkout "$PRESYNC" -- \
  template/module/static/description/icon.png \
  tools/gen_addon_readme.rst.jinja \
  tests/data/readme_tests/addon1/README.expected-oca.rst \
  tests/data/readme_tests/addon_one_maintainer/README.expected-oca.rst \
  tests/data/readme_tests/addon_two_maintainers/README.expected-oca.rst \
  tools/oca_towncrier.py \
  tools/towncrier-template.md \
  tests/test_towncrier.py
git rm -f --ignore-unmatch template/module/static/description/icon.svg
```

If OCA changed a preserve-list file in a way that must be combined (not overwrite), stop and ask the user — do not guess.

### 5. Verify inventory

```bash
# Banner must be absent
! grep -R 'readme-banner-image' tools/gen_addon_readme.rst.jinja \
    tests/data/readme_tests/*/README.expected-oca.rst
# Issue format
grep -A2 '_make_issue_format' tools/oca_towncrier.py   # only return "{issue}"
# Icon
test -f template/module/static/description/icon.png
test ! -e template/module/static/description/icon.svg
# OCB branches match OCA (no accidental 14.0)
grep '^BRANCHES=' tools/ocb-sync.sh
git show OCA/master:tools/ocb-sync.sh | grep '^BRANCHES='
```

Confirm `git diff OCA/master --stat` only shows expected Cetmix deltas plus any intentional leftover.

### 6. Run tests

```bash
tox -e py  # or the env used in CI; see tox.ini / .github/workflows/ci.yml
```

### 7. Finish

Do not commit or push unless the user asks. Report: OCA tip SHA, merge commit (if any), verification results, test results.

## Anti-patterns

- Do not push, PR, or commit to `OCA/maintainer-tools` — fetch/merge only.
- Do not assume undocumented “Cetmix” changes from diff noise (e.g. `14.0` in `ocb-sync.sh`).
- Do not force-push Cetmix `master`.
- Do not skip re-apply after merge — silent overwrite is expected because of OCA’s revert.
