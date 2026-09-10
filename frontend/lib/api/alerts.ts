import { apiClient } from "./client";
import { Alert } from "@/types";

export interface AlertFilterParams {
  case_id: string;
  severity?: string;
  category?: string;
  status?: string;
}

export async function fetchAlerts(params: AlertFilterParams): Promise<Alert[]> {
  const query = new URLSearchParams();
  query.append("case_id", params.case_id);
  if (params.severity) query.append("severity", params.severity);
  if (params.category) query.append("category", params.category);
  if (params.status) query.append("status", params.status);

  return apiClient<Alert[]>(`/alerts?${query.toString()}`);
}

export async function updateAlertStatus(alertId: string, status: string, explanation?: string): Promise<Alert> {
  return apiClient<Alert>(`/alerts/${alertId}`, {
    method: "PATCH",
    body: JSON.stringify({ status, explanation }),
  });
}
