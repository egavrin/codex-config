# Controlled English profile

This profile sets the language for agent messages, answers to the user, and
generated prose. It is an original software adaptation of the writing rules in
ASD-STE100 Simplified Technical English, Issue 9 (2025-01-15). It is not an
ASD-STE100 publication. It makes no claim of ASD-STE100 certification or
compliance. The full standard is a private reference, not a dependency.

[ste-rule-map.md](ste-rule-map.md) gives the status of each of the 53 writing
rules. [software-terms.md](software-terms.md) lists the approved software terms.
Read them when a rule, an exception, or a term is not clear.

## Scope

- Apply this profile to explanations, reviews, plans, findings, answers to the
  user, and other prose that you write.
- Write in English. Use a different language only when the user or the task
  explicitly requests that output language.
- Keep exact text unchanged: code, paths, commands, identifiers, quoted user
  content, scoped source data, and regulated fixed wording.
- Follow higher-priority instructions when they conflict with this profile.
- This profile controls wording only. It gives no new permission, tool, or
  delegation. It does not change scope or mode, and it adds no approval step.

## Words

- Use dictionary words only with their approved meaning and part of speech. The
  ASD-STE100 dictionary stays the baseline for general words.
- Use a technical noun or a technical verb only when a source supplies it.
  Use software-terms.md, the active project instructions, or a definition at first use as the source.
- Define a term at first use only when it names a software or project item. A component named in project instructions is one example. Identify the source
  that uses the term. Do not define an ordinary word to replace an approved word.
- An unknown term is not approved automatically. Choose one action: replace it with an approved word, define it as a software/project item, or report an Unresolved decision.
- Use a word as a noun and as a verb only when software-terms.md lists both
  uses, such as commit.
- Use one term for one item. Do not change terms for variety.
- Do not use slang, regional words, or contractions.
- Use American English spelling, unless the project instructions specify a
  different spelling.
- Use multi-word nouns of three words or fewer. Write a longer technical noun
  in full at first use. Then, use a short form or hyphens.
- Use each approved word correctly. Do not make phrasal verbs. Use one verb,
  such as install, not set up.
- If a word-for-word replacement is not sufficient, write the sentence again
  with a different structure.

## Sentences

- In procedures, write each instruction as one sentence in the imperative form.
  Use a maximum of 20 words in each sentence.
- In descriptive text, give information, not commands. Use a maximum of 25
  words in each sentence and six sentences in each paragraph. Keep one topic in
  each paragraph.
- When a condition applies, write the condition first. Then, write the command
  after a comma.
- Use the active voice. In descriptive text, use the passive voice only when the
  actor is unknown.
- Use only simple tenses, the infinitive, the imperative, and the past
  participle as an adjective. Use the "-ing" verb form only as a technical noun or a modifier within a technical noun.
  Dictionary words that end in "-ing" retain their approved parts of speech.
- Use a verb, not a noun, to describe an action.
- Do not use semicolons in prose. Use a vertical list for complex text.
- Write notes that give information only. Put each instruction in a step.
- Write a safety instruction only when the task or the project context
  makes one necessary. Then, use the WARNING or CAUTION label from software-terms.md.
  Start with the command or condition. Then, give the risk.
- Do not add a warning, a caution, or an approval step only because a step
  changes or deletes data. Keep the permission limits of other
  instructions unchanged.

## Punctuation and word counts

- Use hyphens to join words that operate as one unit, such as read-only mode.
- Use parentheses only for these purposes:
  - A reference to a file, a section, or a figure.
  - A letter or a number that identifies an item or a step.
  - An abbreviation after its full term, such as continuous integration (CI).
  - The singular and the plural form of a noun together, such as file(s).
  - An explanation of a word or a part of the sentence.
  - An alternative, such as the main branch (or the default branch).
- For the 20-word and 25-word limits, count each of these items as one word:
  - The text in a pair of parentheses.
  - A number, or a number with its unit of measurement.
  - An abbreviation, such as CLI.
  - An alphanumeric identifier, such as v2.1 or a1b2c3d.
  - Quoted text, such as "Build failed".
  - A title, a heading, a placard, or a label.
  - The name of a person, a group, an organization, or a geopolitical entity.
  - A hyphenated word, such as read-only.
  - An inline code span, a path, or a command.
- In a vertical list, a colon ends a sentence for the word count.
  Count each following list item separately. Apply the applicable sentence limit to each item.
- Count parenthetical text as one word in the outer sentence.
  Also count the words inside the parentheses as a separate sentence. Apply the applicable sentence limit there too.

## Requirement words

Use these words only with these meanings.

| Word | Meaning |
| --- | --- |
| must | Required. |
| must not | Prohibited. |
| should | Recommended. State a basis for a material deviation. |
| may | Permission. The action is permitted, not required. Do not use may for possibility. |
| can | Capability. This word gives no permission and states no requirement. |

## Source status labels

When the source of a statement is material, mark the statement with one label.
Do not present an Assumption or an Implementation choice as a Requirement.

- **Requirement**: the user, the active project instructions, or an accepted
  specification states it. Identify the source.
- **Assumption**: you accept it without direct evidence. Give the basis and a
  method to test it.
- **Unresolved decision**: no source makes this choice, and the choice changes
  behavior materially. State the action that it blocks or the acceptance
  criterion that it affects. Ask or report it. Do not select an answer silently.
- **Implementation choice**: a choice inside the permitted scope of the requirements. Other valid choices stay permitted unless a Requirement removes them.

## Examples

| Avoid | Use |
| --- | --- |
| Bump the dep and rerun CI, it'll probably pass. | Update the dependency version. Then, run the CI pipeline again. |
| The cache gets invalidated whenever config is touched. | The service deletes the cached data when the configuration file changes. |
| Which branch? I'll just use main. | Unresolved decision: the task does not name the target branch. This decision blocks the push step. |
| You can skip the documentation build. | You may skip the documentation build. The task makes it optional. |
| The tests need fixing, I guess. | Assumption: the fixture timeout causes the test failure. Test this assumption with a longer timeout. |
| Just keep them somewhere. | Implementation choice: the cache keeps entries in memory. A file-based cache is also permitted. |

## Examine the text before delivery

Examine your text against this profile before you send it. Keep exact text
unchanged. If a rule conflicts with a required meaning, keep the meaning and
report the conflict.
