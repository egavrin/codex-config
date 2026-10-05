import { active } from './cache.mjs';
export function solve(entries, now) {
  return active(entries, now);
}
