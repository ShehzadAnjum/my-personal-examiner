import { toNextJsHandler } from "better-auth/next-js";

/**
 * Better-Auth API route handler
 *
 * This catch-all route handles all authentication endpoints:
 * - /api/auth/sign-in
 * - /api/auth/sign-up
 * - /api/auth/sign-out
 * - /api/auth/session
 * - And all other Better-Auth endpoints
 *
 * The route pattern [...route] catches all paths under /api/auth/*
 *
 * Dynamic import prevents build-time evaluation of auth config.
 * In development, we modify the baseURL dynamically to handle port changes.
 */
export const dynamic = "force-dynamic";

// Cache handlers per baseURL to avoid recreating auth instances
const handlerCache = new Map<string, ReturnType<typeof toNextJsHandler>>();

async function getAuthHandler(request: Request) {
  // In development, detect the actual port from the request
  let baseURL: string;

  if (process.env.NODE_ENV === "development") {
    const origin = new URL(request.url).origin;
    // Only use request origin for localhost (handles dynamic ports like 3001)
    if (origin.startsWith("http://localhost:") || origin.startsWith("http://127.0.0.1:")) {
      baseURL = origin;
    } else {
      // Use default from env for non-localhost
      const { env } = await import("@/lib/auth/config/env");
      baseURL = (env.BETTER_AUTH_URL ?? process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000") as string;
    }
  } else {
    // In production, use the configured baseURL
    const { env } = await import("@/lib/auth/config/env");
    const requestOrigin = new URL(request.url).origin;
    baseURL = (env.BETTER_AUTH_URL ?? process.env.NEXT_PUBLIC_APP_URL ?? requestOrigin) as string;
  }

  // Return cached handler if available
  if (handlerCache.has(baseURL)) {
    return handlerCache.get(baseURL)!;
  }

  // Use the auth instance from server.ts (includes Google OAuth config)
  const { auth } = await import("@/lib/auth/core/server");
  const handler = toNextJsHandler(auth.handler);

  // Cache the handler for this baseURL
  handlerCache.set(baseURL, handler);

  return handler;
}

export async function GET(request: Request) {
  const handler = await getAuthHandler(request);
  return handler.GET(request);
}

export async function POST(request: Request) {
  const handler = await getAuthHandler(request);
  return handler.POST(request);
}
