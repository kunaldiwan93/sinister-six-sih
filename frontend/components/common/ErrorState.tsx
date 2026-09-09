import React from "react";
import { AlertTriangle } from "lucide-react";

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({
  message = "Failed to load requested intelligence data.",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="w-full rounded-lg border border-red-900/50 bg-red-950/20 p-6 flex flex-col items-center justify-center text-center">
      <div className="p-3 rounded-full bg-red-950 border border-red-800 text-red-400 mb-3">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-red-200">System Error</h3>
      <p className="mt-1 text-xs text-red-300 max-w-sm">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 px-3 py-1.5 rounded bg-red-900/60 hover:bg-red-800 border border-red-700/60 text-xs font-medium text-red-100 transition-colors"
        >
          Retry Request
        </button>
      )}
    </div>
  );
}
