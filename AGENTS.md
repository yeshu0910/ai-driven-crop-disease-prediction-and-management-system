# AGENTS.md

## Project Context
AI-Driven Crop Disease Prediction and Management System. This is a spec-driven development project with a full Python backend (FastAPI), ML pipeline (PyTorch), mobile app, and CI/CD infrastructure.

## Key Conventions
- Python 3.10+, strict mypy, ruff formatting
- Specs live in `.specify/specs/` and are numbered sequentially
- All features require a spec before implementation

## Workflow
1. Check `.specify/specs/` for open or in-progress features
2. Implement in `src/` matching the spec requirements
3. Add tests in `tests/` with ≥80% coverage
4. Run `pytest`, `ruff check .`, `mypy .` before committing
5. Use conventional commits (`feat:`, `fix:`, `docs:`)

## Allowed Actions
- Create/modify files in `src/`, `tests/`, `docs/`, `.specify/specs/`
- Run tests and linting
- Update CHANGELOG.md via git-cliff on merged commits

## Restricted Actions
- Do NOT push directly to `main` — open MRs only
- Do NOT modify `.gitlab-ci.yml` without team approval
- Do NOT expose secrets in `.env`, `.env.example`, or code
- Do NOT run destructive git commands (force push, drop commits)

## CI/CD
- Pipeline: lint → typecheck → security → test → build → deploy
- Pre-commit hooks: ruff, mypy, bandit, gitleaks
- Merge only after all checks pass

## Reference Files
- `AGENTS.md` — this file
- `CONTRIBUTING.md` — how to contribute
- `.gitlab-ci.yml` — CI pipeline
- `pyproject.toml` — build and tool config
- `SECURITY.md` — vulnerability reporting
- `CODE_OF_CONDUCT.md` — community standards
