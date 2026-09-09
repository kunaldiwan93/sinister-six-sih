"use client";

import React, { useEffect, useState } from "react";
import { Activity, RefreshCw, CheckCircle2, Play } from "lucide-react";
import { fetchCases } from "@/lib/api/cases";
import { fetchAnalysisRuns, triggerPipelineAnalysis } from "@/lib/api/analysis";
import { LoadingSkeleton } from "@/components/common/LoadingSkeleton";
import { AnalysisRun } from "@/types";

export default function AnalysisPage() {
  const [caseId, setCaseId] = useState<string>("");
  const [runs, setRuns] = useState<AnalysisRun[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!caseId) {
      fetchCases().then((cases) => {
        if (cases.length > 0) setCaseId(cases[0].id);
      });
    }
  }, [caseId]);

  const loadRuns = () => {
    if (!caseId) return;
    fetchAnalysisRuns(caseId)
      .then((data) => setRuns(data))
      .catch(() => {});
  };

  useEffect(() => {
    loadRuns();
  }, [caseId]);

  const handleRunAnalysis = async () => {
    if (!caseId || isAnalyzing) return;
    setIsAnalyzing(true);
    setSuccessMsg(null);
    try {
      const res = await triggerPipelineAnalysis(caseId);
      setSuccessMsg(res.message || "Pipeline analysis executed successfully.");
      loadRuns();
    } catch {
      setSuccessMsg("Analysis run failed.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6 font-mono select-none">
      <div className="p-4 rounded-lg bg-surface border border-border flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h1 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Activity className="w-4 h-4 text-nexus-400" />
            <span>Analysis Pipeline Runs & Graph Recalculation</span>
          </h1>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Audit trail of network analytics, centrality recalculations, community detections, and anomaly runs.
          </p>
        </div>

        <button
          onClick={handleRunAnalysis}
          disabled={isAnalyzing}
          className="px-4 py-2 rounded bg-nexus-600 hover:bg-nexus-500 disabled:opacity-50 text-white font-semibold text-xs flex items-center gap-1.5 transition-colors shadow-sm"
        >
          {isAnalyzing ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Executing Pipeline...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Trigger Full Analysis Pipeline</span>
            </>
          )}
        </button>
      </div>

      {successMsg && (
        <div className="p-3 rounded bg-emerald-950/40 border border-emerald-800 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Analysis Runs Table */}
      <div className="rounded-lg bg-surface border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-raised/80 border-b border-border text-[10px] text-slate-400 uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3">Run ID</th>
                <th className="px-4 py-3">Pipeline Type</th>
                <th className="px-4 py-3">Started At</th>
                <th className="px-4 py-3">Duration</th>
                <th className="px-4 py-3">Entities Processed</th>
                <th className="px-4 py-3">Alerts Generated</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {runs.map((r) => (
                <tr key={r.id} className="hover:bg-surface-hover/70 transition-colors">
                  <td className="px-4 py-3 font-mono text-[10px] text-slate-400">
                    {r.id.substring(0, 8)}...
                  </td>
                  <td className="px-4 py-3 font-bold text-white">{r.run_type}</td>
                  <td className="px-4 py-3 text-slate-400 text-[11px]">
                    {new Date(r.started_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-slate-300">{r.duration_seconds}s</td>
                  <td className="px-4 py-3 text-nexus-400 font-bold">{r.entities_extracted}</td>
                  <td className="px-4 py-3 text-red-400 font-bold">{r.alerts_generated}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        r.status === "COMPLETED"
                          ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                          : r.status === "PROCESSING"
                          ? "bg-blue-950 text-blue-400 border border-blue-800"
                          : "bg-red-950 text-red-400 border border-red-800"
                      }`}
                    >
                      {r.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
