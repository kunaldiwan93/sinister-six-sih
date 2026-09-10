import { apiClient } from "./client";
import { Transaction } from "@/types";

export interface TransactionFilterParams {
  case_id: string;
  is_anomalous?: boolean;
  min_amount?: number;
  account?: string;
  limit?: number;
}

export async function fetchTransactions(params: TransactionFilterParams): Promise<Transaction[]> {
  const query = new URLSearchParams();
  query.append("case_id", params.case_id);
  if (params.is_anomalous !== undefined) query.append("is_anomalous", params.is_anomalous.toString());
  if (params.min_amount !== undefined) query.append("min_amount", params.min_amount.toString());
  if (params.account) query.append("account", params.account);
  if (params.limit) query.append("limit", params.limit.toString());

  return apiClient<Transaction[]>(`/transactions?${query.toString()}`);
}
