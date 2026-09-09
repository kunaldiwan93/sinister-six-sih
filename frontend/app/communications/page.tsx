"use client";

import React, { useEffect, useState } from "react";
import { PhoneCall, Search, AlertTriangle, ShieldCheck } from "lucide-react";
import { fetchCases } from "@/lib/api/cases";
import { fetchCommunications } from "@/lib/api/communications";
import { LoadingSkeleton } from "@/components/common/LoadingSkeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { Communication } from "@/types";

export default function CommunicationsPage() {
  const [caseId, setCaseId] = useState<string>("");
  const [comms, setComms] = useState<Communication[]>([]);
  const [anomalyOnly, setAnomalyOnly] = useState(false);
  const [searchPhone, setSearchPhone] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!caseId) {
      fetchCases().then((cases) => {
        if (cases.length > 0) setCaseId(cases[0].id);
      });
    }
  }, [caseId]);

  useEffect(() => {
    if (!caseId) return;
    setLoading(true);
    fetchCommunications({
      case_id: caseId,
      is_anomalous: anomalyOnly ? true : undefined,
      phone: searchPhone.trim() || undefined,
      limit: 100,
    })
      .then((data) => setComms(data))
      .catch(() => setComms([]))
      .finally(() => setLoading(false));
  }, [caseId, anomalyOnly, searchPhone]);

  return (
    <div className="space-y-4 font-mono select-none">
      {/* Header & Controls */}
      <div className="p-4 rounded-lg bg-surface border border-border flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h1 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <PhoneCall className="w-4 h-4 text-cyan-400" />
            <span>Call Detail Records (CDR) & Communication Bursts</span>
          </h1>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Communication frequency, duration analysis, and late-night burst detection ({comms.length} records)
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative w-48">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            <input
              type="text"
              value={searchPhone}
              onChange={(e) => setSearchPhone(e.target.value)}
              placeholder="Search phone number..."
              className="w-full pl-8 pr-3 py-1.5 rounded bg-surface-raised border border-border text-xs text-white placeholder:text-slate-500"
            />
          </div>

          <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={anomalyOnly}
              onChange={(e) => setAnomalyOnly(e.target.checked)}
              className="accent-orange-500 rounded"
            />
            <span className="text-orange-400 font-semibold">Flagged Bursts Only</span>
          </label>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-lg bg-surface border border-border overflow-hidden">
        {loading ? (
          <div className="p-8">
            <LoadingSkeleton text="Loading CDR communications..." />
          </div>
        ) : comms.length === 0 ? (
          <div className="p-8">
            <EmptyState title="No Communications Found" description="No CDR records matched the filter criteria." />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-surface-raised/80 border-b border-border text-[10px] text-slate-400 uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3">Timestamp</th>
                  <th className="px-4 py-3">Caller Phone</th>
                  <th className="px-4 py-3">Receiver Phone</th>
                  <th className="px-4 py-3">Duration</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Anomaly Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {comms.map((c) => (
                  <tr
                    key={c.id}
                    className={`hover:bg-surface-hover/70 transition-colors ${
                      c.is_anomalous ? "bg-orange-950/20" : ""
                    }`}
                  >
                    <td className="px-4 py-3 text-slate-400 text-[11px]">
                      {new Date(c.timestamp).toLocaleString("en-US", {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-bold text-white">{c.caller_phone}</div>
                      {c.caller_name && <div className="text-[10px] text-slate-500">{c.caller_name}</div>}
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-bold text-white">{c.receiver_phone}</div>
                      {c.receiver_name && <div className="text-[10px] text-slate-500">{c.receiver_name}</div>}
                    </td>
                    <td className="px-4 py-3 text-slate-200">
                      {Math.floor(c.duration_seconds / 60)}m {c.duration_seconds % 60}s
                    </td>
                    <td className="px-4 py-3">
                      {c.is_anomalous ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-orange-950 border border-orange-700 text-orange-300">
                          <AlertTriangle className="w-3 h-3" />
                          BURST FLAGGED
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] bg-emerald-950 border border-emerald-800 text-emerald-400">
                          <ShieldCheck className="w-3 h-3" />
                          STANDARD
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-[11px] text-slate-400 max-w-xs truncate">
                      {c.anomaly_reason || "Normal calling pattern"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
