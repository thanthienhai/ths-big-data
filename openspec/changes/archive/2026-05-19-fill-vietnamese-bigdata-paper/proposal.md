## Why

The project needs a Vietnamese paper-style report derived from the detailed `BTL_BigData_.docx` content while preserving the academic paper structure in `paper_bigdata.docx`. The requested output must be concise enough to fit within a 7-page limit, so the change needs explicit rules for selecting, condensing, and marking incomplete sections.

## What Changes

- Fill the paper template with relevant Vietnamese content extracted and synthesized from `BTL_BigData_.docx`.
- Preserve the paper format and section structure from `paper_bigdata.docx` as the target layout.
- Leave sections blank when the source report does not contain enough article-quality content for them.
- Add notes and suggestions for blank or incomplete sections, including suggested content, tables, figures, or charts where useful.
- Keep the final paper in Vietnamese and constrained to a maximum of 7 pages.
- Avoid inventing unsupported technical claims beyond the source material; clearly mark gaps instead.

## Capabilities

### New Capabilities

- `vietnamese-paper-fill`: Defines requirements for producing a 7-page Vietnamese paper from the detailed Big Data report and paper template.

### Modified Capabilities

- None.

## Impact

- Affects document authoring workflow for `paper_bigdata.docx`.
- Requires reading and synthesizing content from `BTL_BigData_.docx`.
- No application code, APIs, runtime dependencies, or database schemas are expected to change.
