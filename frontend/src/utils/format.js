// The backend stores UTC without a timezone suffix, so add "Z" before parsing
export function formatDate(iso) {
  if (!iso) return "";
  const hasTimezone = /([zZ]|[+-]\d{2}:?\d{2})$/.test(iso);
  const date = new Date(hasTimezone ? iso : `${iso}Z`);
  return date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

export const percent = (score) => `${Math.round(Math.max(0, Math.min(1, score)) * 100)}%`;