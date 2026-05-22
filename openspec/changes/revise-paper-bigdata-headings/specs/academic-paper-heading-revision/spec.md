## ADDED Requirements

### Requirement: Use only the DOCX topic as the revision basis
The implementation SHALL use `paper_bigdata_filled.docx` as the authoritative source for the paper topic, scope, and existing content. The implementation MUST NOT use `outline.md`, slide materials, or unrelated source outlines as the basis for deciding the revised section structure.

#### Scenario: Revision source is selected
- **WHEN** the implementation revises the paper headings
- **THEN** the revised structure is derived from the content of `paper_bigdata_filled.docx`, especially the title, abstract, keywords, introduction, methodology, results, and conclusion currently present in that file

### Requirement: Preserve the actual research topic
The revised headings SHALL remain focused on the paper's actual topic: a Vietnamese legal-domain intelligent assistant using Big Data storage/processing, MongoDB, RAG, retrieval, Qwen3-4B fine-tuning with LoRA/QLoRA, and evaluation for legal question answering.

#### Scenario: Topic alignment is checked
- **WHEN** a heading is rewritten or added
- **THEN** it supports the legal-document Big Data, RAG, and LLM fine-tuning research topic rather than introducing Hadoop Streaming, slide-based content, or unrelated technologies

### Requirement: Reframe generic headings into paper-appropriate sections
The implementation SHALL rewrite generic or placeholder headings into academic sections that match the current paper content and improve the research narrative. Revised sections MUST clarify the relationship between problem motivation, data, system architecture, retrieval, model fine-tuning, evaluation, results, limitations, and conclusion.

#### Scenario: Generic heading is found
- **WHEN** the document contains a heading such as a generic system requirement, broad implementation bucket, or placeholder phrase that weakens the academic flow
- **THEN** the heading is replaced with a more specific research-paper heading grounded in the current legal-assistant content

### Requirement: Separate method, experiment, result, and discussion roles
The revised heading structure SHALL distinguish method descriptions from experimental setup, measured results, and interpretation. The implementation MUST NOT place evaluation metrics, claimed results, or limitations under headings where they read as method details.

#### Scenario: Evaluation content is reorganized
- **WHEN** the document discusses BLEU, ROUGE, Exact Match, F1, response time, citation accuracy, hallucination reduction, or manual expert assessment
- **THEN** the related headings place those items under evaluation setup, results, discussion, or limitations as appropriate

### Requirement: Add missing academic sections with descriptions
For necessary academic sections that are missing or underdeveloped in `paper_bigdata_filled.docx`, the implementation SHALL add a heading and a concise Vietnamese description stating what must be written there. The description MUST identify the required evidence or content, such as dataset statistics, train/validation/test split, retrieval configuration, fine-tuning parameters, baseline comparison, expert evaluation protocol, or error analysis.

#### Scenario: Needed evidence is absent
- **WHEN** a section requires information not fully present in `paper_bigdata_filled.docx`
- **THEN** the document includes a section title and a short description of the missing evidence instead of leaving the section blank or inventing details

### Requirement: Avoid unsupported claims and fabricated metrics
The implementation SHALL preserve only claims that are supported by `paper_bigdata_filled.docx` or clearly mark them as content requiring verification. It MUST NOT fabricate benchmark values, training curves, response-time measurements, citation accuracy, or expert-review conclusions.

#### Scenario: Quantitative claim lacks support
- **WHEN** a heading or section implies a quantitative result that is not substantiated in the document
- **THEN** the implementation either rewrites it as an evaluation plan/required evidence item or marks it for verification rather than presenting it as a confirmed result

### Requirement: Keep the revised DOCX editable and coherent
The implementation SHALL save the revised heading structure in `paper_bigdata_filled.docx` or an explicitly named revised DOCX while preserving normal Word editability and practical formatting.

#### Scenario: Revised document is opened
- **WHEN** the user opens the revised document
- **THEN** the heading structure is readable, editable, and coherent as a Vietnamese academic paper on the legal-domain Big Data/RAG/LLM assistant
