import React from "react";
import { User, Phone, Car, MapPin, Building2, CreditCard, Folder, Calendar } from "lucide-react";
import { EntityType } from "@/types";

interface EntityBadgeProps {
  type: EntityType;
  label?: string;
  className?: string;
}

export function EntityBadge({ type, label, className = "" }: EntityBadgeProps) {
  const normType = (type || "UNKNOWN").toUpperCase();

  let Icon = User;
  let style = "bg-blue-950/80 border-blue-700/60 text-blue-300";

  if (normType === "PHONE") {
    Icon = Phone;
    style = "bg-cyan-950/80 border-cyan-700/60 text-cyan-300";
  } else if (normType === "VEHICLE") {
    Icon = Car;
    style = "bg-amber-950/80 border-amber-700/60 text-amber-300";
  } else if (normType === "LOCATION") {
    Icon = MapPin;
    style = "bg-emerald-950/80 border-emerald-700/60 text-emerald-300";
  } else if (normType === "ORGANIZATION") {
    Icon = Building2;
    style = "bg-slate-900 border-slate-700 text-slate-300";
  } else if (normType === "BANK_ACCOUNT") {
    Icon = CreditCard;
    style = "bg-purple-950/80 border-purple-700/60 text-purple-300";
  } else if (normType === "CASE") {
    Icon = Folder;
    style = "bg-indigo-950/80 border-indigo-700/60 text-indigo-300";
  } else if (normType === "DATE") {
    Icon = Calendar;
    style = "bg-zinc-900 border-zinc-700 text-zinc-300";
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-mono border ${style} ${className}`}>
      <Icon className="w-3.5 h-3.5 shrink-0" />
      <span>{label || normType}</span>
    </span>
  );
}
