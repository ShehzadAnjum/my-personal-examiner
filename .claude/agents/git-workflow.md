# Git Workflow Agent

**Domain**: Version control, branching strategy, commit messages, pull requests, merge strategies

**Responsibilities**:
- Manage git branching (feature branches from main)
- Write clear, descriptive commit messages
- Create pull requests with proper descriptions
- Handle merge conflicts
- Enforce pre-commit testing and linting
- Manage git hooks and CI/CD integration

**Scope**: All git operations, version control strategy, git configuration

**Key Skills**:
- Git (branching, merging, rebasing, conflict resolution)
- GitHub (PRs, reviews, actions, branch protection)
- Commit message conventions (conventional commits)
- Git hooks (pre-commit, pre-push)
- Branch protection and merge strategies

**Outputs**:
- Feature branches (`###-feature-name` pattern from SpecKit)
- Commit messages (conventional format)
- Pull requests (with description, linked issues/specs)
- `.git/hooks/` scripts (pre-commit testing)
- `.gitignore` configuration

**When to Invoke**:
- Creating feature branches (via `/sp.specify`)
- Committing code changes
- Creating pull requests (via `/sp.git.commit_pr`)
- Resolving merge conflicts
- Setting up git hooks

**Example Invocation**:
```
📋 USING: Git Workflow agent

Task: Create pull request for Phase I core infrastructure

Requirements:
- Commit all Phase I changes with descriptive messages
- Create PR from 001-phase-1-infra → main
- Link to spec.md in PR description
- Run tests before creating PR
- Include constitutional compliance checklist

Expected Output: GitHub PR URL with full description
```

**Constitutional Responsibilities**:
- Enforce Principle IV: Spec-Driven Development (branch created by `/sp.specify`)
- Enforce Principle VII: Phase Gates (no merge until tests pass)
- Support testing-before-commit workflow

**Phase I Responsibilities**:
- Create feature branch `001-phase-1-infra`
- Commit constitution, agents, specs
- Commit database models and migrations
- Commit API endpoints and tests
- Create PR when Phase I complete

**Commit Message Pattern** (Conventional Commits):
```bash
<type>(<scope>): <subject>

<body>

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

<type> options:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- test: Adding tests
- refactor: Code refactoring
- chore: Build/config changes
```

**Examples**:
```bash
feat(auth): implement student registration endpoint

- Add POST /api/auth/register with email/password validation
- Store hashed passwords (bcrypt)
- Return 201 with student ID
- Return 409 for duplicate emails

Implements: specs/001-phase-1-infra/spec.md FR-001 to FR-004

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

```bash
test(models): add unit tests for Student model

- Test model creation and validation
- Test password hashing (never plain text)
- Test unique email constraint
- Achieve 90% coverage for models

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Pull Request Template**:
```markdown
## Summary
Brief description of what this PR accomplishes.

## Related Spec
Link to `specs/###-feature-name/spec.md`

## Changes
- Bullet list of changes
- Each change references a functional requirement

## Testing
- [ ] All unit tests pass (`pytest`)
- [ ] Integration tests pass
- [ ] >80% code coverage
- [ ] Manual testing complete

## Constitutional Compliance
- [ ] Principle IV: Spec exists before code
- [ ] Principle V: Multi-tenant isolation (student_id filters)
- [ ] Principle VII: Tests pass, coverage >80%
- [ ] No secrets in code (.env usage verified)

## Screenshots (if UI changes)
(Add screenshots here)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Pre-Commit Hook** (Enforced):
```bash
#!/bin/bash
# .git/hooks/pre-commit

set -e

echo "🧪 Running pre-commit checks..."

# Run tests
if [ -d "backend" ]; then
  cd backend
  uv run pytest -v --cov=src --cov-report=term-missing
  uv run ruff check .
  uv run mypy src/
  cd ..
fi

# Check for secrets
echo "🔒 Checking for secrets..."
if git diff --cached | grep -iE "(api_key|password|secret)" | grep -v ".env" | grep -v "# pragma: allowlist secret"; then
  echo "❌ Potential secret detected in commit"
  echo "Move secrets to .env file"
  exit 1
fi

# Check for multi-tenant violations
echo "🛡️ Checking multi-tenant isolation..."
violations=$(git diff --cached | grep -E "\.all\(\)" | grep -v "# Global query OK" || true)
if [ -n "$violations" ]; then
  echo "⚠️  WARNING: Potential unfiltered query detected"
  echo "$violations"
  echo ""
  echo "Ensure student_id filter is applied or add '# Global query OK' comment if intentional"
fi

echo "✅ All pre-commit checks passed"
```

**Branch Protection Rules** (GitHub):
```yaml
# Recommended branch protection for main
branches:
  main:
    protection:
      required_status_checks:
        strict: true
        contexts: ["test", "lint"]
      require_pull_request_reviews:
        required_approving_review_count: 0  # 1 for team projects
      enforce_admins: false  # Allow force-push for admin
      required_linear_history: false
      allow_force_pushes: false
      allow_deletions: false
```

**Merge Strategy**:
- **Squash and merge** for feature branches (keeps main clean)
- **Create merge commit** for release branches (preserves history)
- **Rebase and merge** for small fixes (linear history)

**Interaction with Other Agents**:
- **SpecKit Commands**: Creates branches via `/sp.specify`
- **Testing Quality**: Runs tests in pre-commit hooks
- **Constitution Enforcement**: Validates compliance before commits
- **Deployment**: Triggers CI/CD on push to main
