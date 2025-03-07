"""Run copier update on a branch in all addons repos."""

import subprocess
import textwrap
from pathlib import Path
from typing import Iterable, Optional, Tuple

import click
import requests

from .gitutils import commit_if_needed
from .oca_projects import BranchNotFoundError, get_repositories, temporary_clone

IGNORED_REJ_FILES = ["oca_dependencies.txt.rej"]


def _make_update_dotfiles_branch(branch: str) -> str:
    return f"{branch}-ocabot-update-dotfiles"


def _make_commit_msg(ci_skip: bool) -> str:
    msg = "[IMP] update dotfiles"
    if ci_skip:
        msg += " [ci skip]"
    return msg


def _get_update_dotfiles_open_pr(org: str, repo: str, branch: str) -> Optional[str]:
    r = requests.get(
        f"https://api.github.com/repos"
        f"/{org}/{repo}/pulls"
        f"?base={branch}&head={org}:{_make_update_dotfiles_branch(branch)}"
    )
    r.raise_for_status()
    prs = r.json()
    if not prs:
        return None
    pr = prs[0]
    if pr["state"] == "open":
        return pr["number"]
    return None


def _make_update_dotfiles_pr(org: str, repo: str, branch: str) -> None:
    pr_branch = _make_update_dotfiles_branch(branch)
    subprocess.check_call(["git", "checkout", "-B", pr_branch])
    subprocess.check_call(["git", "add", "."])
    subprocess.check_call(["git", "commit", "-m", _make_commit_msg(ci_skip=False)])
    subprocess.check_call(["git", "push", "-f", "origin", pr_branch])
    if not _get_update_dotfiles_open_pr(org, repo, branch):
        subprocess.check_call(
            [
                "gh",
                "pr",
                "create",
                "--repo",
                f"{org}/{repo}",
                "--base",
                branch,
                "--title",
                f"[{branch}] dotfiles update needs manual intervention",
                "--body",
                textwrap.dedent(
                    """\
                        Dear maintainer,

                        After updating the dotfiles, `pre-commit run -a`
                        fails in a manner that cannot be resolved automatically.

                        Can you please have a look, fix and merge?

                        Thanks,
                    """
                ),
                "--label",
                "help wanted",
            ]
        )


def _iterate_repos_and_branches(repos: str, branches: str) -> Iterable[Tuple[str, str]]:
    if repos == ":all:":
        all_repos = get_repositories()
    else:
        all_repos = repos.split(",")
    for repo in all_repos:
        repo = repo.strip()
        if not repo:
            continue
        for branch in branches.split(","):
            branch = branch.strip()
            if not branch:
                continue
            yield repo, branch


def _fix_copier_answers():
    copier_answers_path = Path(".copier-answers.yml")
    if not copier_answers_path.exists():
        return
    modified_copier_answers = copier_answers = copier_answers_path.read_text()
    modified_copier_answers = modified_copier_answers.replace(
        "repo_description: null", 'repo_description: ""'
    )
    if modified_copier_answers != copier_answers:
        copier_answers_path.write_text(modified_copier_answers)
        subprocess.check_call(["git", "add", ".copier-answers.yml"])
        subprocess.check_call(["git", "commit", "-m", "[FIX] .copier-answers.yml"])


@click.command()
@click.option("--org", default="OCA", show_default=True)
@click.option(
    "--repos",
    required=True,
    help="Comma-separated list of repo names, or :all:",
)
@click.option(
    "--branches",
    required=True,
    help="Comma-separated list of branches",
)
@click.option(
    "--git-user-name",
    default="oca-git-bot",
    show_default=True,
)
@click.option(
    "--git-user-email",
    default="oca-git-bot@odoo-community.org",
    show_default=True,
)
@click.option("--skip-ci/--no-skip-ci", default=False)
@click.option("--git-protocol", default="git", show_default=True)
def main(
    org: str,
    repos: str,
    branches: str,
    git_user_name: str,
    git_user_email: str,
    skip_ci: bool,
    git_protocol: str,
) -> None:
    for repo, branch in _iterate_repos_and_branches(repos, branches):
        try:
            with temporary_clone(
                org_name=org, project_name=repo, branch=branch, protocol=git_protocol
            ):
                print("=" * 10, repo, branch, "=" * 10)
                if git_user_name:
                    subprocess.check_call(
                        ["git", "config", "user.name", git_user_name],
                    )
                if git_user_email:
                    subprocess.check_call(
                        ["git", "config", "user.email", git_user_email],
                    )
                if not Path(".copier-answers.yml").exists():
                    print(f"Skipping {repo} because it has no .copier-answers.yml")
                    continue
                _fix_copier_answers()
                r = subprocess.call(["copier", "update", "-f", "--trust"])
                if r != 0:
                    print("$" * 10, f"copier update failed on {repo}")
                    continue
                subprocess.check_call(["rm", "-f"] + IGNORED_REJ_FILES)
                # git add updated files so pre-commit run -a will pick them up
                # (notably newly created .rej files)
                subprocess.check_call(["git", "add", "."])
                # run up to 3 pre-commit passes, in case autofixers
                # (which cause pre-commit to fail when they change files)
                # resolve issues
                for _ in range(3):
                    r = subprocess.call(["pre-commit", "run", "-a"])
                    # git add, in case pre-commit created new files
                    subprocess.check_call(["git", "add", "."])
                    if r == 0:
                        break
                if r != 0:
                    print("$" * 10, f"need manual intervention in {repo}")
                    _make_update_dotfiles_pr(org, repo, branch)
                    continue
                if commit_if_needed(["."], _make_commit_msg(ci_skip=skip_ci)):
                    subprocess.check_call(["git", "push"])
        except BranchNotFoundError:
            pass
