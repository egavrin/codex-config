import { Emitter } from './emitter.mjs';
export function solve(actions) {
  const emitter = new Emitter();
  const delivered = [];
  for (const [kind, name] of actions) {
    if (kind === 'on') emitter.on(name);
    if (kind === 'off') emitter.off(name);
    if (kind === 'emit') delivered.push(...emitter.emit());
  }
  return delivered;
}
