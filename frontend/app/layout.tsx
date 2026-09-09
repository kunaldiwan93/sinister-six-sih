"use client";

import React, { useState } from "react";
import "./globals.css";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 1000 * 60 * 3, // 3 minutes
    },
  },
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [currentCaseId, setCurrentCaseId] = useState<string>("");

  return (
    <html lang="en" className="dark">
      <head>
        <title>NEXUS — AI Criminal Network Intelligence Platform</title>
        <meta
          name="description"
          content="AI-powered criminal network analysis and investigation intelligence system combining NLP, knowledge graphs, and anomaly detection."
        />
      </head>
      <body className="bg-background text-slate-200 antialiased h-screen overflow-hidden flex">
        <QueryClientProvider client={queryClient}>
          <Sidebar />
          <div className="flex-1 flex flex-col h-screen overflow-hidden">
            <Topbar currentCaseId={currentCaseId} onCaseChange={setCurrentCaseId} />
            <main className="flex-1 overflow-y-auto bg-background p-6">
              {children}
            </main>
          </div>
        </QueryClientProvider>
      </body>
    </html>
  );
}
