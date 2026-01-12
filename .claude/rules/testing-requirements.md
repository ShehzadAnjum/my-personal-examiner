# Rule: Testing Requirements

**Priority**: HIGH
**Enforcement**: All new code

---

## Rule Statement

All new code must have ≥80% test coverage. No PR merges without passing tests.

## Coverage Targets

| Component | Minimum | Current |
|-----------|---------|---------|
| Models | 100% | 100% |
| Services | 100% | 100% |
| Routes | 90% | 90% |
| Schemas | 100% | 100% |
| **Overall** | **80%** | **82%** |

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Fast, isolated tests
│   ├── test_models.py
│   └── test_services.py
└── integration/             # API and database tests
    └── test_routes.py
```

## Running Tests

```bash
cd backend
uv run pytest tests/ -v                           # All tests
uv run pytest tests/ --cov=src --cov-report=term  # With coverage
uv run pytest tests/unit/ -v                      # Unit only
```

## Phase Gate Validation

Before completing any phase:
```bash
./scripts/check-phase-N-complete.sh
```

## Skill Reference

Use `.claude/skills/pytest-testing-patterns.md` for patterns.
