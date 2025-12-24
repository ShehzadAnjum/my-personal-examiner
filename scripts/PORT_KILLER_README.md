# Port Killer Script - Quick Reference

## Usage

### Using the Script (Recommended)

```bash
# Kill default ports (3000, 3001, 3002)
./scripts/kill-ports.sh

# Kill specific ports
./scripts/kill-ports.sh 3000 8000 5432

# Kill a single port
./scripts/kill-ports.sh 3000
```

### One-Liner Alternatives

**Kill ports 3000, 3001, 3002 (Linux/WSL):**

```bash
# Using lsof (most reliable)
lsof -ti :3000,:3001,:3002 | xargs -r kill -9

# Using fuser (alternative)
fuser -k 3000/tcp 3001/tcp 3002/tcp
```

**Kill a single port:**

```bash
# Port 3000
lsof -ti :3000 | xargs -r kill -9

# Port 8000
lsof -ti :8000 | xargs -r kill -9
```

**Find what's using a port (without killing):**

```bash
# Check port 3000
lsof -i :3000

# Or with more details
netstat -tlnp | grep :3000

# Or with ss (modern alternative)
ss -tlnp | grep :3000
```

**Kill all Node.js processes:**

```bash
pkill -9 node
```

**Kill all Next.js dev servers:**

```bash
pkill -9 -f "next dev"
```

## Common Scenarios

### Stuck Next.js Dev Server

```bash
# Kill all Next.js processes
./scripts/kill-ports.sh 3000 3001 3002

# Or target Next.js specifically
pkill -9 -f "next dev"
```

### Port Already in Use Error

When you see:
```
Error: listen EADDRINUSE: address already in use :::3000
```

Run:
```bash
./scripts/kill-ports.sh 3000
```

### Clean Slate (Kill Everything)

```bash
# Kill frontend (Next.js)
./scripts/kill-ports.sh 3000 3001 3002

# Kill backend (FastAPI)
./scripts/kill-ports.sh 8000

# Kill database (if running locally)
./scripts/kill-ports.sh 5432
```

## Troubleshooting

### Script says ports are free but they're not

**Problem**: Next.js says "Port 3000 is in use" but script shows it's free

**Cause**: Process is bound to IPv6 (`:::3000`) which `lsof` sometimes misses

**Solution**: Script now checks multiple sources (lsof + netstat/ss + fuser) to catch all processes

**Manual check**:
```bash
# See what's actually on the port
netstat -tlnp | grep :3000
# or
ss -tlnp | grep :3000
```

### Script says "command not found"

```bash
# Make script executable
chmod +x scripts/kill-ports.sh
```

### Permission Denied

```bash
# Try with sudo (last resort)
sudo ./scripts/kill-ports.sh 3000
```

### lsof command not found

```bash
# Install lsof (Ubuntu/Debian)
sudo apt-get install lsof

# Or use fuser alternative
fuser -k 3000/tcp
```

### Multiple Next.js servers running

If you have multiple Next.js dev servers stuck:

```bash
# Kill all Next.js processes
pkill -9 node

# Or kill all next-server processes specifically
pkill -9 -f next-server

# Then verify
netstat -tlnp | grep -E ":300[0-2]"
```

## Add to PATH (Optional)

To use the script from anywhere:

```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'alias kill-ports="~/dev/my_personal_examiner/scripts/kill-ports.sh"' >> ~/.bashrc
source ~/.bashrc

# Now you can run from anywhere
kill-ports 3000 3001 3002
```

## Safety Notes

- The script tries graceful shutdown (SIGTERM) first, then force kill (SIGKILL)
- Always check what's running before killing: `lsof -i :3000`
- Be careful with `sudo` - only use if you own the process
- Don't kill system processes (ports < 1024 without sudo)
