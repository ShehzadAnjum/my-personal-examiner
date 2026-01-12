import { ReactNode } from "react";
import { DashboardHeader } from "@/components/layout/DashboardHeader";

export default function DashboardLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <DashboardHeader />
      {/* Main content area - fully scrollable */}
      <main className="flex-1">{children}</main>
    </div>
  );
}
