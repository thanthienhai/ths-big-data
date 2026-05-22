## ADDED Requirements

### Requirement: Preserve Paper Template
The implementation SHALL use `paper_bigdata.docx` as the target paper template and preserve its section structure, order, and document styling unless a change is required to keep the final paper within 7 pages.

#### Scenario: Template structure is reused
- **WHEN** the filled paper is produced
- **THEN** the output retains the academic paper structure from `paper_bigdata.docx`

#### Scenario: Source template remains available
- **WHEN** the implementation modifies document content
- **THEN** the original `paper_bigdata.docx` remains recoverable or an explicit output copy is created

### Requirement: Synthesize Vietnamese Content From Source Report
The implementation SHALL fill relevant paper sections using Vietnamese content synthesized from `BTL_BigData_.docx`.

#### Scenario: Matching source content exists
- **WHEN** a paper section has enough relevant information in `BTL_BigData_.docx`
- **THEN** the section is filled with concise Vietnamese prose grounded in the source report

#### Scenario: Source claims are insufficient
- **WHEN** a paper section lacks enough source-backed information
- **THEN** the section body remains blank instead of inventing unsupported content

### Requirement: Annotate Incomplete Sections
The implementation SHALL add notes for sections that remain blank or incomplete, describing the missing content and suggesting useful additions such as tables, figures, charts, metrics, or references.

#### Scenario: Blank section needs guidance
- **WHEN** a section is left blank because source material is insufficient
- **THEN** the section includes a concise Vietnamese note explaining what content is missing

#### Scenario: Visual evidence would improve the paper
- **WHEN** a blank or incomplete section would benefit from visual support
- **THEN** the note suggests the needed table, figure, or chart

### Requirement: Enforce Seven Page Limit
The implementation SHALL constrain the final Vietnamese paper to no more than 7 pages.

#### Scenario: Draft exceeds page limit
- **WHEN** the filled draft is longer than 7 pages
- **THEN** the content is condensed while preserving the most important paper sections

#### Scenario: Notes affect length
- **WHEN** notes for missing content increase document length
- **THEN** the notes are shortened or consolidated so the output remains within 7 pages

### Requirement: Maintain Reviewable Output
The implementation SHALL produce a reviewable DOCX output and clearly identify what was filled, what was left blank, and what still needs source material.

#### Scenario: Paper is ready for review
- **WHEN** the implementation finishes
- **THEN** the workspace contains the filled paper document and a concise summary of filled sections, blank sections, and suggested additions
