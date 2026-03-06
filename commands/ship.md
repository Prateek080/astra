---
description: Run pre-flight checks, commit changes, and create a pull request
argument-hint: "[base branch]"
---

> **Arguments**: Any text the user provides after the command name serves as input. In Claude Code, this is substituted into $ARGUMENTS automatically.

# Ship Phase

You are preparing changes for commit and pull request. Follow the pre-flight checklist before creating any commits.

## Pre-Flight Checks

1. **Check tools**: Verify `gh` CLI is installed by running `gh --version`. If not found, warn the user: "`gh` CLI is not installed. I can commit and push, but won't be able to create a PR. Install it from https://cli.github.com/ or skip the PR step." Let the user decide whether to proceed without PR creation.
2. **Check the branch**: Run `git branch --show-current`. If on the repository's default branch (main/master/develop), warn the user: "You're on [branch]. Shipping will push directly to the default branch. Do you want to create a feature branch first?" Only proceed after the user confirms. If the user wants a branch, create one with a descriptive name based on the changes and switch to it.
3. **Run tests**: Execute the project's test suite. If any tests fail, stop and fix them first.
4. **Run linter/formatter**: If the project has a linter or formatter configured, run it.
5. **Check for secrets**: Scan staged files for anything that looks like credentials, API keys, or .env files. Warn if found.
6. **Check for debug artifacts**: Look for console.log, print(), debugger statements, or commented-out code in the diff.
7. **Review the diff**: Run `git diff --staged` (or `git diff` if nothing is staged). Summarize what changed and why.

## Commit

8. Stage relevant files by name. Do NOT use `git add -A` or `git add .` — be explicit about what's included.
9. Write a commit message:
   - First line: imperative mood, under 72 chars, explains WHY not WHAT
   - Body (if needed): context, trade-offs, or migration notes
   - Do NOT add Co-Authored-By or any AI attribution to the commit message

## Pull Request

10. Push to remote with `-u` flag if the branch doesn't have an upstream.
11. Create PR using `gh pr create` with (skip if `gh` is not available):
    - Title: short, under 70 chars
    - Body: summary bullets, test plan checklist, any migration notes
12. Return the PR URL to the user. If the changes involved a non-trivial bug fix or architectural decision, suggest: "Consider running `/astra:compound` to document this solution for future reference."

## Base Branch

If $ARGUMENTS specifies a base branch, use it. Otherwise, use the repository's default branch.
