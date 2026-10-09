# ASD-STE100 rule map

This map gives the status of each of the 53 writing rules in ASD-STE100
Simplified Technical English, Issue 9, for the profile in
[controlled-english.md](controlled-english.md). Each subject is a short original
summary, not the upstream wording. The ASD-STE100 dictionary stays the baseline
for approved meanings and parts of speech. Sections 5 and 6 apply to procedures
and to descriptive text respectively.

Source: ASD-STE100 Issue 9, dated 2025-01-15, at
https://asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf, SHA-256
d1f4ea9e7cd6e46b47aa9057209f99e78c0e9cfc4e27a5b07895b05c1a166431. The standard
is a private reference. This repository does not include it or depend on it.
This map makes no claim of certification.

## Statuses and scopes

- **Adopted**: the rule applies as the standard states it. The Exception column
  adds only E and notes on how the rule applies to software text.
- **Adapted**: the rule applies with the software change in the Exception
  column.
- **Conditional**: the rule applies only in the case in the Applies to column.
- **All prose**: agent messages, answers to the user, explanations, and other
  generated prose.
- **Procedures**: steps and instructions to an agent or to the user.
- **Descriptive text**: explanations, reviews, findings, and answers that give
  information.
- **E** (exact-text exception): code, paths, commands, identifiers, quoted user
  content, scoped source data, regulated fixed wording, and text in an
  explicitly requested language other than English. Exact text must stay
  accurate, and the rules apply to English only.

## Map

| Rule | Subject | Status | Applies to | Exception | Reason |
| --- | --- | --- | --- | --- | --- |
| 1.1 | Permitted word sources | Adapted | All prose | E. Also the requirement words and source status labels in controlled-english.md. | Fixed levels of obligation are necessary for requirement text. The dictionary does not supply these levels. |
| 1.2 | Part of speech of dictionary words | Adopted | All prose | E only. | One part of speech for each word prevents ambiguous text. |
| 1.3 | Approved meanings of dictionary words | Adapted | All prose | E. Also must, must not, should, may, and can, only with the meanings in controlled-english.md. | One fixed meaning for each requirement word prevents a misread obligation. |
| 1.4 | Approved forms of verbs and adjectives | Adopted | All prose | E only. | Fixed forms keep the meaning predictable. |
| 1.5 | Words in a technical noun category | Adapted | All prose | E. For software text, the categories are the software items, agent roles, and labels in software-terms.md. A word must fit one of these categories. | This profile maps the categories to software text in one list. Each agent then uses the same categories. |
| 1.6 | Words not in the dictionary only in technical nouns | Adapted | All prose | E. Such a word qualifies only from software-terms.md, the active project instructions, or a definition at first use. A definition at first use must identify a software or project item and the source that uses it. | An unknown word must not become approved by default. A definition must not approve an ordinary word only because the word is convenient. |
| 1.7 | Technical nouns not used as verbs | Adapted | All prose | E. A word that software-terms.md lists as both a technical noun and a technical verb, such as commit, has both uses. Other technical nouns stay nouns only. | Software text uses some words for an item and for the operation that makes it. The term list gives each permitted part of speech. |
| 1.8 | Technical nouns approved for the company, industry, or subject field | Adapted | All prose | E. The approved sources are software-terms.md, the active project instructions, and definitions at first use in the same text or packet. Each definition names a software or project item and its source. | The project is the company and subject field for this profile. A source makes each approval traceable. |
| 1.9 | Short, clear technical nouns | Adopted | All prose | E only. | Short terms are easy to find and to repeat. |
| 1.10 | No regional words, slang, or jargon as technical nouns | Adopted | All prose | E. Terms in software-terms.md are field terms, not jargon. | Field terms have one known meaning. Short forms such as repo and LGTM do not qualify. |
| 1.11 | One technical noun for one item | Adopted | All prose | E only. | Two names make the reader think that two items exist. |
| 1.12 | Verbs in a technical verb category | Adapted | All prose | E. For software text, the category is the software operations in software-terms.md. | This profile maps the category to software operations in one list. Each agent then uses the same technical verbs. |
| 1.13 | Technical verbs not used as nouns | Adapted | All prose | E. A word that software-terms.md lists as both a technical verb and a technical noun, such as build, has both uses. Other technical verbs stay verbs only. | Software text uses some words for an operation and for its result. The term list gives each permitted part of speech. |
| 1.14 | American English spelling | Adopted | All prose in English | E. A spelling that the project instructions specify takes precedence. | The rule makes an exception for other official directives. Project instructions are such directives. |
| 2.1 | Multi-word nouns of three words or fewer | Adopted | All prose | E. An identifier or a file name is exact text, not a noun group. | Long noun groups hide the relation between the words. |
| 2.2 | Technical nouns of more than three words | Adopted | All prose | E only. | A full first use and then a short form keeps the term exact and short. |
| 3.1 | Verb forms from the dictionary | Adopted | All prose | E only. | Fixed forms keep the meaning predictable. |
| 3.2 | Permitted verb forms and tenses | Adopted | All prose | E only. | Simple tenses make time and status clear. |
| 3.3 | Past participle as an adjective | Adopted | All prose | E only. | A past participle has one clear function in a sentence. |
| 3.4 | No complex verb constructions with auxiliaries | Adapted | All prose | E. A requirement word from controlled-english.md with an infinitive, such as must run or may skip, is permitted. | The profile extends the modal words for requirement text. Each requirement word has one defined meaning, not a complex tense. |
| 3.5 | The "-ing" verb form as a technical noun or its modifier | Adopted | All prose | E only. | Approved dictionary words that end in "-ing" keep their specified parts of speech. |
| 3.6 | Active voice | Adopted | All prose | E. Passive voice is permitted in descriptive text when the actor is unknown. | An active sentence names the actor. The actor identifies who must do the work. |
| 3.7 | Verbs for actions | Adopted | All prose | E only. | A verb makes the required action clear. |
| 4.1 | Short, clear sentences | Adopted | All prose | E only. | Short sentences reduce parsing errors. |
| 4.2 | No omitted words and no contractions | Adapted | All prose | E. Headings, table cells, and labels may use short noun phrases. Contractions stay prohibited. | Compact cells make reference tables easy to read. Full sentences around the tables keep the instructions complete. |
| 4.3 | Vertical lists for complex text | Adopted | All prose | E only. | A list makes each step and condition easy to examine. |
| 4.4 | Connecting words for related sentences | Adopted | All prose | E only. | Connecting words show the logic between statements. |
| 4.5 | Articles and demonstratives before nouns | Adopted | All prose | E. Headings, table cells, and labels may omit articles. | The rule applies only when applicable. Compact labels are not applicable cases. |
| 5.1 | Procedure sentences of 20 words or fewer | Adopted | Procedures | E. Put a long command or path on its own line, outside the sentence. | Short steps reduce skipped or merged actions. |
| 5.2 | One instruction in each sentence | Adopted | Procedures | E only. The rule itself has an exception for simultaneous actions in one sentence. | Each step gives one completion point that a reader can examine. |
| 5.3 | Imperative form for instructions | Adopted | Procedures | E only. | The imperative names the action directly. |
| 5.4 | Condition before the command | Adopted | Procedures | E only. | The reader examines the condition before the action. |
| 5.5 | Notes give information only | Adopted | Procedures | E only. | An instruction in a note is easy to miss. |
| 6.1 | Information in a gradual sequence | Adopted | Descriptive text | E only. | The reader gets the context before the detail. |
| 6.2 | Key words for a logical structure | Adopted | Descriptive text | E only. | Key words help a reader find each part. |
| 6.3 | Descriptive sentences of 25 words or fewer | Adopted | Descriptive text | E. Put long code or a long path on its own line. | Short sentences reduce parsing errors. |
| 6.4 | Paragraphs for related information | Adopted | Descriptive text | E only. | A paragraph shows which statements belong together. |
| 6.5 | One topic in each paragraph | Adopted | Descriptive text | E only. | One topic makes each paragraph easy to find and to cite. |
| 6.6 | Six sentences or fewer in each paragraph | Adopted | Descriptive text | E only. | Short paragraphs are easy to scan. |
| 7.1 | A word that identifies the risk level | Conditional | A safety instruction that is necessary for the task or project context | E. Use the WARNING and CAUTION labels in software-terms.md. Do not add a safety instruction only because a step changes or deletes data. | The rule lets the writer select an applicable word. The software labels name software risks, such as data loss. Unrelated warnings make the necessary warnings less visible. |
| 7.2 | Safety instructions start with a command or condition | Conditional | Same as 7.1 | E only. | The reader sees the required action before the risk. |
| 7.3 | Explanation of the risk or result | Conditional | Same as 7.1 | E only. | The reason lets the reader judge the result. |
| 8.1 | No semicolons | Adopted | All prose | E. Semicolons in code, commands, and quoted text stay. | Two sentences are clearer than one long sentence. |
| 8.2 | Hyphens for directly related words | Adopted | All prose | E only. | A hyphen shows one unit, as in read-only mode. |
| 8.3 | Permitted uses of parentheses | Adopted | All prose | E. Parentheses in code, commands, and function calls are exact text. | Parentheses keep a reference, an identifier, an abbreviation, a plural form, an explanation, or an alternative next to the related word. |
| 8.4 | A colon in a vertical list ends a sentence for word counts | Adopted | Procedures and descriptive text | E only. | Count the text before the colon and each following list item separately. Apply the applicable sentence limit to each part. |
| 8.5 | Text in parentheses counts as one word | Adopted | Procedures and descriptive text | E only. | Count the parenthetical text as one word in the outer sentence. Also count its internal words as a separate sentence. Apply the sentence limit to both. |
| 8.6 | Elements that count as one word | Adapted | Procedures and descriptive text | E. Count each number, number with units, abbreviation, alphanumeric identifier, quoted text, title, heading, placard, or label as one word. Also count each name of a person, group, organization, or geopolitical entity as one word. The profile also counts each inline code span, path, or command as one word. | Exact text cannot change to fit a word limit. A software identifier often has the form of code. |
| 8.7 | Hyphenated words count as one word | Adopted | All prose | E only. | This keeps word counts consistent with rule 8.2. |
| 9.1 | A different sentence structure when a word replacement is not sufficient | Adopted | All prose | E only. | A direct word replacement can keep an unclear structure or change the meaning. |
| 9.2 | Correct use of each approved word | Adopted | All prose | E only. | An approved word with an incorrect function or meaning makes the text ambiguous. |
| 9.3 | No phrasal verbs from two words | Adopted | All prose | E. Exact text, such as a command name, stays unchanged. | The meaning of a phrasal verb does not come from its parts. One verb, such as install, is clear. |
| 9.4 | Consistent terminology and wording | Adopted | All prose | E only. | The same wording for the same action lets the reader recognize it fast. |
