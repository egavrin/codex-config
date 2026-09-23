export class Emitter {
  listeners = [];
  on(name) { this.listeners.push(name); }
  off(name) { this.listeners = this.listeners.filter(item => item === name); }
  emit() { return [...this.listeners]; }
}
