export const cytoscapeStyles: any[] = [
  // Base Node Style
  {
    selector: "node",
    style: {
      "label": "data(label)",
      "color": "#e2e8f0",
      "font-size": "11px",
      "font-family": "ui-monospace, monospace",
      "text-valign": "bottom",
      "text-margin-y": 6,
      "text-outline-color": "#070b13",
      "text-outline-width": 2,
      "text-max-width": "110px",
      "text-wrap": "ellipsis",
      "background-color": "#1e293b",
      "border-width": 2,
      "border-color": "#334155",
      "width": 38,
      "height": 38,
      "transition-property": "background-color, border-color, width, height, border-width",
      "transition-duration": "0.2s"
    } as any,
  },

  // Node Type Shapes & Background Colors
  {
    selector: "node[type = 'PERSON']",
    style: {
      "shape": "ellipse",
      "background-color": "#1e3a8a",
      "border-color": "#3b82f6",
    } as any,
  },
  {
    selector: "node[type = 'PHONE']",
    style: {
      "shape": "diamond",
      "background-color": "#083344",
      "border-color": "#06b6d4",
      "width": 34,
      "height": 34,
    } as any,
  },
  {
    selector: "node[type = 'VEHICLE']",
    style: {
      "shape": "rectangle",
      "background-color": "#451a03",
      "border-color": "#f59e0b",
      "width": 42,
      "height": 30,
    } as any,
  },
  {
    selector: "node[type = 'LOCATION']",
    style: {
      "shape": "hexagon",
      "background-color": "#064e3b",
      "border-color": "#10b981",
      "width": 40,
      "height": 40,
    } as any,
  },
  {
    selector: "node[type = 'BANK_ACCOUNT']",
    style: {
      "shape": "tag",
      "background-color": "#3b0764",
      "border-color": "#a855f7",
      "width": 36,
      "height": 36,
    } as any,
  },
  {
    selector: "node[type = 'ORGANIZATION']",
    style: {
      "shape": "round-rectangle",
      "background-color": "#334155",
      "border-color": "#94a3b8",
      "width": 46,
      "height": 32,
    } as any,
  },

  // Risk Level Borders and Sizes
  {
    selector: "node[risk_level = 'CRITICAL']",
    style: {
      "border-color": "#ef4444",
      "border-width": 4,
      "width": 46,
      "height": 46,
      "font-weight": "bold",
    } as any,
  },
  {
    selector: "node[risk_level = 'HIGH']",
    style: {
      "border-color": "#f97316",
      "border-width": 3,
      "width": 42,
      "height": 42,
    } as any,
  },
  {
    selector: "node[risk_level = 'MODERATE']",
    style: {
      "border-color": "#f59e0b",
      "border-width": 2.5,
    } as any,
  },

  // Base Edge Style
  {
    selector: "edge",
    style: {
      "width": 1.5,
      "line-color": "#334155",
      "target-arrow-color": "#334155",
      "target-arrow-shape": "triangle",
      "curve-style": "bezier",
      "arrow-scale": 0.8,
      "opacity": 0.7,
      "label": "data(relationship)",
      "font-size": "9px",
      "font-family": "ui-monospace, monospace",
      "color": "#64748b",
      "text-rotation": "autorotate",
      "text-background-color": "#0b0f19",
      "text-background-opacity": 0.8,
      "text-background-padding": "2px",
    } as any,
  },

  // Edge Type Styles
  {
    selector: "edge[relationship = 'TRANSFERRED_MONEY']",
    style: {
      "line-color": "#8b5cf6",
      "target-arrow-color": "#8b5cf6",
      "line-style": "dashed",
      "width": 2,
    } as any,
  },
  {
    selector: "edge[relationship = 'CALLED']",
    style: {
      "line-color": "#06b6d4",
      "target-arrow-color": "#06b6d4",
      "width": 1.8,
    } as any,
  },
  {
    selector: "edge[relationship = 'MET'], edge[relationship = 'SHARED_VEHICLE']",
    style: {
      "line-color": "#f59e0b",
      "target-arrow-color": "#f59e0b",
      "width": 2.2,
    } as any,
  },

  // Selection and Highlight States
  {
    selector: "node:selected",
    style: {
      "border-color": "#38bdf8",
      "border-width": 5,
      "background-color": "#0284c7",
      "shadow-blur": 15,
      "shadow-color": "#38bdf8",
      "shadow-opacity": 0.8,
    } as any,
  },
  {
    selector: "node.highlighted",
    style: {
      "border-color": "#38bdf8",
      "border-width": 4,
      "opacity": 1.0,
      "z-index": 999,
    } as any,
  },
  {
    selector: "node.path-node",
    style: {
      "border-color": "#ec4899",
      "border-width": 5,
      "background-color": "#be185d",
      "z-index": 1000,
      "width": 48,
      "height": 48,
    } as any,
  },
  {
    selector: "edge.path-edge",
    style: {
      "line-color": "#ec4899",
      "target-arrow-color": "#ec4899",
      "width": 4,
      "opacity": 1.0,
      "z-index": 1000,
    } as any,
  },
  {
    selector: "node.dimmed, edge.dimmed",
    style: {
      "opacity": 0.12,
    } as any,
  },
  {
    selector: "node.community-1",
    style: { "background-color": "#1e3a8a", "border-color": "#60a5fa" } as any,
  },
  {
    selector: "node.community-2",
    style: { "background-color": "#831843", "border-color": "#f472b6" } as any,
  },
  {
    selector: "node.community-3",
    style: { "background-color": "#14532d", "border-color": "#4ade80" } as any,
  },
];
