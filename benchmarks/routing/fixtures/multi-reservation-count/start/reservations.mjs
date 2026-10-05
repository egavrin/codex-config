export function consumed(rows) {
  return rows.filter(r => r.state !== 'cancelled').reduce((n, r) => n + r.quantity, 0);
}
