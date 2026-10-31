# GitHub Workflow

## Repository Information
- **URL:** https://github.com/aviralb1311/Subscription-Management-System
- **Owner:** aviralb1311
- **Name:** Subscription-Management-System
- **Main Branch:** main

## Branching Strategy
- `main` - Production-ready code
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates

## Commit Message Conventions
```
Type: Brief description

Detailed explanation if needed
```
Types: feat, fix, docs, style, refactor, test, chore

## Hourly Push Requirement
During active development, push at least once every hour. Commit completed logical units of work regularly.

## Pre-commit Checks
- [ ] Run backend tests: `cd backend && pytest`
- [ ] Run frontend tests: `cd frontend && npm test`
- [ ] Build frontend: `cd frontend && npm run build`
- [ ] No secrets or .env files staged
- [ ] Code follows architecture guidelines

## Push Verification
Always verify push succeeded by checking `git push` output.

## Conflict Resolution
1. Pull latest: `git pull origin main`
2. Resolve conflicts manually
3. Test after resolution
4. Commit and push

## Rules
- Never commit .env files or credentials
- Never force-push without explicit approval
- Never overwrite existing remote history
- Push at least once per hour during active development
- Record pushes in PROGRESS.md
