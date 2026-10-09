# Software terms

This list extends the technical noun and technical verb categories of the
profile in [controlled-english.md](controlled-english.md). Rules 1.5 to 1.13 in
[ste-rule-map.md](ste-rule-map.md) control the use of these terms. When a word
is also in the ASD-STE100 dictionary, the dictionary meaning stays the baseline.
This list adds only the stated software meaning and part of speech.

## How a term qualifies

A term is approved for a text only when one of these sources supplies it:

- This list.
- The active project instructions.
- A definition at first use in the same text or packet. The term must name a
  software or project item. The definition must identify a source that uses
  the term, such as a file or the project instructions.

Code, paths, commands, and identifiers are exact text, not terms. An unknown
term is not approved. Define it, replace it, or report it as an Unresolved
decision. A definition does not approve an ordinary word in place of an
approved dictionary word. Add a term only when no approved word names the software item, operation, agent role, or status.

## Technical nouns

| Term | Meaning |
| --- | --- |
| baseline | The recorded state of a file, such as a hash, that a tool compares before a change. |
| branch | A named line of commits in a repository. |
| build | The output of a build operation, or one run of that operation. |
| bundle | The complete data that a tool sends in one request. |
| cache | Stored copies of data that a program uses again to save time. |
| client | A program that sends requests to a service. |
| commit | One recorded set of changes in a repository. |
| configuration file | A file that sets how a program operates. |
| dependency | A software package necessary to build or run a project. |
| diff | Text that shows the differences between two versions of files. |
| directory | A file system container for files and other directories. |
| exit code | The number that a process returns when it stops. |
| fixture | Fixed test data or a fake program that a test uses. |
| handoff | The transfer of a task and its context from one agent to a different agent. |
| hash | A fixed-length value that a tool calculates from data to detect changes. |
| hunk | One continuous changed section of a diff. |
| log | A record of events that a program writes. |
| packet | The task description that a native agent gives to an external agent. |
| patch | A diff that a tool can apply to files. |
| path | The location of a file or a directory. |
| pipeline | A sequence of automated build and test steps, such as a CI pipeline. |
| process | A program while it runs. |
| pull request | A request to merge the commits of one branch into a different branch. |
| repository | A set of files and its version history. |
| routing | The rules that select the agent or the skill that receives a task. |
| schema | The specification of the permitted fields and types in data. |
| scope | The paths or tasks that an agent has permission to change. |
| service | A program that runs continuously and answers requests. |
| skill | A packaged set of instructions that an agent loads for one type of task. |
| symlink | A file system entry that points to a different path. |
| test | A program or procedure that compares an actual result with an expected result. |
| timeout | A time limit after which a tool stops an operation. |
| trigger | A request or a condition that causes a host to load a skill. |

## Technical verbs

A word in both term tables, such as build or commit, is a technical noun and a
technical verb. Every other term has only the part of speech of its table.

| Term | Meaning |
| --- | --- |
| build | To make runnable output from source files. |
| commit | To record a set of changes in a repository. |
| compile | To convert source files into a form that a computer runs. |
| deploy | To install software in the system where it operates. |
| merge | To combine the changes from two branches or versions. |
| parse | To read structured text into data. |
| push | To send local commits to a remote repository. |
| revert | To make a new change that cancels an earlier change. |
| validate | To compare structured data or a program result with its schema or specification. |

## Agent roles

| Term | Meaning |
| --- | --- |
| user | The person who gives the task and owns its decisions. |
| native agent | An agent that the host runs for the user, including a native child. Active instructions define its assignment and authority. |
| root | The agent responsible for overall task scope, integration, and final acceptance. |
| external agent | A model that a native agent consults with a bounded packet. It has no task authority. The native agent examines its output as data. |
| maintainer | A person who changes these profile files. |

## Status and risk labels

[controlled-english.md](controlled-english.md) defines the requirement words
must, must not, should, may, and can. It also defines the source status labels
Requirement, Assumption, Unresolved decision, and Implementation choice. Use
these words and labels only with those meanings.

| Label | Meaning |
| --- | --- |
| WARNING | The step can cause permanent data loss, exposure of private data or credentials, or an unwanted security change. |
| CAUTION | The step can cause damage that is possible to recover from, such as a stopped service or a failed build. |

Use these labels only in a safety instruction that the task or the project
context makes necessary. Do not add a label to a step only because the step changes
or deletes data. These labels give information about risk. They give no
permission for the operation, and they add no approval step. The permission
boundaries in other instructions stay unchanged.

## Abbreviations

Write the full term at first use. API, CI, CLI, HTTP, JSON, and URL are
exceptions because they are more familiar than their full terms.

| Abbreviation | Full term |
| --- | --- |
| API | application programming interface |
| CI | continuous integration |
| CLI | command-line interface |
| HTTP | Hypertext Transfer Protocol |
| JSON | JavaScript Object Notation |
| SHA-256 | Secure Hash Algorithm with a 256-bit output |
| URL | uniform resource locator |

Do not use informal short forms such as repo, dep, config, LGTM, or nit.

## Term sources

These sources identify the software concepts in this list. These definitions
do not replace the general dictionary meanings.

- The [Git glossary](https://git-scm.com/docs/gitglossary) defines branch, commit, diff, hash, merge, patch, push, and repository concepts.
- The [GitHub glossary](https://docs.github.com/en/get-started/learning-about-github/github-glossary) supplies pull request, build, and deployment concepts.
- The [Python glossary](https://docs.python.org/3/glossary.html) supplies the software meanings of parameter, module, and related program concepts.
- The local [bridge reference](../../claude-collab/references/bridge.md) defines its baseline, bundle, packet, scope, and external-agent protocol.
- [Skill mechanics](../SKILL-MECHANICS.md) defines the local skill, trigger, and invocation concepts.
- Global [AGENTS.md](../../../AGENTS.md) defines the root and native-agent roles, their assignments, and their authority. These definitions give no new permission or route.
- The active project instructions define project-specific routing, handoffs, fixtures, schemas, and validation contracts.

When a term has no source in these materials, identify its actual project
definition before use. A source must support the stated technical meaning.
