export function solve(timestamps) {
  const counts = {};
  for (const stamp of timestamps) {
    const day = stamp.slice(0, 10);
    counts[day] = (counts[day] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort());
}
