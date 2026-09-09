"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { fetchCases } from "@/lib/api/cases";
import { fetchCaseGraph } from "@/lib/api/graph";
import { GraphViewer } from "@/components/graph/GraphViewer";
import { EntityPanel } from "@/components/entities/EntityPanel";
import { LoadingSkeleton } from "@/components/common/LoadingSkeleton";
import { ErrorState } from "@/components/common/ErrorState";
import { GraphData, GraphNode, GraphEdge } from "@/types";

function ExplorerContent({ currentCaseId }: { currentCaseId?: string }) {
  const searchParams = useSearchParams();
  const highlightParam = searchParams.get("highlight");

  const [caseId, setCaseId] = useState<string>(currentCaseId || "");
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!caseId) {
      fetchCases()
        .then((cases) => {
          if (cases.length > 0) setCaseId(cases[0].id);
        })
        .catch(() => setError("Failed to retrieve cases."));
    }
  }, [caseId]);

  useEffect(() => {
    if (!caseId) return;
    setLoading(true);
    fetchCaseGraph(caseId, 300)
      .then((data) => {
        setGraphData(data);
        if (highlightParam) {
          const match = data.nodes.find((n) => n.id === highlightParam);
          if (match) setSelectedNode(match);
        }
      })
      .catch((err) => setError(err.message || "Failed to load network topology."))
      .finally(() => setLoading(false));
  }, [caseId, highlightParam]);

  if (loading) {
    return <LoadingSkeleton text="Rendering interactive Cytoscape knowledge graph..." className="h-[80vh]" />;
  }

  if (error || !graphData) {
    return <ErrorState message={error || "Graph data unavailable"} onRetry={() => setCaseId(caseId)} />;
  }

  return (
    <div className="relative h-[calc(100vh-7rem)] w-full rounded-lg border border-border overflow-hidden flex">
      {/* Cytoscape Graph Canvas */}
      <div className="flex-1 h-full relative">
        <GraphViewer
          data={graphData}
          caseId={caseId}
          onSelectNode={(node) => setSelectedNode(node)}
          onSelectEdge={(edge) => setSelectedEdge(edge)}
          highlightedNodeId={highlightParam || selectedNode?.id}
        />
      </div>

      {/* Slide-over Entity Intelligence Drawer */}
      {selectedNode && (
        <EntityPanel
          entityId={selectedNode.id}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </div>
  );
}

export default function ExplorerPage() {
  return (
    <Suspense fallback={<LoadingSkeleton text="Loading Network Explorer..." className="h-[80vh]" />}>
      <ExplorerContent />
    </Suspense>
  );
}
