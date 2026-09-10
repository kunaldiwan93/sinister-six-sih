import { apiClient } from "./client";
import { TimelineEvent } from "@/types";

export interface TimelineFilterParams {
  case_id: string;
  event_type?: string;
  severity?: string;
  entity_id?: string;
  limit?: number;
}

export async function fetchTimeline(params: TimelineFilterParams): Promise<TimelineEvent[]> {
  const query = new URLSearchParams();
  query.append("case_id", params.case_id);
  if (params.event_type) query.append("event_type", params.event_type);
  if (params.severity) query.append("severity", params.severity);
  if (params.entity_id) query.append("entity_id", params.entity_id);
  if (params.limit) query.append("limit", params.limit.toString());

  return apiClient<TimelineEvent[]>(`/timeline?${query.toString()}`);
}
