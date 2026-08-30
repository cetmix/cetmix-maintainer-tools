# Cetmix customizations

This repository is a Cetmix fork of [OCA/maintainer-tools](https://github.com/OCA/maintainer-tools).

**Write only to Cetmix** (`cetmix/cetmix-maintainer-tools`). Never commit or push to the OCA upstream repo; sync is fetch + merge into this fork only.

Only the changes below are intentional Cetmix customizations. Everything else should track OCA `master`.

## 1. Cetmix module icon

**Commits:** `a1cae73`, `7f6de8c`

- Keep Cetmix `template/module/static/description/icon.png`.
- Do not keep OCA `template/module/static/description/icon.svg` (removed in `7f6de8c`).

## 2. No OCA README banner

**Commit:** `7f6de8c`

- `tools/gen_addon_readme.rst.jinja` must not include the `odoo-community.org/readme-banner-image` block (even when `org_name == 'OCA'`).
- Matching fixtures without the banner:
  - `tests/data/readme_tests/addon1/README.expected-oca.rst`
  - `tests/data/readme_tests/addon_one_maintainer/README.expected-oca.rst`
  - `tests/data/readme_tests/addon_two_maintainers/README.expected-oca.rst`

Note: OCA `#671` only hides the banner when `org_name != 'OCA'`. Cetmix removes it unconditionally.

## 3. Towncrier issue references without GitHub links

**Commits:** `4994bf0`, `35c69f9`

In `tools/oca_towncrier.py`, `_make_issue_format` returns only `"{issue}"` (Cetmix uses internal task numbers, not GitHub issue URLs).

## 4. Towncrier Markdown template layout

**Commit:** `e6329ad`

Workaround for duplicated category headers:

- `tools/towncrier-template.md` — list items as `- {{ category name }}: {{ text }}` (no `### Category` headings).
- `tests/test_towncrier.py` — must match Cetmix outputs, e.g.:
  - `_make_issue_format` → `"{issue}"` for both `rst` and `md`
  - RST history line: `- Bugfix description. (50)`
  - MD history line: `- Bugfixes: Bugfix description. (50)`

## Not customizations

| Observation | Action on sync |
|-------------|----------------|
| `tools/ocb-sync.sh` listing `14.0` while OCA does not | Take OCA (merge artifact / stale line; not a Cetmix commit) |
| Presence of `tools/repos_with_ids.txt`, `tools/runbot_ids.py`, `tools/add-badges.py` while OCA removed them | Take OCA deletion |
| Missing `oca-create-branch-from-previous` / related tests while OCA added them | Take OCA addition |

## Syncing from OCA

Use the project skill `.cursor/skills/sync-oca-upstream/` (see `SKILL.md`). A plain merge can silently overwrite the files above because OCA reverted an accidental Cetmix merge (`71aa4ca`); always re-apply this inventory after merging.
