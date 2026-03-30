# Oleg-helper

Personal assistant powered by Claude Code.

## Setup

```bash
npm install
cp .env.example .env
# Edit .env with your values
```

## Development

```bash
npm run dev       # Start dev server with hot reload
npm run build     # Build for production
npm run test      # Run tests
npm run lint      # Lint codebase
```

## Project Structure

```
src/
  core/           # Core application logic
  services/       # External service integrations
  utils/          # Shared utility functions
  types/          # TypeScript type definitions
tests/            # Test files mirroring src/ structure
scripts/          # Build and automation scripts
```
