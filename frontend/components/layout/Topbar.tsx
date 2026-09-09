"use client";

import React, { useState, useEffect } from "react";
import { Search, Bell, Shield, CheckCircle2, ChevronDown, FolderGit2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { Case } from "@/types";
import { fetchCases } from "@/lib/api/cases";
import { fetchEntities } from "@/lib/api/entities";

interface TopbarProps {
  currentCaseId: string;
  onCaseChange: (caseId: string) => void;
}

export function Topbar({ currentCaseId, onCaseChange }: TopbarProps) {
  const router = useRouter();
  const [cases, setCases] = useState<Case[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    fetchCases()
      .then((data) => {
        setCases(data);
        if (data.length > 0 && !currentCaseId) {
          onCaseChange(data[0].id);
        }
      })
      .catch(() => {});
  }, [currentCaseId, onCaseChange]);

  // Debounced Global Search
  useEffect(() => {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      setSearchResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const ents = await fetchEntities({
          case_id: currentCaseId,
          search: searchQuery,
          limit: 6,
        });
        setSearchResults(ents);
      } catch {
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 280);

    return () => clearTimeout(timer);
  }, [searchQuery, currentCaseId]);

  const activeCase = cases.find((c) => c.id === currentCaseId) || cases[0];

  return (
    <header className="h-16 border-b border-border bg-surface px-6 flex items-center justify-between sticky top-0 z-20">
      {/* Case Selector */}
      <div className="flex items-center gap-4">
        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-surface-raised border border-border hover:border-nexus-600 text-xs font-mono text-white transition-colors"
          >
            <FolderGit2 className="w-3.5 h-3.5 text-nexus-400" />
            <span className="font-semibold">{activeCase?.name || "Operation Nexus"}</span>
            <span className="px-1.5 py-0.2 rounded bg-slate-800 text-[10px] text-slate-400">
              {activeCase?.case_number || "CAS-2026-NEXUS"}
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-1" />
          </button>

          {showDropdown && (
            <div className="absolute left-0 mt-1 w-64 rounded-md bg-surface-raised border border-border shadow-xl z-50 p-1">
              <div className="px-3 py-1.5 text-[10px] font-mono uppercase text-slate-400 border-b border-border/50">
                Select Active Investigation
              </div>
              {cases.map((c) => (
                <button
                  key={c.id}
                  onClick={() => {
                    onCaseChange(c.id);
                    setShowDropdown(false);
                  }}
                  className={`w-full text-left px-3 py-2 rounded text-xs font-mono flex items-center justify-between transition-colors ${
                    c.id === currentCaseId
                      ? "bg-nexus-900/50 text-nexus-300"
                      : "text-slate-300 hover:bg-surface-hover"
                  }`}
                >
                  <div>
                    <p className="font-semibold">{c.name}</p>
                    <p className="text-[10px] text-slate-400">{c.case_number}</p>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                    {c.status}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="hidden md:flex items-center gap-2 text-xs font-mono text-slate-400">
          <span className="px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-700/50 text-emerald-400 flex items-center gap-1.5 text-[11px]">
            <CheckCircle2 className="w-3 h-3" />
            <span>ONLINE</span>
          </span>
        </div>
      </div>

      {/* Global Search Bar */}
      <div className="relative w-80 lg:w-96">
        <div className="relative flex items-center">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search persons, phones, vehicles, accounts..."
            className="w-full pl-9 pr-4 py-1.5 rounded-md bg-surface-raised border border-border focus:border-nexus-500 focus:outline-none text-xs font-mono text-slate-200 placeholder:text-slate-400 transition-colors"
          />
        </div>

        {/* Autocomplete Results */}
        {searchResults.length > 0 && (
          <div className="absolute left-0 right-0 mt-1 rounded-md bg-surface-raised border border-border shadow-2xl z-50 p-1">
            <div className="px-3 py-1 text-[10px] font-mono uppercase text-slate-400">
              Matching Entities ({searchResults.length})
            </div>
            {searchResults.map((item) => (
              <div
                key={item.id}
                onClick={() => {
                  setSearchQuery("");
                  router.push(`/explorer?highlight=${item.id}`);
                }}
                className="px-3 py-2 rounded hover:bg-surface-hover cursor-pointer flex items-center justify-between text-xs font-mono transition-colors"
              >
                <div>
                  <span className="font-semibold text-white">{item.display_name}</span>
                  <span className="ml-2 text-[10px] px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300">
                    {item.type}
                  </span>
                </div>
                <span className="text-[10px] text-orange-400">Risk: {item.risk_score}/100</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.push("/alerts")}
          className="p-2 rounded-md bg-surface-raised border border-border hover:border-nexus-500 text-slate-300 hover:text-white transition-colors relative"
          title="View Alerts"
        >
          <Bell className="w-4 h-4" />
          <span className="w-2 h-2 rounded-full bg-red-500 absolute top-1.5 right-1.5 animate-pulse" />
        </button>

        <div className="flex items-center gap-2 pl-3 border-l border-border/70">
          <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-mono font-bold text-slate-300">
            AG
          </div>
          <div className="hidden lg:block text-left">
            <p className="text-xs font-medium text-slate-200">Investigator 01</p>
            <p className="text-[10px] font-mono text-slate-400">Special Intel Cell</p>
          </div>
        </div>
      </div>
    </header>
  );
}
