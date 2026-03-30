# Oleg-helper

Personal assistant project powered by Claude Code.

## Project Overview

Oleg-helper is a personal assistant application. It serves as an intelligent helper for day-to-day tasks, automation, and productivity.

## Critical Rules

### Code Organization
- Many small files over few large files
- High cohesion, low coupling
- 200-400 lines typical, 800 max per file
- Organize by feature/domain, not by type

### Code Style
- No emojis in code, comments, or documentation
- Immutability preferred - avoid mutating objects or arrays
- No console.log in production code
- Proper error handling with try/catch
- Input validation at system boundaries

### Security
- No hardcoded secrets - use environment variables
- Never paste secrets (API keys, tokens, passwords, JWTs) in code or logs
- Validate all user inputs
- Parameterized queries only for database operations

### Testing
- Write tests for critical paths
- Unit tests for utilities
- Integration tests for APIs

## File Structure

```
src/
  core/           # Core application logic
  services/       # External service integrations
  utils/          # Shared utility functions
  types/          # TypeScript type definitions
tests/            # Test files mirroring src/ structure
scripts/          # Build and automation scripts
```

## Environment Variables

```bash
# Required (add to .env, never commit)
# API_KEY=
# DATABASE_URL=
```

## Available Commands

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run test` - Run test suite
- `npm run lint` - Lint codebase

## Git Workflow

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`
- Never commit to main directly
- PRs require review
- All tests must pass before merge
