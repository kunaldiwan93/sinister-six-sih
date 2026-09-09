"use client";

import React, { useEffect, useState } from "react";
import { X, ShieldAlert, Network, ArrowRight, Bot, Phone, Car, MapPin, CreditCard, Activity } from "lucide-react";
import { useRouter } from "next/navigation";
import { Entity, EntityProfile } from "@/types";
import { fetchEntityProfile } from "@/lib/api/entities";
import { RiskBadge } from "@/components/common/RiskBadge";
import { EntityBadge } from "@/components/common/EntityBadge";
import { LoadingSkeleton } from "@/components/common/LoadingSkeleton";

interface EntityPanelProps {
  entityId: string | null;
  onClose: () => void;
}

export function EntityPanel({ entityId, onClose }: EntityPanelProps) {
  const router = useRouter();
  const [profile, setProfile] = useState<EntityProfile | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!entityId) {
      setProfile(null);
      return;
    }

    setLoading(true);
    fetchEntityProfile(entityId)
      .then((data) => setProfile(data))
      .catch(() => setProfile(null))
      .finally(() => setLoading(false));
  }, [entityId]);

  if (!entityId) return null;

  return (
    <div className="w-96 bg-surface/98 backdrop-blur border-l border-border h-full flex flex-col shadow-2xl z-20 overflow-hidden select-none">
      {/* Drawer Header */}
      <div className="p-4 border-b border-border flex items-center justify-between bg-surface-raised/40">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-nexus-400" />
          <span className="text-xs font-mono font-bold tracking-wider text-white">
            ENTITY INTELLIGENCE PROFILE
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-surface-hover text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-xs">
        {loading ? (
          <LoadingSkeleton text="Retrieving multi-modal intelligence profile..." />
        ) : profile ? (
          <>
            {/* Identity Card */}
            <div className="p-3.5 rounded-lg bg-surface-raised border border-border">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-sm font-bold text-white tracking-tight">
                    {profile.entity.display_name}
                  </h2>
                  <p className="text-[10px] text-slate-400 mt-0.5">
                    Canonical ID: {profile.entity.canonical_name}
                  </p>
                </div>
                <EntityBadge type={profile.entity.type} />
              </div>

              <div className="mt-3 flex items-center justify-between pt-2 border-t border-border/50">
                <span className="text-[11px] text-slate-400">Risk Indicator:</span>
                <RiskBadge
                  level={profile.entity.risk_level}
                  score={profile.entity.risk_score}
                />
              </div>

              {profile.entity.aliases && profile.entity.aliases.length > 0 && (
                <div className="mt-2 text-[10px] text-slate-400">
                  <span className="text-slate-400">Known Aliases: </span>
                  <span className="text-slate-300">{profile.entity.aliases.join(", ")}</span>
                </div>
              )}
            </div>

            {/* Why is this Entity Flagged? */}
            <div className="p-3.5 rounded-lg bg-red-950/20 border border-red-900/40">
              <div className="flex items-center gap-1.5 text-red-400 font-semibold mb-2">
                <ShieldAlert className="w-4 h-4" />
                <span>Key Measurable Indicators</span>
              </div>
              <ul className="space-y-1.5 text-[11px] text-slate-300">
                {profile.risk_reasons.map((reason, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="text-red-400 shrink-0">•</span>
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Network Analytics Metrics */}
            <div className="p-3.5 rounded-lg bg-surface-raised border border-border">
              <div className="flex items-center gap-1.5 text-nexus-400 font-semibold mb-2.5">
                <Network className="w-4 h-4" />
                <span>Graph Centrality & Topology</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className="p-2 rounded bg-surface border border-border/60">
                  <p className="text-[10px] text-slate-400">Betweenness (Bridge)</p>
                  <p className="font-bold text-white text-xs mt-0.5">
                    {profile.metrics.betweenness.toFixed(3)}
                  </p>
                </div>
                <div className="p-2 rounded bg-surface border border-border/60">
                  <p className="text-[10px] text-slate-400">PageRank (Influence)</p>
                  <p className="font-bold text-white text-xs mt-0.5">
                    {profile.metrics.pagerank.toFixed(3)}
                  </p>
                </div>
                <div className="p-2 rounded bg-surface border border-border/60">
                  <p className="text-[10px] text-slate-400">Degree Centrality</p>
                  <p className="font-bold text-white text-xs mt-0.5">
                    {profile.metrics.degree.toFixed(2)}
                  </p>
                </div>
                <div className="p-2 rounded bg-surface border border-border/60">
                  <p className="text-[10px] text-slate-400">Cluster / Community</p>
                  <p className="font-bold text-nexus-300 text-xs mt-0.5">
                    Community {profile.metrics.community_id}
                  </p>
                </div>
              </div>
            </div>

            {/* Direct Connections */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-slate-300 font-semibold">
                <span>Associated Connections ({profile.associated_entities.length})</span>
              </div>
              <div className="space-y-1.5 max-h-44 overflow-y-auto pr-1">
                {profile.associated_entities.map((assoc, idx) => (
                  <div
                    key={idx}
                    className="p-2 rounded bg-surface-raised border border-border/60 flex items-center justify-between text-[11px]"
                  >
                    <div>
                      <span className="font-semibold text-white">
                        {assoc.connected_entity_name}
                      </span>
                      <p className="text-[10px] text-slate-400">
                        {assoc.relationship_type} ({assoc.direction.toLowerCase()})
                      </p>
                    </div>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-900 text-slate-400">
                      {(assoc.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Action Bar */}
            <div className="pt-2">
              <button
                onClick={() =>
                  router.push(`/assistant?query=Why is ${profile.entity.display_name} considered high risk?`)
                }
                className="w-full py-2 px-3 rounded bg-nexus-600 hover:bg-nexus-500 text-white font-medium flex items-center justify-center gap-2 transition-colors shadow-sm"
              >
                <Bot className="w-4 h-4" />
                <span>Ask AI Assistant About Subject</span>
              </button>
            </div>
          </>
        ) : (
          <p className="text-center text-slate-400 py-10">Entity not found.</p>
        )}
      </div>
    </div>
  );
}
