# Port Management - Quick Reference Card

**Skill**: port-management.md
**Updated**: 2025-12-24
**Print this**: Save as reference for stuck port issues

---

## 🚀 Quick Fix (Most Common)

```bash
# Kill default dev ports
./scripts/kill-ports.sh

# Or from anywhere (if alias set up)
kill-ports
```

---

## 🔍 Diagnostic Commands

```bash
# What's on port 3000?
netstat -tlnp | grep :3000

# What's on ports 3000-3002?
netstat -tlnp | grep -E ":300[0-2]"

# All Node.js processes
ps aux | grep node
```

---

## 💀 Kill Commands

### Script (Recommended)
```bash
./scripts/kill-ports.sh 3000 3001 3002
```

### One-Liners
```bash
# Kill specific ports
lsof -ti :3000,:3001,:3002 | xargs -r kill -9

# Kill all Next.js
pkill -9 -f next-server

# Nuclear: Kill all Node
pkill -9 node
```

---

## ⚠️ Common Errors

| Error | Fix |
|-------|-----|
| `EADDRINUSE :::3000` | `./scripts/kill-ports.sh 3000` |
| `Port in use` but lsof says free | IPv6 issue - use script v2.0+ |
| Permission denied | `sudo ./scripts/kill-ports.sh 3000` |
| Still stuck after kill | Wait 60s for TIME_WAIT |

---

## 🎯 By Scenario

### Next.js Won't Start
```bash
./scripts/kill-ports.sh 3000 3001 3002
npm run dev
```

### After IDE Crash
```bash
pkill -9 node
./scripts/kill-ports.sh
```

### WSL After Sleep
```bash
./scripts/kill-ports.sh
# May need sudo
```

### Full Stack Reset
```bash
# Kill frontend + backend
./scripts/kill-ports.sh 3000 8000
npm run dev &
cd backend && uv run uvicorn src.main:app --reload &
```

---

## 📁 Files

| File | Purpose |
|------|---------|
| `scripts/kill-ports.sh` | Main script |
| `scripts/PORT_KILLER_README.md` | Full docs |
| `.claude/skills/port-management.md` | Skill docs |

---

## 🔧 Setup Alias (One-Time)

```bash
echo 'alias kill-ports="~/dev/my_personal_examiner/scripts/kill-ports.sh"' >> ~/.bashrc
source ~/.bashrc
```

Now use anywhere: `kill-ports 3000`

---

## 📱 Mobile-Friendly Commands

```bash
# Shortest command
lsof -ti :3000 | xargs kill -9

# Check only
ss -tlnp | grep :3000

# Kill all Node
pkill -9 node
```

---

**💡 Pro Tip**: Add `./scripts/kill-ports.sh` to your `predev` npm script for automatic cleanup!

```json
{
  "scripts": {
    "predev": "bash ../../scripts/kill-ports.sh 2>/dev/null || true",
    "dev": "next dev"
  }
}
```
