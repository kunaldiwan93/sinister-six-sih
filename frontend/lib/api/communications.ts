import { apiClient } from "./client";
import { Communication } from "@/types";

export interface CommunicationFilterParams {
  case_id: string;
  is_anomalous?: boolean;
  phone?: string;
  limit?: number;
}

export async function fetchCommunications(params: CommunicationFilterParams): Promise<Communication[]> {
  const query = new URLSearchParams();
  query.append("case_id", params.case_id);
  if (params.is_anomalous !== undefined) query.append("is_anomalous", params.is_anomalous.toString());
  if (params.phone) query.append("phone", params.phone);
  if (params.limit) query.append("limit", params.limit.toString());

  return apiClient<Communication[]>(`/communications?${query.toString()}`);
}
