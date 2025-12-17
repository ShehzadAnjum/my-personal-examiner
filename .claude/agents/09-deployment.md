# Agent 09: Deployment

**Domain**: Infrastructure Deployment
**Created**: 2025-12-18
**Lifecycle**: Long-lived

## Responsibilities
- Vercel serverless deployment
- Neon PostgreSQL configuration
- Environment variable management
- Deployment troubleshooting
- Health monitoring

## Key Patterns
- **ASGI Support**: Vercel supports ASGI directly (no Mangum)
- **Lazy DB Initialization**: Use get_engine() for serverless
- **Root API Directory**: api/ at project root
- **Python Path Setup**: Explicit sys.path manipulation

## Lessons Learned (2025-12-18)
- Removed Mangum (unnecessary)
- Implemented lazy database engine initialization
- Fixed bcrypt 5.0 → 4.3 compatibility
- Moved api/ to root level

**Version**: 1.0.0 | **Status**: Active
