# HTML Report Format

In an authorized mode where writes are permitted, create one HTML architecture review in the OS temp directory.
Use a unique architecture-review timestamp and random suffix.
In Plan or read-only mode, write no files. Use the same content structure in Markdown/Mermaid in chat.
Tailwind and Mermaid are optional CDN features. The core content must stay readable without them.

Use Mermaid for graph diagrams. Use custom divs and inline SVG for mass diagrams and cross-sections.
Select the method that best explains each structure.

## Safe content and fallback

Treat file names, repository text, labels, and findings as untrusted data. HTML-escape all inserted text and attribute values with a standard encoder. Do not interpolate data into JavaScript, CSS, raw SVG markup, event handlers, or shell commands. Build diagrams with fixed node IDs and sanitized, quoted labels. Encode Mermaid label syntax and HTML. Prohibit source-derived directives, links, and click handlers.

Use strict Mermaid security. Repository-derived text is never executable code.

Keep every candidate's findings and before/after relationship descriptions in ordinary HTML outside the rendered diagram. If a CDN fails or Mermaid rejects a diagram, those descriptions and the source diagram remain available. Use fixed CSS for a readable fallback layout. CDN styles are optional additions. Replace illustrative scaffold content with actual findings, and use English unless the user explicitly requests another output language. Report uncertainty faithfully.

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

Include the repository name, date, and a compact legend. Use solid box = module, dashed line = seam, red arrow = leakage, and thick dark box = deep module. Start with the candidates, without an introductory paragraph.

## Candidate card

The diagrams explain structure. Keep prose concise and use the project's domain language with the vocabulary from the installed sibling [codebase-design](../codebase-design/SKILL.md). Include enough textual evidence to remain useful without diagrams.

Each candidate is one `<article>`:

- **Title**: short, names the deepening (for example "Collapse the Order intake pipeline").
- **Badge row**: recommendation strength (`Strong` = emerald, `Worth exploring` = amber, `Speculative` = slate), plus a tag for the dependency category (`in-process`, `local-substitutable`, `remote but owned`, `true external`).
- **Files and evidence**: monospaced paths with relevant symbols, line references, or observed call paths. Distinguish observations from assumptions.
- **Before / After diagram**: two columns, side by side. Add a concise ordinary-text description of each structure outside the diagram so CDN or rendering failures cannot hide the finding. See patterns below.
- **Problem**: one sentence. What hurts.
- **Solution**: one sentence. What changes.
- **Wins**: bullets, ≤6 words each. for example "Tests hit one interface", "Pricing logic stops leaking", "Delete 4 shallow wrappers".
- **ADR callout** (if applicable): one line in an amber-tinted box.

Use concise explanations and legible diagrams. Add sufficient context to support a recommendation. Keep the necessary evidence.

## Diagram patterns

Select the pattern that fits each candidate. Use different patterns when they help explain different structures.

### Mermaid graph (the workhorse for dependencies / call flow)

Use a Mermaid `flowchart` or `graph` for the relationship "X calls Y calls Z, and look at the mess." Put it in a card with Tailwind styles. Use classDef to color leakage edges red and the deep module dark. Use sequence diagrams for "before: 6 round-trips; after: 1."

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

### Custom boxes-and-arrows (when Mermaid's layout fights you)

Modules as `<div>`s with borders and labels. Arrows as inline SVG `<line>` or `<path>` elements positioned absolutely over a relative container. Use this pattern for an "after" diagram with one thick-bordered deep module and greyed-out internals. Mermaid does not render that visual weight correctly.

### Cross-section (good for layered shallowness)

Stack horizontal bands (`h-12 border-l-4`) to show layers a call passes through. Before: 6 thin layers each doing nothing. After: 1 thick band labelled with the consolidated responsibility.

### Mass diagram (good for "interface as wide as implementation")

Two rectangles per module: one for interface surface area, one for implementation. Before: interface rectangle is nearly as tall as the implementation rectangle (shallow). After: interface rectangle is short, implementation rectangle is tall (deep).

### Call-graph collapse

Before: a tree of function calls rendered as nested boxes. After: the same tree collapsed into one box, with the now-internal calls shown faded inside it.

## Style guidance

- Use a publication layout with generous whitespace. Serif headings are optional (`font-serif` works well with stone/slate).
- Use color sparingly: one accent (emerald or indigo) plus red for leakage and amber for warnings.
- Keep diagrams ~320px tall so before/after sits comfortably side by side without scrolling.
- Use `text-xs uppercase tracking-wider` for module labels inside diagrams, so they read as schematic, not as UI.
- The only scripts are the Tailwind CDN and the Mermaid ESM import. The report is otherwise static: no app code, no interactivity beyond Mermaid's own rendering.

## Top recommendation section

One larger card. Candidate name, one sentence on why, anchor link to its card. That is it.

## Tone

Use English unless the user explicitly requests another output language. Keep explanations concise and preserve project identifiers. Map the shared architecture vocabulary to the project's terms.

**Shared vocabulary:** module, interface, implementation, depth, deep, shallow, seam, adapter, leverage, locality.

Normal project terms such as component, service, API, layer, and boundary are permitted. Clarify their role when necessary rather than renaming domain concepts.

**Phrasings that fit the style:**

- "Order intake module is shallow: interface nearly matches the implementation."
- "Pricing leaks across the seam."
- "Deepen: one interface, one place to test."
- "The existing HTTP adapter and a justified test adapter exercise this seam."

**Wins bullets** name the gain in glossary terms: *"locality: bugs concentrate in one module"*, *"leverage: one interface, N call sites"*, *"interface shrinks; implementation absorbs the wrappers"*. Prefer concrete gains over unsupported claims such as "cleaner code."

State confidence honestly. Give concrete evidence for strong recommendations. Preserve uncertainty for speculative opportunities.
