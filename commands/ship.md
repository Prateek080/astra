---
description: Run pre-flight checks, commit changes, and create a pull request
argument-hint: "[base branch]"
---

# Ship Phase

You are preparing changes for commit and pull request. Follow the pre-flight checklist before creating any commits.

## Pre-Flight Checks

1. **Run tests**: Execute the project's test suite. If any tests fail, stop and fix them first.
2. **Run linter/formatter**: If the project has a linter or formatter configured, run it.
3. **Check for secrets**: Scan staged files for anything that looks like credentials, API keys, or .env files. Warn if found.
4. **Check for debug artifacts**: Look for console.log, print(), debugger statements, or commented-out code in the diff.
5. **Review the diff**: Run `git diff --staged` (or `git diff` if nothing is staged). Summarize what changed and why.

## Commit

6. Stage relevant files by name. Do NOT use `git add -A` or `git add .` — be explicit about what's included.
7. Write a commit message:
   - First line: imperative mood, under 72 chars, explains WHY not WHAT
   - Body (if needed): context, trade-offs, or migration notes
   - End with: `Co-Authored-By: Claude <noreply@anthropic.com>`

## Pull Request

8. Push to remote with `-u` flag if the branch doesn't have an upstream.
9. Create PR using `gh pr create` with:
   - Title: short, under 70 chars
   - Body: summary bullets, test plan checklist, any migration notes
10. Return the PR URL to the user.

## Base Branch

If $ARGUMENTS specifies a base branch, use it. Otherwise, use the repository's default branch.
