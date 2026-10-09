---
name: improve-codebase-architecture
description: "Review codebase architecture for evidenced opportunities to deepen modules, reduce coupling, and improve workflow testability. Present candidates and guide design decisions. Use for architectural reviews or structural refactor exploration. Exclude tiny local cleanups."
---

# Improve Codebase Architecture

Identify architectural friction. Propose **deepening opportunities**: refactors that hide meaningful complexity behind a usable interface. Honor the user's scope and the active repository instructions, execution mode, and delegation policy. Use English for reports and discussion unless the user explicitly requests another output language. Preserve project identifiers.

Read the installed sibling [codebase-design](../codebase-design/SKILL.md) when applying its shared architecture principles. Map module, interface, depth, seam, adapter, leverage, and locality to project terms. Existing terms such as service or API remain valid. Read relevant `GLOSSARY.md` entries and `docs/adr/` decisions when present. Their absence, or the absence of Git, does not block a review.

## Explore the requested scope

If the user names a module, subsystem, candidate, or pain point, start there. Otherwise use recent commit history when available to identify frequently changed areas before widening the review. Without useful history, start from the known workflow or entry points and state the scope assumption.

Inspect the smallest connected surface needed to substantiate architectural friction:

- Must a reader move between many small modules to understand one concept?
- Is an interface nearly as complex as what it hides?
- Does logic or dependency knowledge leak across callers?
- Do tests miss failures in the complete workflow, or is the public interface hard to exercise?

Use the deletion test carefully. If complexity disappears with the module, the module can be redundant forwarding. If complexity appears again across callers, the module provides useful depth. Do not mistake file count or small functions alone for architectural harm. Preserve existing behavior and contracts when evaluating refactors.

Investigate directly unless the active AGENTS routing calls for delegation. Follow that routing and its ownership, model, concurrency, and acceptance rules. This skill makes no subagent mandatory.

## Present evidenced candidates

Use [HTML-REPORT.md](HTML-REPORT.md) for report structure, diagram patterns, safe rendering, and fallback presentation. Include evidence from concrete files or call paths, the problem, proposed direction, benefits, before/after visuals, and recommendation strength (`Strong`, `Worth exploring`, or `Speculative`). Separate observed friction from assumptions. Mark any material ADR conflict and explain why reopening it may be justified. Do not invent candidates to fill a quota. If evidence shows no worthwhile opportunity, report that result.

In ordinary authorized mode, create a unique `architecture-review-<timestamp>-<random>.html` using the OS temporary directory (for example, Python's `tempfile`), never the repository by default. Show it with available Codex file/browser tools and provide an absolute Markdown file link. If no opener is available, the absolute link still delivers the artifact. Do not execute repository-derived text or shell-interpolate it.

In Plan or read-only mode, write no report file. Present the same core content as Markdown with Mermaid in chat. If the user has selected a candidate already, focus on it and skip the selection question. Otherwise present the candidates and discuss the user's choice before detailing interfaces.

## Guide the chosen design

Use a standalone decision conversation. No additional grilling or domain-modeling skill is required. Identify the observable workflow, existing contracts, invariants, failure modes, dependencies, and constraints that matter. Resolve material uncertainties with focused questions while advancing independent analysis. Explain what the module would hide, where variation really exists, which callers change, and how behavior will be verified.

When alternative interfaces would help, read the sibling [DESIGN-IT-TWICE.md](../codebase-design/DESIGN-IT-TWICE.md). For dependency and testing decisions, use [DEEPENING.md](../codebase-design/DEEPENING.md).

Edit code, glossaries, and ADRs only within the requested scope and a mode where writes are permitted. Existing authorization remains sufficient. Do not invent an extra approval gate. A review-only request produces recommendations. Record new or clarified domain terms only when documentation changes are in scope. When requested or already authorized, record a durable decision or rejection reason in an ADR.

Follow project conventions. Otherwise, discuss the proposed documentation change without a file write.

## Source and adaptation

Locally adapted from Matt Pocock's skills for Codex. See [PROVENANCE.md](PROVENANCE.md) for the upstream source, pinned revision, adaptation details, and license.
