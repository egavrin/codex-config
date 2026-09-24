import { consumed } from './reservations.mjs';
export function solve(stock, reservations) {
  const left = stock - consumed(reservations);
  return left < 0 ? null : left;
}
