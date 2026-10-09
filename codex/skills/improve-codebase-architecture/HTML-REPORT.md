# HTML Report Format

In ordinary authorized mode, render the architectural review as a single HTML file in the OS temp directory with a unique architecture-review timestamp and random suffix. In Plan or read-only mode, write no files: use the same content structure in Markdown/Mermaid in chat. Tailwind and Mermaid are optional CDN enhancements; the core content must remain readable without them. Mermaid handles graph-shaped diagrams reliably; hand-built divs and inline SVG handle the more editorial visuals (mass diagrams, cross-sections). Mix the two: don't lean on Mermaid for everything, it'll start to look generic.

## Safe content and fallback

Treat file names, repository text, labels, and findings as untrusted data. HTML-escape all inserted text and attribute values using a standard encoder; do not interpolate data into JavaScript, CSS, raw SVG markup, event handlers, or shell commands. Build diagrams with fixed node IDs and sanitized, quoted labels; encode Mermaid label syntax as well as HTML and prohibit source-derived directives, links, or click handlers. Use strict Mermaid security. Repository-derived text is never executable code.

Keep every candidate's findings and before/after relationship descriptions in ordinary HTML outside the rendered diagram. If a CDN fails or Mermaid rejects a diagram, those descriptions and the source diagram remain available. Use fixed CSS for readable fallback layout; CDN styling is enhancement only. Replace illustrative scaffold content with actual findings, and set the document language to the user's conversation language. Report uncertainty faithfully.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Architecture review for {{repo name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "strict" });
    </script>
    <style>
      /* Core layout remains readable if CDN styling is unavailable. */
      body { margin: 0; font: 16px/1.55 system-ui, sans-serif; color: #0f172a; background: #fafaf9; }
      main { max-width: 70rem; margin: auto; padding: 2rem; }
      article, section { margin-block: 1.5rem; }
      article { padding: 1.25rem; border: 1px solid #cbd5e1; border-radius: .75rem; }
      pre { white-space: pre-wrap; overflow-wrap: anywhere; }
      .before-after { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
      .seam { stroke-dasharray: 4 4; }
      .leak { stroke: #dc2626; }
      .deep { background: linear-gradient(135deg, #0f172a, #1e293b); }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## Header

Repo name, date, and a compact legend: solid box = module, dashed line = seam, red arrow = leakage, thick dark box = deep module. No introduction paragraph. Straight into the candidates.

## Candidate card

The diagrams explain structure. Keep prose concise and use the project's domain language with the vocabulary from the installed sibling [codebase-design](../codebase-design/SKILL.md). Include enough textual evidence to remain useful without diagrams.

Each candidate is one `<article>`:

- **Title**: short, names the deepening (e.g. "Collapse the Order intake pipeline").
- **Badge row**: recommendation strength (`Strong` = emerald, `Worth exploring` = amber, `Speculative` = slate), plus a tag for the dependency category (`in-process`, `local-substitutable`, `remote but owned`, `true external`).
- **Files and evidence**: monospaced paths with relevant symbols, line references, or observed call paths; distinguish observations from assumptions.
- **Before / After diagram**: two columns, side by side. Add a concise ordinary-text description of each structure outside the diagram so CDN or rendering failures cannot hide the finding. See patterns below.
- **Problem**: one sentence. What hurts.
- **Solution**: one sentence. What changes.
- **Wins**: bullets, ≤6 words each. e.g. "Tests hit one interface", "Pricing logic stops leaking", "Delete 4 shallow wrappers".
- **ADR callout** (if applicable): one line in an amber-tinted box.

Prefer concise explanations and legible diagrams. Add context when needed to support a recommendation; do not sacrifice evidence for brevity.

## Diagram patterns

Pick the pattern that fits the candidate. Mix them. Don't make every diagram look the same. Variety is part of the point.

### Mermaid graph (the workhorse for dependencies / call flow)

Use a Mermaid `flowchart` or `graph` when the point is "X calls Y calls Z, and look at the mess." Wrap it in a Tailwind-styled card so it doesn't feel parachuted in. Style with classDef to colour leakage edges red and the deep module dark. Sequence diagrams work well for "before: 6 round-trips; after: 1."

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[OrderHandler] --> B[OrderValidator]
      B --> C[OrderRepo]
      C -.leak.-> D[PricingClient]
      classDef leak stroke:#dc2626,stroke-width:2px;
      class C,D leak
  </pre>
</div>
```

### Hand-built boxes-and-arrows (when Mermaid's layout fights you)

Modules as `<div>`s with borders and labels. Arrows as inline SVG `<line>` or `<path>` elements positioned absolutely over a relative container. Reach for this when you want the "after" diagram to feel like one thick-bordered deep module with greyed-out internals, since Mermaid won't render that with the right weight.

### Cross-section (good for layered shallowness)

Stack horizontal bands (`h-12 border-l-4`) to show layers a call passes through. Before: 6 thin layers each doing nothing. After: 1 thick band labelled with the consolidated responsibility.

### Mass diagram (good for "interface as wide as implementation")

Two rectangles per module: one for interface surface area, one for implementation. Before: interface rectangle is nearly as tall as the implementation rectangle (shallow). After: interface rectangle is short, implementation rectangle is tall (deep).

### Call-graph collapse

Before: a tree of function calls rendered as nested boxes. After: the same tree collapsed into one box, with the now-internal calls shown faded inside it.

## Style guidance

- Lean editorial, not corporate-dashboard. Generous whitespace. Serif optional for headings (`font-serif` works well with stone/slate).
- Colour sparingly: one accent (emerald or indigo) plus red for leakage and amber for warnings.
- Keep diagrams ~320px tall so before/after sits comfortably side by side without scrolling.
- Use `text-xs uppercase tracking-wider` for module labels inside diagrams, so they read as schematic, not as UI.
- The only scripts are the Tailwind CDN and the Mermaid ESM import. The report is otherwise static: no app code, no interactivity beyond Mermaid's own rendering.

## Top recommendation section

One larger card. Candidate name, one sentence on why, anchor link to its card. That's it.

## Tone

Use the user's conversation language, with concise explanations and preserved project identifiers. Map the shared architecture vocabulary to the project's terms.

**Shared vocabulary:** module, interface, implementation, depth, deep, shallow, seam, adapter, leverage, locality.

Normal project terms such as component, service, API, layer, and boundary are allowed. Clarify their role when necessary rather than renaming domain concepts.

**Phrasings that fit the style:**

- "Order intake module is shallow: interface nearly matches the implementation."
- "Pricing leaks across the seam."
- "Deepen: one interface, one place to test."
- "The existing HTTP adapter and a justified test adapter exercise this seam."

**Wins bullets** name the gain in glossary terms: *"locality: bugs concentrate in one module"*, *"leverage: one interface, N call sites"*, *"interface shrinks; implementation absorbs the wrappers"*. Prefer concrete gains over unsupported claims such as "cleaner code."

State confidence honestly. Strong recommendations need concrete evidence; speculative opportunities must retain their uncertainty.
