"use client";

import React, { useEffect, useState } from "react";
import { AlertTriangle, Filter } from "lucide-react";
import { fetchCases } from "@/lib/api/cases";
import { fetchAlerts } from "@/lib/api/alerts";
import { AlertCard } from "@/components/alerts/AlertCard";
import { LoadingSkeleton } from "@/components/common/LoadingSkeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { Alert } from "@/types";

export default function AlertsPage() {
  const [caseId, setCaseId] = useState<string>("");
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [categoryFilter, setCategoryFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!caseId) {
      fetchCases().then((cases) => {
        if (cases.length > 0) setCaseId(cases[0].id);
      });
    }
  }, [caseId]);

  const loadAlerts = () => {
    if (!caseId) return;
    setLoading(true);
    fetchAlerts({
      case_id: caseId,
      severity: severityFilter !== "ALL" ? severityFilter : undefined,
      category: categoryFilter !== "ALL" ? categoryFilter : undefined,
      status: statusFilter !== "ALL" ? statusFilter : undefined,
    })
      .then((data) => setAlerts(data))
      .catch(() => setAlerts([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAlerts();
  }, [caseId, severityFilter, categoryFilter, statusFilter]);

  return (
    <div className="space-y-4 font-mono select-none">
      {/* Header & Filter Controls */}
      <div className="p-4 rounded-lg bg-surface border border-border flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h1 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <span>Risk Indicators & Anomaly Alert Engine</span>
          </h1>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Automated alerts backed by Isolation Forest, bridge node metrics, and cross-modal evidence ({alerts.length} alerts)
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded bg-surface-raised border border-border text-xs text-slate-200"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium / Moderate</option>
            <option value="LOW">Low</option>
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded bg-surface-raised border border-border text-xs text-slate-200"
          >
            <option value="ALL">All Categories</option>
            <option value="TRANSACTION_ANOMALY">Transaction Anomaly</option>
            <option value="COMMUNICATION_ANOMALY">Communication Burst</option>
            <option value="BRIDGE_NODE">Bridge Node / Intermediary</option>
            <option value="SHARED_IDENTIFIER">Shared Infrastructure</option>
            <option value="UNUSUAL_LOCATION_ACTIVITY">Cross-Network Location</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded bg-surface-raised border border-border text-xs text-slate-200"
          >
            <option value="ALL">All Statuses</option>
            <option value="NEW">New</option>
            <option value="REVIEWED">Reviewed</option>
            <option value="DISMISSED">Dismissed</option>
          </select>
        </div>
      </div>

      {/* Alerts Grid */}
      {loading ? (
        <LoadingSkeleton text="Loading investigation alerts..." />
      ) : alerts.length === 0 ? (
        <EmptyState title="No Active Alerts" description="No alerts match the selected severity and category filters." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {alerts.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onStatusChange={() => loadAlerts()}
            />
          ))}
        </div>
      )}
    </div>
  );
}
