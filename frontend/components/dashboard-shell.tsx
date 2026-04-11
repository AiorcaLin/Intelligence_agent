"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { NavSidebar } from "@/components/nav-sidebar";
import { isAuthenticated } from "@/lib/auth";

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    }
  }, [router]);

  return (
    <div className="flex h-screen overflow-hidden">
      <NavSidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto px-4 py-6 lg:px-8 lg:py-8 max-w-7xl">
          {children}
        </div>
      </main>
    </div>
  );
}
