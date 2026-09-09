"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Users,
  Network,
  AlertTriangle,
  Layers,
  ArrowRight,
  TrendingUp,
  Activity,
  ShieldAlert,
  Clock,
  ExternalLink,
  Bot,
  RefreshCw,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { fetchCases, fetchCaseSummary } from "@/lib/api/cases";
import { fetchCaseGraph, fetchCommunities } from "@/lib/api/graph";
import { fetchEntities } from "@/lib/api/entities";
import { fetchAlerts } from "@/lib/api/alerts";
import { fetchTimeline } from "@/lib/api/timeline";
import { KpiCard } from "@/components/common/KpiCard";
import { RiskBadge } from "@/components/common/RiskBadge";
import { EntityBadge } from "@/components/common/EntityBadge";
import { LoadingSkeleton } from "@/components/common/LoadingSkeleton";
import { ErrorState } from "@/components/common/ErrorState";
import { Entity, Alert, TimelineEvent, GraphData } from "@/types";

const COLORS = ["#3b82f6", "#06b6d4", "#f59e0b", "#10b981", "#a855f7", "#64748b"];

export default function Dashboard() {
  const router = useRouter();
  const [caseId, setCaseId] = useState<string>("");
  const [caseInfo, setCaseInfo] = useState<any>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [topEntities, setTopEntities] = useState<Entity[]>([]);
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([]);
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([]);
  const [communityData, setCommunityData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!caseId) {
      fetchCases()
        .then((cases) => {
          if (cases.length > 0) setCaseId(cases[0].id);
        })
        .catch(() => setError("Failed to connect to NEXUS intelligence backend."));
    }
  }, [caseId]);

  useEffect(() => {
    if (!caseId) return;
    setLoading(true);
    setError(null);

    Promise.all([
      fetchCaseSummary(caseId),
      fetchCaseGraph(caseId, 150),
      fetchEntities({ case_id: caseId, limit: 5 }),
      fetchAlerts({ case_id: caseId }),
      fetchTimeline({ case_id: caseId, limit: 5 }),
      fetchCommunities(caseId),
    ])
      .then(([summary, graph, entities, alerts, timeline, communities]) => {
        setCaseInfo(summary);
        setGraphData(graph);
        setTopEntities(entities);
        setRecentAlerts(alerts.slice(0, 5));
        setTimelineEvents(timeline);
        setCommunityData(communities);
      })
      .catch((err) => {
        setError(err.message || "Failed to load case intelligence dashboard.");
      })
      .finally(() => setLoading(false));
  }, [caseId]);

  if (loading) {
    return <LoadingSkeleton text="Synthesizing multi-source intelligence and knowledge graph analytics..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={() => setCaseId(caseId)} />;
  }

  // Calculate entity type chart data
  const entityTypeCounts: Record<string, number> = {};
  graphData?.nodes.forEach((n) => {
    entityTypeCounts[n.type] = (entityTypeCounts[n.type] || 0) + 1;
  });
  const entityDistribution = Object.entries(entityTypeCounts).map(([name, count]) => ({
    name,
    count,
  }));

  // Calculate relationship distribution chart data
  const relTypeCounts: Record<string, number> = {};
  graphData?.edges.forEach((e) => {
    relTypeCounts[e.relationship] = (relTypeCounts[e.relationship] || 0) + 1;
  });
  const relDistribution = Object.entries(relTypeCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([name, count]) => ({
      name: name.replace("_", " "),
      count,
    }));

  const highRiskCount = graphData?.nodes.filter((n) => n.risk_level === "CRITICAL" || n.risk_level === "HIGH").length || 0;

  return (
    <div className="space-y-6 font-mono select-none">
      {/* Investigation Title Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface p-5 rounded-lg border border-border">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-lg font-bold tracking-tight text-white">
              {caseInfo?.case_name || "Operation Nexus"}
            </h1>
            <span className="px-2 py-0.5 rounded bg-nexus-950 border border-nexus-800 text-xs text-nexus-400 font-semibold">
              ACTIVE CASE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-3xl leading-relaxed">
            {caseInfo?.executive_summary ||
              "Trans-national criminal network intelligence and cross-modal entity link analysis."}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => router.push("/explorer")}
            className="px-4 py-2 rounded bg-nexus-600 hover:bg-nexus-500 text-xs font-semibold text-white flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <Network className="w-4 h-4" />
            <span>Open Network Explorer</span>
          </button>
          <button
            onClick={() => router.push("/assistant")}
            className="px-3 py-2 rounded bg-surface-raised hover:bg-surface-hover border border-border text-xs text-slate-200 flex items-center gap-1.5 transition-colors"
          >
            <Bot className="w-4 h-4 text-nexus-400" />
            <span>AI Copilot</span>
          </button>
        </div>
      </div>

      {/* Top KPI Metrics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <KpiCard
          title="Total Entities"
          value={graphData?.metadata.node_count || 0}
          icon={Users}
          subtitle="Multi-modal subjects"
          onClick={() => router.push("/entities")}
        />
        <KpiCard
          title="Relationships"
          value={graphData?.metadata.edge_count || 0}
          icon={Network}
          subtitle="Graph link topology"
          onClick={() => router.push("/explorer")}
        />
        <KpiCard
          title="Flagged Alerts"
          value={recentAlerts.length}
          icon={AlertTriangle}
          variant={recentAlerts.length > 0 ? "danger" : "default"}
          subtitle="Active anomalies"
          onClick={() => router.push("/alerts")}
        />
        <KpiCard
          title="High Risk Nodes"
          value={highRiskCount}
          icon={ShieldAlert}
          variant="warning"
          subtitle="Score >= 60/100"
          onClick={() => router.push("/entities?min_risk=60")}
        />
        <KpiCard
          title="Communities"
          value={communityData?.count || 0}
          icon={Layers}
          subtitle="Detected clusters"
          onClick={() => router.push("/explorer")}
        />
        <KpiCard
          title="Network Density"
          value={(graphData?.metadata.density || 0).toFixed(3)}
          icon={Activity}
          subtitle="Graph connectivity"
        />
      </div>

      {/* Main Grid: Priority Entities & Recent Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* High Priority Entities */}
        <div className="bg-surface rounded-lg border border-border p-5 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-border/70">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-orange-400" />
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                High Priority Investigative Leads
              </span>
            </div>
            <button
              onClick={() => router.push("/entities")}
              className="text-[11px] text-nexus-400 hover:text-nexus-300 flex items-center gap-1"
            >
              <span>View All</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-2">
            {topEntities.map((entity) => (
              <div
                key={entity.id}
                onClick={() => router.push(`/explorer?highlight=${entity.id}`)}
                className="p-3 rounded bg-surface-raised hover:bg-surface-hover border border-border/70 cursor-pointer flex items-center justify-between transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-xs">{entity.display_name}</span>
                    <EntityBadge type={entity.type} />
                  </div>
                  <p className="text-[10px] text-slate-400">
                    Betweenness: {entity.betweenness_centrality?.toFixed(3) || "0.000"} | PageRank: {entity.pagerank_score?.toFixed(3) || "0.000"}
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <RiskBadge level={entity.risk_level} score={entity.risk_score} />
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Anomalies & Alerts */}
        <div className="bg-surface rounded-lg border border-border p-5 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-border/70">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Recent Network Anomalies
              </span>
            </div>
            <button
              onClick={() => router.push("/alerts")}
              className="text-[11px] text-nexus-400 hover:text-nexus-300 flex items-center gap-1"
            >
              <span>View All</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-2">
            {recentAlerts.map((alert) => (
              <div
                key={alert.id}
                onClick={() => router.push("/alerts")}
                className="p-3 rounded bg-surface-raised hover:bg-surface-hover border border-border/70 cursor-pointer space-y-1.5 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-white truncate max-w-xs">{alert.title}</span>
                  <span
                    className={`text-[9px] px-2 py-0.2 rounded font-bold border ${
                      alert.severity === "CRITICAL"
                        ? "bg-red-950 text-red-300 border-red-700"
                        : "bg-orange-950 text-orange-300 border-orange-700"
                    }`}
                  >
                    {alert.severity}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-1">{alert.explanation}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Analytical Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Entity Distribution Chart */}
        <div className="bg-surface rounded-lg border border-border p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              Entity Type Breakdown
            </span>
            <span className="text-[10px] text-slate-400">{graphData?.nodes.length} total</span>
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={entityDistribution}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0c121e", borderColor: "#1f2e4a", fontSize: "11px" }}
                />
                <Bar dataKey="count" fill="#38a5f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Relationship Distribution Chart */}
        <div className="bg-surface rounded-lg border border-border p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              Dominant Relationship Types
            </span>
            <span className="text-[10px] text-slate-400">{graphData?.edges.length} total</span>
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={relDistribution} layout="vertical">
                <XAxis type="number" stroke="#64748b" fontSize={10} />
                <YAxis type="category" dataKey="name" stroke="#64748b" fontSize={10} width={120} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0c121e", borderColor: "#1f2e4a", fontSize: "11px" }}
                />
                <Bar dataKey="count" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
