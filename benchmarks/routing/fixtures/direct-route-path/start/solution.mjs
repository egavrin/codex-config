export function solve(path) {
  return path.replace(/\/+$/, '') || '/';
}
