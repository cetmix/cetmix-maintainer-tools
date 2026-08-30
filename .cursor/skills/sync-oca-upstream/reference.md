# Sync OCA upstream — reference

## Remotes and history notes

| Remote | URL | Role |
|--------|-----|------|
| `origin` | `https://github.com/cetmix/cetmix-maintainer-tools.git` | Only remote allowed for push/commit publish |
| `OCA` | `https://github.com/OCA/maintainer-tools.git` | Fetch-only upstream (`push` URL must be `DISABLE_PUSH_TO_OCA`) |

Documented Cetmix-authored customization commits (still in history):

| Commit | Subject | Effect |
|--------|---------|--------|
| `4994bf0` | `[IMP] oca_towncrier` | Drop GitHub issue URL in towncrier issue format |
| `35c69f9` | `[IMP] template/module` (message mismatch) | `_make_issue_format` → `"{issue}"` |
| `a1cae73` | `[IMP] template/module` | Cetmix `icon.svg` added (later removed) |
| `e6329ad` | `[FIX] towncrier template` | Inline category lines; avoid duplicated headers |
| `7f6de8c` | `Cetmix Updates` | Remove OCA banner; Cetmix `icon.png`; drop `icon.svg` |

Prior Cetmix sync: PR [#6](https://github.com/cetmix/cetmix-maintainer-tools/pull/6) → merge commit `8da8e14` (`Merge branch 'OCA-master'`), incorporating OCA tip `368f7e9` / `26f0bff`.

OCA later: `71aa4ca` *Revert "Merge branch 'master' into master"* undid Cetmix file contents that had landed on OCA. Subsequent OCA work includes:

- `#671` / `7f6a368` — hide OCA banner when `org_name != 'OCA'` (Cetmix still removes banner entirely)
- `#676` / `2f90356` — HTML `<title>` from manifest name
- `#663` / `676ec44` — `oca-create-branch-from-previous`
- `#681` / `c15e855` — remove `repos_with_ids.txt`, `runbot_ids.py`, `add-badges.py`

## Pre-sync blob SHAs (as of `8da8e14`)

Use only as a baseline when re-syncing from that tip; after a successful sync, refresh this table.

| Blob | Path |
|------|------|
| `3963e676c9d5985c484b71ea0a19be5b3f23838e` | `template/module/static/description/icon.png` |
| `2ad375d00603070e6cfb7ae9b13b1eade18829d2` | `tools/gen_addon_readme.rst.jinja` |
| `982ff1a15f3c1a21507f902aeb7c8de716530fda` | `tests/data/readme_tests/addon1/README.expected-oca.rst` |
| `3f759fd1176b02eb7c55c86928e2073e94128b74` | `tests/data/readme_tests/addon_one_maintainer/README.expected-oca.rst` |
| `dc63c60c5ab49f1ab5637d11427c208ef45be9e3` | `tests/data/readme_tests/addon_two_maintainers/README.expected-oca.rst` |
| `b648bb09e509c277b4ce676d33e385cfe7223f4c` | `tools/oca_towncrier.py` |
| `db6cc457bc775656244b775574b5dbee70adde8a` | `tools/towncrier-template.md` |
| `0d0b592f182a5f97f30b2eea643221cf2c0e015f` | `tests/test_towncrier.py` |

`icon.svg` must be absent.

## Verification commands

```bash
git rev-parse OCA/master
git diff --name-status OCA/master HEAD
# Expect only customization files (and no stale OCA-only removals left behind)
```
