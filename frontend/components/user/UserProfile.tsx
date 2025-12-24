"use client";

import { useState, useEffect } from "react";
import { authClient } from "@/lib/auth/core/client";

interface User {
  id: string;
  email: string;
  name?: string;
  image?: string;
}

export function UserProfile() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const session = await authClient.getSession();
      console.log('🔍 Full session:', session); // Debug full session
      console.log('🔍 Session user:', session?.data?.user); // Debug user

      if (session?.data?.user) {
        const userData = session.data.user;
        // Extract image from various possible locations
        const userImage = userData.image || userData.picture || undefined;

        console.log('📸 User image found:', userImage);

        setUser({
          id: userData.id,
          email: userData.email || "",
          name: userData.name || undefined,
          image: userImage,
        });
      }
    } catch (error) {
      console.error("Error loading user:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      // Sign out from Better Auth
      await authClient.signOut();

      // Clear any local state
      setUser(null);

      // Force a hard redirect to login page to clear any cached state
      // Using window.location ensures a full page reload and clears all cookies/cache
      window.location.href = "/login";
    } catch (error) {
      console.error("Error signing out:", error);
      // Even if signOut fails, redirect to login
      window.location.href = "/login";
    } finally {
      setIsLoggingOut(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2">
        <div className="h-8 w-8 rounded-full bg-gray-300 animate-pulse" />
        <div className="h-4 w-20 bg-gray-300 animate-pulse rounded" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="flex items-center gap-3">
      {/* User Avatar */}
      {user.image ? (
        <img
          src={user.image}
          alt={user.name || user.email}
          className="h-8 w-8 rounded-full border-2 border-gray-400"
        />
      ) : (
        <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold text-sm border-2 border-gray-400">
          {(user.name || user.email || "U").charAt(0).toUpperCase()}
        </div>
      )}

      {/* User Name/Email */}
      <div className="flex flex-col">
        <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
          {user.name || user.email.split("@")[0]}
        </span>
        <span className="text-xs text-gray-600 dark:text-gray-400">{user.email}</span>
      </div>

      {/* Logout Button */}
      <button
        onClick={handleLogout}
        disabled={isLoggingOut}
        className="px-3 py-1.5 text-sm font-semibold text-red-600 dark:text-red-400 hover:text-white hover:bg-red-600 dark:hover:bg-red-500 rounded-md border border-red-400 dark:border-red-500 disabled:opacity-50 transition-colors"
      >
        {isLoggingOut ? "Logging out..." : "Logout"}
      </button>
    </div>
  );
}
