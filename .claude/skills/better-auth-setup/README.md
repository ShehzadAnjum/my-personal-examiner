# How to Use This Skill with Claude

## Invoking the Skill

When you want Claude to set up authentication in a new Next.js project, say:

### ✅ Correct Way:
```
Use the better-auth-setup skill to set up authentication in this project.
Copy from ~/dev/evolution_to_do/frontend
```

or:

```
Apply the better-auth-setup skill
```

or:

```
Set up authentication using the better-auth-setup skill from .claude/skills/
```

### ❌ Wrong Way:
```
Implement better-auth
```
(This makes Claude recreate from scratch instead of using the skill)

---

## What Claude Will Do

When invoked, Claude should:

1. **Check the skill documentation**: `.claude/skills/better-auth-setup/SKILL.md`
2. **Run the setup script**: `./scripts/setup-better-auth.sh`
3. **Follow the checklist** in SKILL.md
4. **Verify** everything works

---

## Skill Structure (For Claude Code)

This skill follows the proper Claude Code skill structure:

```
.claude/skills/better-auth-setup/
├── SKILL.md         # Main documentation (what Claude reads)
├── skill.yaml       # Metadata (version, dependencies, etc.)
└── README.md        # This file (how to invoke)
```

**Why this structure?**
- Folder-based skills are properly discovered by Claude Code
- `.md` file at root was the old/wrong way
- `skill.yaml` provides structured metadata

---

## For Developers

**Manual Setup** (without Claude):
```bash
./scripts/setup-better-auth.sh ~/dev/evolution_to_do/frontend
node setup-better-auth-db.mjs
npm run dev
```

**Testing**:
Visit http://localhost:3000/login

---

## Version

**Current**: 1.0.0
**Last Updated**: 2025-12-24
**Tested**: ✅ Yes
