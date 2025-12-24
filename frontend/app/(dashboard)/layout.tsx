import { ReactNode } from "react";
import { UserProfile } from "@/components/user/UserProfile";
import { ThemeToggle } from "@/components/theme-toggle";
import { BookOpen } from "lucide-react";
import Link from "next/link";

export default function DashboardLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Sticky Header - Modern gradient with glassmorphism */}
      <nav className="sticky top-0 z-50 h-16 bg-card/80 backdrop-blur-md border-b border-border shadow-sm">
        <div className="h-full px-4 lg:px-8 flex items-center justify-between">
          <Link
            href="/teaching"
            className="flex items-center gap-3 hover:opacity-80 transition-opacity cursor-pointer"
          >
            <div className="p-2 bg-primary/10 rounded-lg">
              <BookOpen className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-foreground">
                My Personal Examiner
              </h1>
              <p className="text-xs text-muted-foreground">Economics 9708 A-Level</p>
            </div>
          </Link>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <UserProfile />
          </div>
        </div>
      </nav>
      {/* Main content area - fully scrollable */}
      <main className="flex-1">{children}</main>
    </div>
  );
}
