import { apiClient } from "./client";
import { GraphData, ShortestPathResult } from "@/types";

export async function fetchCaseGraph(caseId: string, limit: number = 300): Promise<GraphData> {
  return apiClient<GraphData>(`/cases/${caseId}/graph?limit=${limit}`);
}

export async function findShortestPath(caseId: string, sourceId: string, targetId: string): Promise<ShortestPathResult> {
  return apiClient<ShortestPathResult>("/graph/shortest-path", {
    method: "POST",
    body: JSON.stringify({
      case_id: caseId,
      source_id: sourceId,
      target_id: targetId,
    }),
  });
}

export async function filterGraph(payload: {
  case_id: string;
  entity_types?: string[];
  relationship_types?: string[];
  min_risk_score?: number;
  community_id?: number;
  search_query?: string;
  limit?: number;
}): Promise<GraphData> {
  return apiClient<GraphData>("/graph/filter", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchCommunities(caseId: string) {
  return apiClient<any>(`/communities?case_id=${caseId}`);
}

export async function fetchGraphMetrics(caseId: string) {
  return apiClient<any>(`/cases/${caseId}/metrics`);
}
