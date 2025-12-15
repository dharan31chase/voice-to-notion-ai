# Git Hooks

This directory contains git hooks that should be installed in `.git/hooks/`.

## Why hooks are tracked here

Git doesn't track the `.git/hooks/` directory, so we keep a copy here and provide an install script.

## Installation

After cloning the repo or when hooks are updated:

```bash
bash scripts/git-hooks/install-hooks.sh
```

## Available Hooks

### `prepare-commit-msg`

Auto-fills commit message template with structured format:

- Subject line with ROADMAP tag
- What Shipped
- Critical Discovery (optional)
- Decisions
- Architecture Decisions (optional)
- Impact
- Next Steps
- Key Learnings

**Format enforced by**:
1. Git hook (pre-fills template)
2. CLAUDE.md instructions (teaches Claude how to fill it)

This ensures ~99% adherence to commit message standards.

## Updating Hooks

If you modify a hook:

1. Edit the file in `scripts/git-hooks/`
2. Run `bash scripts/git-hooks/install-hooks.sh` to reinstall
3. Commit the updated hook to the repo
