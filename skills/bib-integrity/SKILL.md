---
name: bib-integrity
description: Verify and repair academic bibliographic records against authoritative sources — work identity, authorship, publication metadata, persistent identifiers, version status, and citation-style representation — without inventing unresolved fields or judging whether a source supports a substantive claim.
---

# Bibliographic Integrity

Verify academic references as bibliographic records, not as plausible text. Resolve the cited work and ground every material field before treating a bibliography, reference list, or BibTeX database as publication-ready.

## Use when

- preparing or auditing references for a paper, report, thesis, or scholarly presentation
- creating or repairing BibTeX or another structured bibliography
- checking author names/order, titles, venues, dates, volume/issue, pages or article numbers, DOI/arXiv/ISBN metadata, or publication status
- normalising references to an explicitly supplied journal, publisher, conference, or style-guide requirement
- a source-of-truth audit needs the identity and metadata of scholarly references verified

Do not use this skill to decide whether a cited source supports the surrounding claim, to perform a literature review, or to judge novelty or research significance.

## Responsibility boundary

`bib-integrity` owns **bibliographic identity, metadata, version identity, and representation**.

It does not own **claim/source faithfulness**: whether a paper actually proves, states, or supports the proposition for which it is cited. For a candidate source-of-truth artifact, `sot-integrity` owns that source-grounding judgement and may consume `bib-integrity` findings as evidence.

Do not emit `sot-integrity` verdicts such as `TRUSTED`, `CONFLICTED`, or `BROKEN`.

## Inputs

Gather or infer:

- `artifact` — reference list, manuscript, bibliography database, or records to verify
- `target_style` — journal/conference/publisher style or other citation rules, if supplied
- `target_format` — prose references, BibTeX, BibLaTeX, CSL-oriented data, or another requested representation
- `source_constraints` — supplied authoritative sources or repository constraints, if any

If no target style is supplied, preserve a coherent existing style. Do not invent venue-specific formatting rules.

## Evidence rules

Verification requires external bibliographic evidence. Model memory, generated citations, search snippets, and another unsourced bibliography are discovery aids only.

Prefer the source closest to the record being verified rather than imposing one universal database ranking:

- official publisher, journal, conference, or proceedings records for publication metadata and venue citation guidance
- authoritative persistent-identifier registries for identifier resolution
- official scholarly repositories for preprint metadata and version identity
- disciplinary or institutional bibliographic databases as corroborating evidence

When authoritative sources materially disagree, report the conflict. Do not silently choose the value that looks most plausible.

## Procedure

### 1. Inventory records

Identify each distinct cited record and, for structured bibliographies, its citation key. Detect duplicate keys and likely duplicate records before normalisation.

### 2. Resolve work identity

Resolve each record to a unique scholarly work using title, authors, identifiers, venue, and date together.

- A DOI, arXiv ID, ISBN, or other identifier must resolve to the same work described by the remaining fields.
- Similar title text is not sufficient when authors, venue, or version disagree.
- Failure to locate a work is `UNRESOLVED`, not proof that the work is fictitious, unless authoritative evidence establishes invalidity.

### 3. Verify material fields

Check, when applicable:

- author identity and author order
- exact title and subtitle
- journal, conference, book, proceedings, or publisher identity
- publication year/date
- volume, issue, pages, or article number
- DOI, arXiv ID, ISBN, or other persistent identifier
- edition or version information
- publication state: preprint, accepted manuscript, conference version, or version of record
- structured-entry type and fields

Do not infer missing volume, pages, initials, name order, or identifiers from convention or memory.

### 4. Preserve name identity

Distinguish bibliographic identity from style rendering.

- Preserve the authoritative author sequence.
- Do not guess family/given-name roles from typography, capitalization, or cultural assumptions.
- A target style may change display order, initials, punctuation, or truncation while preserving author identity and sequence.
- When structured metadata and display text differ, use the structured identity fields when they are authoritative; otherwise mark the ambiguity unresolved.

### 5. Distinguish versions

Do not conflate a preprint, conference paper, accepted manuscript, and later version of record.

A deliberate citation to an earlier version is valid when identified as that version. When replacing it with a later version would change what was actually consulted or cited, report the option rather than silently substituting it.

### 6. Apply representation rules

Apply formatting only after identity and metadata are verified.

- Follow the explicitly supplied target style or venue instructions.
- Use a venue-provided preferred citation when it is compatible with the requested style and identifies the intended version.
- Use journal abbreviations only when the target style or an authoritative abbreviation source defines them; otherwise retain the full title.
- Do not convert page ranges to article numbers, or vice versa, merely to make records look uniform.

### 7. Repair without invention

For every incorrect field, replace it only when authoritative evidence supplies the correction. Leave unresolved fields unresolved and name the evidence needed to close them.

When generating a new record, omit optional metadata that cannot be verified rather than fabricating a complete-looking citation.

## Per-record status

Assign exactly one status to each material record:

- `VERIFIED` — unique work resolved; material metadata and requested representation are grounded
- `REPAIRABLE` — unique work resolved; one or more material fields are wrong or incomplete and authoritative corrections are available
- `CONFLICTED` — identifiers or authoritative records disagree materially about work identity or required metadata
- `UNRESOLVED` — work identity or a required material field cannot be verified from available authoritative evidence

Use the first applicable status in this order: `CONFLICTED` → `UNRESOLVED` → `REPAIRABLE` → `VERIFIED`.

A formatting-only difference that is permitted by the target style does not make a record `REPAIRABLE`.

## Severity

- **BLOCKING** — wrong or unresolved work identity; identifier points to another work; wrong author identity/order; wrong version identity; fabricated material metadata; duplicate structured key that breaks bibliography resolution
- **MINOR** — verified work with a correctable style or non-identity metadata defect that does not risk citing the wrong work
- **NOTE** — optional normalisation or a better-supported representation that does not correct an error

If a supposedly stylistic difference can change identity or version interpretation, treat it as BLOCKING.

## Required output

Default to review mode. Report:

1. **Summary** — counts by per-record status and any blocking condition.
2. **Record evidence** — for every record: citation key or location, status, and authoritative supporting source(s) sufficient to audit the verification decision.
3. **Defect details** — for each non-`VERIFIED` record: severity, affected field, observed value, and concrete correction or unresolved requirement.
4. **Duplicate/version findings** — duplicate keys, duplicate records, or version-family collisions; write `None` when absent.
5. **Repair output** — corrected citation/BibTeX text when requested and evidence is sufficient. Never fill unresolved fields.

In generation or fix mode, still surface `CONFLICTED` and `UNRESOLVED` records rather than hiding them behind polished output.

## Boundary cases

Must flag:

- a DOI resolves to a different title or authors than the bibliography entry
- author order was guessed incorrectly
- an arXiv preprint is represented as the journal version of record
- plausible volume/pages were inserted without evidence
- two BibTeX keys resolve to the same work and create duplicate bibliography entries
- a journal abbreviation was invented rather than grounded in the requested style

Must not flag:

- a target style renders family/given names differently while preserving identity and author sequence
- a journal uses an article number instead of a page range
- a correctly identified preprint is deliberately cited although a later version of record exists
- the full journal title is retained because no authoritative abbreviation rule is available

## Working rules

- Verify before formatting.
- Never treat fluency or plausibility as bibliographic evidence.
- Never manufacture a missing reference to make an in-text citation resolve.
- Preserve exact Unicode/diacritics in names and titles when supported by authoritative metadata and the target format.
- Report source conflicts and uncertainty explicitly.
- Keep the review bibliographic: do not expand into reading every cited paper for substantive support.
