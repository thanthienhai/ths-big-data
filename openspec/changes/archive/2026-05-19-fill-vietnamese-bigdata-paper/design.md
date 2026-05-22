## Context

The workspace contains two Word documents: `BTL_BigData_.docx` as the detailed source report and `paper_bigdata.docx` as the target paper template. The output is a Vietnamese academic-style paper, capped at 7 pages, that reuses the template's structure and only fills sections where the source report provides enough article-quality material.

The implementation is a document-authoring task rather than an application-code change. The main technical risk is preserving the template's formatting while editing DOCX content and avoiding unsupported claims when summarizing the source report.

## Goals / Non-Goals

**Goals:**

- Extract the structure, section order, and formatting expectations from `paper_bigdata.docx`.
- Extract and condense relevant technical content from `BTL_BigData_.docx`.
- Fill the target template in Vietnamese with concise, source-grounded content.
- Keep the final paper within 7 pages.
- Leave unsupported sections blank and add implementation notes that suggest missing content, tables, figures, or charts.
- Preserve the original files unless an explicit output-copy strategy is selected during implementation.

**Non-Goals:**

- Do not create new experiments, results, datasets, citations, or claims that are not supported by the source report.
- Do not redesign the paper format beyond what is necessary to fit the content.
- Do not implement application features, APIs, or automated document-generation tooling unless needed to safely edit the DOCX.

## Decisions

- Use `paper_bigdata.docx` as the formatting source of truth. This preserves the expected paper layout and avoids introducing a separate markdown-to-docx conversion path that may lose styles.
- Create a working copy for the filled paper before modifying content. This protects the template and makes the final output easier to review or regenerate.
- Read both DOCX files structurally, including paragraphs, tables, and document metadata when available. This is preferable to plain text extraction only because table and heading placement can affect what belongs in a 7-page paper.
- Fill only supported sections with synthesized Vietnamese prose. Where the source lacks sufficient content, leave the section body blank and add a concise note identifying what evidence or material is needed.
- Treat the 7-page limit as a hard acceptance constraint. If content overflows, prioritize abstract/introduction/method/results/conclusion substance and move less critical detail into suggested-table or suggested-figure notes.

## Risks / Trade-offs

- Page-count estimation can vary by Word renderer and installed fonts -> Mitigate by preserving template styles, keeping prose concise, and verifying final pagination in Word-compatible tooling when possible.
- DOCX editing can damage formatting if handled as raw XML without care -> Mitigate by using a DOCX-aware library or minimal targeted XML edits on a copied file.
- The source report may contain long-form report sections that do not map cleanly to paper sections -> Mitigate by summarizing only the strongest matching material and marking weak sections with notes instead of forcing content.
- Notes inside blank sections may count toward the 7-page limit -> Mitigate by keeping notes short, clearly labeled, and only adding them where required by the request.
