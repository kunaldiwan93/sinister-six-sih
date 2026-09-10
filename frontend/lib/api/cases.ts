import { apiClient } from "./client";
import { Case } from "@/types";

export async function fetchCases(): Promise<Case[]> {
  return apiClient<Case[]>("/cases");
}

export async function fetchCaseById(id: string): Promise<Case> {
  return apiClient<Case>(`/cases/${id}`);
}

export async function fetchCaseSummary(id: string) {
  return apiClient<any>(`/cases/${id}/summary`);
}

export async function createCase(data: { case_number: string; name: string; description?: string }) {
  return apiClient<Case>("/cases", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
