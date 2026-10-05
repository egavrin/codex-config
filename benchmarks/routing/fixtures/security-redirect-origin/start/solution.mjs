export function solve(trusted, candidate) {
  return candidate.startsWith(trusted) ? candidate : null;
}
