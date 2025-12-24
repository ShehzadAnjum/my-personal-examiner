import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { SignJWT } from "jose";
import { auth } from "@/lib/auth/core/server";

/**
 * API route to get JWT token from Better Auth session
 *
 * Better Auth stores sessions in httpOnly cookies. This route:
 * 1. Validates the Better Auth session
 * 2. Generates a JWT token with the user ID for the FastAPI backend
 * 3. Returns the token to the client for API requests
 */
export async function GET() {
  try {
    const cookieStore = await cookies();
    const session = await auth.api.getSession({
      headers: new Headers({
        cookie: cookieStore.toString(),
      }),
    });

    if (!session?.user) {
      return NextResponse.json(
        { error: "Not authenticated" },
        { status: 401 }
      );
    }

    // Get BETTER_AUTH_SECRET from environment
    const secret = process.env.BETTER_AUTH_SECRET;
    if (!secret) {
      console.error("BETTER_AUTH_SECRET not configured");
      return NextResponse.json(
        { error: "Server configuration error" },
        { status: 500 }
      );
    }

    const secretKey = new TextEncoder().encode(secret);

    // Create JWT with user ID (Better Auth uses string IDs)
    const token = await new SignJWT({
      sub: session.user.id, // Standard JWT subject claim
      userId: session.user.id, // Also include userId for backend compatibility
      user_id: session.user.id, // Alternative key
      email: session.user.email,
    })
      .setProtectedHeader({ alg: "HS256" })
      .setIssuedAt()
      .setExpirationTime("7d") // Token expires in 7 days
      .sign(secretKey);

    return NextResponse.json({ token });
  } catch (error) {
    console.error("Error getting token:", error);
    return NextResponse.json(
      { error: "Failed to get token" },
      { status: 500 }
    );
  }
}
