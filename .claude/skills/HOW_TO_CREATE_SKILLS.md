# How to Create Claude Code Skills

## ✅ Correct Skill Structure

```
.claude/skills/your-skill-name/
├── SKILL.md         # Main documentation (REQUIRED)
├── skill.yaml       # Metadata (OPTIONAL but recommended)
└── README.md        # Usage instructions (OPTIONAL)
```

## ❌ Wrong Structure

```
.claude/skills/
└── your-skill-name.md  # ❌ This won't be properly discovered
```

---

## File Details

### 1. `SKILL.md` (Required)

Main skill documentation that Claude reads.

**Template**:
```markdown
# Your Skill Name

**Version**: 1.0.0
**Last Updated**: YYYY-MM-DD

## Purpose

What does this skill do?

## When to Use

✅ Use when: ...
❌ Don't use when: ...

## Quick Start

Step-by-step instructions...

## Troubleshooting

Common issues and fixes...
```

### 2. `skill.yaml` (Optional)

Structured metadata for the skill.

**Template**:
```yaml
name: your-skill-name
description: Brief description
version: 1.0.0
author: Your Name
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
tags:
  - category1
  - category2
dependencies:
  - package1
  - package2
tested: true
working: true
```

### 3. `README.md` (Optional)

How to invoke the skill when talking to Claude.

**Template**:
```markdown
# How to Use This Skill

## Invoking the Skill

Say to Claude:
"Use the your-skill-name skill to..."

## What It Does

1. Step 1
2. Step 2
3. Step 3
```

---

## Example: Better-Auth Setup Skill

```
.claude/skills/better-auth-setup/
├── SKILL.md         # 12KB - Complete setup guide
├── skill.yaml       # 470B - Metadata
└── README.md        # 1KB - How to invoke
```

**Invoke with**:
```
Use the better-auth-setup skill
```

---

## Naming Conventions

### Skill Folder Name
- **Use kebab-case**: `better-auth-setup`
- **Be descriptive**: `nextjs-prisma-setup` not just `prisma`
- **Avoid generic names**: `database-migration` not just `db`

### File Names
- `SKILL.md` (uppercase) or `skill.md` (lowercase) - both work
- `skill.yaml` (lowercase preferred)
- `README.md` (uppercase preferred)

---

## Skill Categories

Organize skills by purpose:

```
.claude/skills/
├── better-auth-setup/       # Authentication
├── nextjs-tailwind-setup/   # UI framework
├── fastapi-sqlmodel-setup/  # Backend framework
├── neon-postgres-setup/     # Database
└── vercel-deployment/       # Deployment
```

---

## Best Practices

### 1. **Test Before Committing**
- Run the skill in a fresh project
- Verify all steps work
- Document any prerequisites

### 2. **Include Reference Projects**
```yaml
reference_project: ~/dev/working-example
```

### 3. **Version Your Skills**
```yaml
version: 1.0.0
```
Update version when making changes.

### 4. **Add Time Estimates**
```yaml
time_to_setup: 5 minutes
complexity: low
```

### 5. **Include Troubleshooting**
Document common errors and fixes.

### 6. **Add Testing Checklist**
```markdown
## Testing Checklist

- [ ] Step 1 works
- [ ] Step 2 works
- [ ] Final result verified
```

---

## Skill Discovery

Claude Code discovers skills by:
1. Scanning `.claude/skills/` directory
2. Looking for folders (not individual .md files)
3. Reading `SKILL.md` or `skill.md` in each folder
4. Optionally reading `skill.yaml` for metadata

**That's why** we need the folder structure!

---

## Invoking Skills

### ✅ Good Invocations
```
"Use the better-auth-setup skill"
"Apply the nextjs-tailwind-setup skill to this project"
"Run the database-migration skill"
```

### ❌ Bad Invocations
```
"Implement better-auth" # Claude recreates from scratch
"Add authentication"    # Claude doesn't know to use skill
```

---

## Converting Old Skills

If you have old `.md` files in `.claude/skills/`:

```bash
# Old structure
.claude/skills/my-skill.md

# Convert to new structure
mkdir .claude/skills/my-skill/
mv .claude/skills/my-skill.md .claude/skills/my-skill/SKILL.md

# Add metadata
cat > .claude/skills/my-skill/skill.yaml << EOF
name: my-skill
version: 1.0.0
EOF
```

---

## Skill Template Generator

Create this as `scripts/create-skill.sh`:

```bash
#!/bin/bash

SKILL_NAME=$1

if [ -z "$SKILL_NAME" ]; then
  echo "Usage: ./create-skill.sh skill-name"
  exit 1
fi

mkdir -p .claude/skills/$SKILL_NAME

cat > .claude/skills/$SKILL_NAME/SKILL.md << EOF
# $SKILL_NAME

**Version**: 1.0.0
**Last Updated**: $(date +%Y-%m-%d)

## Purpose

What does this skill do?

## Quick Start

Step-by-step instructions...
EOF

cat > .claude/skills/$SKILL_NAME/skill.yaml << EOF
name: $SKILL_NAME
version: 1.0.0
created: $(date +%Y-%m-%d)
tested: false
EOF

echo "✅ Skill created at .claude/skills/$SKILL_NAME/"
```

---

## Summary

✅ **Do**:
- Create folder structure
- Add SKILL.md with detailed docs
- Include troubleshooting
- Test in fresh project
- Version your skills

❌ **Don't**:
- Use single .md files
- Skip testing
- Use generic names
- Forget to update versions
