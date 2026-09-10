import { apiClient } from "./client";
import { AnalysisRun } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function fetchAnalysisRuns(caseId?: string): Promise<AnalysisRun[]> {
  const query = caseId ? `?case_id=${caseId}` : "";
  return apiClient<AnalysisRun[]>(`/analysis-runs${query}`);
}

export async function uploadDocument(caseId: string, file: File, title?: string, docType: string = "FIR") {
  const formData = new FormData();
  formData.append("file", file);
  if (title) formData.append("title", title);
  formData.append("doc_type", docType);

  const res = await fetch(`${API_BASE_URL}/cases/${caseId}/documents`, {
    method: "POST",
    body: formData,
  });
  const json = await res.json();
  if (!res.ok || !json.success) {
    throw new Error(json.error?.message || "Upload failed");
  }
  return json.data;
}

export async function uploadCdrCsv(caseId: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/cases/${caseId}/cdr`, {
    method: "POST",
    body: formData,
  });
  const json = await res.json();
  if (!res.ok || !json.success) {
    throw new Error(json.error?.message || "CDR upload failed");
  }
  return json.data;
}

export async function uploadTransactionCsv(caseId: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/cases/${caseId}/transactions`, {
    method: "POST",
    body: formData,
  });
  const json = await res.json();
  if (!res.ok || !json.success) {
    throw new Error(json.error?.message || "Transaction upload failed");
  }
  return json.data;
}

export async function triggerPipelineAnalysis(caseId: string) {
  return apiClient<any>(`/cases/${caseId}/analyze`, {
    method: "POST",
  });
}
