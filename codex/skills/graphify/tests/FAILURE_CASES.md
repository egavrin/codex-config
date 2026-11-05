# Failure cases before implementation

The public launcher needs these workflow checks before acceptance:

- First extraction fails, returns malformed data, or omits the graph.
- A later extraction fails after writing partial output and damages the previous graph.
- Unchanged sources trigger unnecessary extraction.
- Added, changed, or deleted sources leave stale results.
- A query omits source references or uses another project's graph.
- An ignored file, credential file, symbolic link, or output directory enters extraction.
- Provider environment variables enable a model backend or skill refresh.
- Simultaneous readers and writers use inconsistent data or wait indefinitely.
- Read-only mode creates a cache, lock, query stamp, bytecode, or graph.
- A missing, stale, or malformed graph reaches the query engine.
- A state-file or graph-file symbolic link exposes a credential target during a read-only query.
- A filesystem root, home directory, or multi-project parent enters extraction.
- Claude worktrees block the parent graph or enter its extraction and freshness checks.
- A worktree exclusion hides an unrelated nested repository outside `.claude/worktrees/`.
- A graph from an earlier exclusion policy is reused without a rebuild.
- Added, changed, or deleted files below a `dist` directory trigger unnecessary extraction.
- A `dist` exclusion hides a nested Git directory or linked-worktree file.
- A nested-project fallback omits the project boundary or exposes Git marker contents.
- State format 3 remains fresh after the fingerprint policy changes.
- Parent extraction visits a Git index entry with mode `160000` or includes its source through a symbolic link.
- An ignore negation or a literal path with glob characters changes which submodule paths the scanner excludes.
- A submodule path with a different filesystem spelling hides an unrelated directory or enters extraction.
- Changes inside a submodule trigger parent extraction. Changes to its Git index entry leave the parent graph current.
- The launcher trusts `.gitmodules` without a matching Git index entry.
- An unreadable or conflicted Git index allows extraction or changes the previous graph.
- Converting a source directory to a submodule leaves its symbols in the parent graph.
- Removing a submodule declaration fails to restore ordinary source to the parent graph.
- Local Git excludes replace user entries or change tracked ignore files.
- An interrupted publication leaves a recoverable previous graph.

The workflow test uses separate temporary Git repositories and a fake CLI for failure injection.
It also supports the installed Graphify CLI for a real extraction and query workflow.
Each run saves the command, fixture inputs, script hashes, expected results, and observed results.
