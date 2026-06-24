/* Single source of truth for node-type colours (matches playbook §7.4
   and the CSS variables in index.css). */

export const TYPE_COLORS = {
  Equipment: "#4f8cff",
  Procedure: "#a06bff",
  FailureMode: "#ff5d6c",
  Supplier: "#16c4b0",
  ComplianceStd: "#f6b73c",
};

export const TYPE_ORDER = [
  "Equipment",
  "Procedure",
  "FailureMode",
  "Supplier",
  "ComplianceStd",
];

export const TYPE_LABELS = {
  Equipment: "Equipment",
  Procedure: "Procedure",
  FailureMode: "Failure Mode",
  Supplier: "Supplier",
  ComplianceStd: "Compliance",
};

export const colorFor = (type) => TYPE_COLORS[type] || "#7a86a3";
