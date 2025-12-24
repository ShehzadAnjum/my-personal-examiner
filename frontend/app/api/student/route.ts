import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { auth } from "@/lib/auth/core/server";

/**
 * API route to get or create a student record for the current better-auth user
 *
 * This endpoint:
 * 1. Validates the Better Auth session
 * 2. Checks if a Student exists in the backend with this email
 * 3. If not, creates one
 * 4. Returns the student_id for use in API requests
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

    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    // Try to find existing student by email
    try {
      const response = await fetch(`${backendUrl}/api/auth/student-by-email?email=${encodeURIComponent(session.user.email)}`, {
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const student = await response.json();
        return NextResponse.json({ student_id: student.id });
      }

      // If 404, student doesn't exist, create one
      if (response.status === 404) {
        // Create new student
        const createResponse = await fetch(`${backendUrl}/api/auth/register`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: session.user.email,
            password: `better-auth-${session.user.id}-${Date.now()}`, // Random password since auth is handled by better-auth
            full_name: session.user.name || session.user.email.split("@")[0],
          }),
        });

        if (!createResponse.ok) {
          const error = await createResponse.json();
          console.error("Failed to create student:", error);
          return NextResponse.json(
            { error: "Failed to create student record" },
            { status: 500 }
          );
        }

        const newStudent = await createResponse.json();
        return NextResponse.json({ student_id: newStudent.id });
      }

      throw new Error(`Unexpected response: ${response.status}`);
    } catch (error) {
      console.error("Error fetching/creating student:", error);
      return NextResponse.json(
        { error: "Failed to get student record" },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error("Error in student route:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
