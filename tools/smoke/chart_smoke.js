const fs = require('fs');
function el(tag) {
  return {
    tagName: tag, children: [], attrs: {}, textContent: '',
    setAttribute(k, v) { this.attrs[k] = v; },
    getAttribute(k) { return this.attrs[k]; },
    appendChild(c) { this.children.push(c); return c; },
    removeChild(c) { this.children = this.children.filter((x) => x !== c); },
    get firstChild() { return this.children[0] || null; },
  };
}
const inputs = { 'staged-window': '24', 'staged-yield': '4', 'staged-drift': '7' };
const nodes = { 'staged-chart': el('svg'), 'staged-chart-legend': el('p') };
globalThis.window = globalThis;
globalThis.window.print = () => {};
globalThis.document = {
  getElementById: (id) => (id in nodes ? nodes[id] : id in inputs ? { value: inputs[id], addEventListener() {} } : null),
  querySelectorAll: () => [],
  createElementNS: (ns, tag) => el(tag),
  createElement: (tag) => el(tag),
};
for (const file of ['assets/staged-vs-lump.js', 'assets/app.js']) {
  const script = new (require('vm').Script)(fs.readFileSync(file, 'utf8'), { filename: file });
  script.runInThisContext();
}
const chart = nodes['staged-chart'];
console.log('bars:', chart.children.filter((c) => c.tagName === 'rect').length);
console.log('labels:', chart.children.filter((c) => c.tagName === 'text').length);
console.log('legend:', nodes['staged-chart-legend'].textContent);
