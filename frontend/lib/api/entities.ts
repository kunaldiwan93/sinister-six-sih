import { apiClient } from "./client";
import { Entity, EntityProfile, GraphData } from "@/types";

export interface EntityFilterParams {
  case_id: string;
  type?: string;
  min_risk?: number;
  search?: string;
  limit?: number;
}

export async function fetchEntities(params: EntityFilterParams): Promise<Entity[]> {
  const query = new URLSearchParams();
  query.append("case_id", params.case_id);
  if (params.type) query.append("type", params.type);
  if (params.min_risk !== undefined) query.append("min_risk", params.min_risk.toString());
  if (params.search) query.append("search", params.search);
  if (params.limit) query.append("limit", params.limit.toString());

  return apiClient<Entity[]>(`/entities?${query.toString()}`);
}

export async function fetchEntityById(id: string): Promise<Entity> {
  return apiClient<Entity>(`/entities/${id}`);
}

export async function fetchEntityProfile(id: string): Promise<EntityProfile> {
  return apiClient<EntityProfile>(`/entities/${id}/profile`);
}

export async function fetchEntityNeighbors(id: string, hops: number = 1): Promise<GraphData> {
  return apiClient<GraphData>(`/entities/${id}/neighbors?hops=${hops}`);
}
