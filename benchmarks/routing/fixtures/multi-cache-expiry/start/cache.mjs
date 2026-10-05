export function active(entries, now) {
  return entries.filter(e => now - e.createdAt <= e.ttl).map(e => e.key);
}
