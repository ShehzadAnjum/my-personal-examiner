# Skill: Port Management & Cleanup

**Type**: Development Tools
**Created**: 2025-12-24
**Domain**: DevOps, Process Management
**Parent Agent**: General (Cross-Project Utility)

## Overview
Manages stuck ports by identifying and killing processes that occupy development ports (3000-3002 for frontend, 8000 for backend). Handles both IPv4 and IPv6 bindings that commonly cause "EADDRINUSE" errors in Next.js, React, and FastAPI development.

## When to Use

### Common Scenarios
- **Error**: `EADDRINUSE: address already in use :::3000`
- **Error**: `Port 3000 is in use by an unknown process`
- Multiple dev servers running from previous sessions
- WSL port conflicts after system sleep/resume
- Orphaned processes after IDE crashes

### Not Needed When
- Port is genuinely free (check with `netstat -tlnp | grep :3000`)
- You want to run multiple services on different ports
- System services on privileged ports (<1024)

## Quick Commands

### Using the Script (Recommended)
```bash
# Kill default ports (3000, 3001, 3002)
./scripts/kill-ports.sh

# Kill specific ports
./scripts/kill-ports.sh 3000 8000 5432

# Kill single port
./scripts/kill-ports.sh 3000
```

### One-Liner Alternatives
```bash
# Kill ports 3000, 3001, 3002 (handles IPv4 + IPv6)
lsof -ti :3000,:3001,:3002 | xargs -r kill -9

# Kill single port with all methods
lsof -ti :3000 | xargs -r kill -9; fuser -k 3000/tcp 2>/dev/null

# Kill all Next.js processes
pkill -9 -f next-server

# Kill all Node.js processes (nuclear option)
pkill -9 node
```

### Diagnostic Commands
```bash
# Check what's on a port (IPv4 + IPv6)
netstat -tlnp | grep :3000
ss -tlnp | grep :3000

# List all Node.js processes
ps aux | grep node

# Check all ports 3000-3002
netstat -tlnp | grep -E ":300[0-2]"
```

## Technical Details

### IPv6 vs IPv4 Detection
- **lsof**: Good for IPv4, sometimes misses IPv6 (`:::port`)
- **netstat/ss**: Catches both IPv4 and IPv6 bindings
- **fuser**: Additional fallback, works on port number directly

### Why Multiple Tools Needed
Next.js binds to IPv6 by default (`:::3000`), which `lsof -ti :3000` may not detect. The script uses:
1. `lsof` - Primary IPv4 detection
2. `ss`/`netstat` - IPv6 detection
3. `fuser` - Fallback

### Graceful vs Force Kill
1. **SIGTERM** (graceful): `kill PID` - allows cleanup
2. **SIGKILL** (force): `kill -9 PID` - immediate termination
Script tries graceful first, then force after 1 second.

## Integration with Project

### Location
- **Script**: `scripts/kill-ports.sh`
- **Docs**: `scripts/PORT_KILLER_README.md`
- **Skill**: `.claude/skills/port-management.md`

### Make Globally Available
```bash
# Add alias to ~/.bashrc or ~/.zshrc
echo 'alias kill-ports="~/dev/my_personal_examiner/scripts/kill-ports.sh"' >> ~/.bashrc
source ~/.bashrc

# Now use from anywhere
kill-ports 3000 3001 3002
```

### Common Workflow
```bash
# 1. Kill stuck ports
./scripts/kill-ports.sh

# 2. Verify ports are free
netstat -tlnp | grep -E ":300[0-2]"

# 3. Start fresh
npm run dev  # Frontend on :3000
cd backend && uv run uvicorn src.main:app --reload  # Backend on :8000
```

## Troubleshooting

### Script says port is free but Next.js disagrees
**Cause**: IPv6 process not detected by lsof
**Solution**:
```bash
# Manual check
netstat -tlnp | grep :3000

# If you see ":::3000", kill by PID
kill -9 <PID>

# Or use updated script (v2.0+)
./scripts/kill-ports.sh 3000
```

### Permission denied
**Cause**: Process owned by different user or root
**Solution**:
```bash
# Check process owner
ps aux | grep <PID>

# Kill with sudo (last resort)
sudo ./scripts/kill-ports.sh 3000
```

### Port still in use after killing
**Cause**: TIME_WAIT state (TCP socket cleanup)
**Solution**: Wait 30-60 seconds or use different port

### Multiple Next.js dev servers
**Cause**: Previous `npm run dev` sessions didn't terminate
**Solution**:
```bash
# Kill all Next.js processes
pkill -9 -f next-server

# Or all Node.js
pkill -9 node
```

## Lessons Learned

### WSL-Specific Issues
- WSL sometimes holds ports after Windows sleep/resume
- May require `sudo` even for user-owned processes
- IPv6 binding more common in WSL than native Linux

### Next.js Port Behavior
- Searches for next available port if 3000 taken (3001, 3002, etc.)
- Binds to IPv6 (`:::`) by default, not just IPv4
- Can have multiple instances running if not cleaned up

### Prevention
```bash
# Add to package.json scripts
"predev": "pkill -9 -f next-server || true",
"dev": "next dev"
```

### Best Practices
1. Always check ports before starting dev servers
2. Use the script for consistent cleanup
3. Add cleanup to project README for team members
4. Consider Docker for isolated port management

## Related Skills
- **uv-package-management.md**: Backend dependency management
- **vercel-fastapi-deployment.md**: Production port configuration
- **pytest-testing-patterns.md**: Test port isolation

## Script Features (v2.0)

### Enhancements over v1.0
- ✅ IPv6 detection via netstat/ss
- ✅ Multiple PID source aggregation
- ✅ Duplicate PID filtering
- ✅ Color-coded output
- ✅ Process details before killing
- ✅ Graceful shutdown attempt
- ✅ Post-kill verification

### Future Improvements
- [ ] Add `--watch` mode for continuous monitoring
- [ ] Add `--restore` to remember and restart killed processes
- [ ] Add `--config` for custom port lists
- [ ] Integration with Docker port conflicts

## Usage Examples

### Frontend Development
```bash
# Start fresh frontend session
./scripts/kill-ports.sh 3000 3001 3002
cd frontend && npm run dev
```

### Full Stack Development
```bash
# Clear all dev ports
./scripts/kill-ports.sh 3000 8000
npm run dev &  # Frontend
cd backend && uv run uvicorn src.main:app --reload &  # Backend
```

### CI/CD Pipeline
```bash
# In GitHub Actions / Jenkins
- name: Clean ports
  run: |
    lsof -ti :3000,:8000 | xargs -r kill -9 || true
```

### Docker Conflicts
```bash
# If Docker containers hold ports
docker ps | grep 3000
docker stop <container_id>

# Or kill local processes first
./scripts/kill-ports.sh 3000
```

**Version**: 2.0.0 | **Last Updated**: 2025-12-24 | **Status**: Production Ready
