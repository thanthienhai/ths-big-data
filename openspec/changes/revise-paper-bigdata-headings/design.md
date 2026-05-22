## Context

`paper_bigdata_filled.docx` hiện đã có khung bài báo tiếng Việt cho đề tài "Nghiên cứu huấn luyện và tinh chỉnh mô hình ngôn ngữ lớn cho nhiệm vụ phản hồi văn bản pháp luật Việt Nam". Nội dung chính trong DOCX xoay quanh dữ liệu pháp luật Việt Nam, Big Data, MongoDB, RAG, Hybrid Search, Reranking, Qwen3-4B, LoRA/QLoRA, Google Colab và đánh giá hỏi đáp pháp lý. Vì vậy, việc chỉnh sửa đầu mục phải xuất phát từ chính DOCX này, không dùng `outline.md`, slide, hoặc dàn ý ngoài tài liệu làm căn cứ đề tài.

Stakeholder chính là người viết paper cần một cấu trúc đầu mục đủ chuẩn nghiên cứu để tiếp tục hoàn thiện nội dung. Output phải ưu tiên tính học thuật, tính đúng đề tài pháp lý Big Data/RAG/LLM, và khả năng dùng trực tiếp trong DOCX.

## Goals / Non-Goals

**Goals:**

- Chỉnh sửa hệ thống heading của `paper_bigdata_filled.docx` để phù hợp với bài báo về trợ lý pháp lý thông minh sử dụng Big Data, RAG và fine-tuning LLM.
- Thay các heading chung chung bằng các mục có vai trò nghiên cứu rõ ràng: bối cảnh, khoảng trống, dữ liệu pháp luật, kiến trúc hệ thống, truy xuất RAG, fine-tuning, thiết lập đánh giá, kết quả, thảo luận, hạn chế, kết luận.
- Bổ sung heading còn thiếu kèm mô tả ngắn, nêu rõ nội dung cần viết hoặc bằng chứng cần có.
- Giữ văn phong tiếng Việt học thuật, súc tích, có thể tiếp tục phát triển thành paper hoàn chỉnh.
- Không bịa kết quả định lượng; nếu thiếu dữ liệu thực nghiệm, ghi rõ mục đó cần bổ sung loại số liệu, bảng, hình hoặc log nào.

**Non-Goals:**

- Không viết lại toàn bộ nội dung paper từ đầu.
- Không tự tạo kết quả benchmark, số liệu hiệu năng, hình ảnh hoặc bảng không có nguồn.
- Không thay đổi template trình bày ngoài phạm vi cần thiết để cập nhật heading và mô tả mục.
- Không dùng `outline.md`, slide, hoặc tài liệu ngoài DOCX để thay đổi đề tài paper.
- Không triển khai phần mềm, pipeline huấn luyện, crawler, hệ thống RAG, hoặc script đánh giá trong change này.

## Decisions

1. Treat the DOCX as the only source of truth for the paper topic.

   The implementation should inspect and edit `paper_bigdata_filled.docx` directly, preferably with a structured DOCX library such as `python-docx` if available. The title, abstract, keywords, introduction, method sections, result sections, and conclusion in this DOCX determine the revised headings. Alternative considered: using `outline.md` or slide material for structure. That is rejected because those sources do not represent the current paper topic.

2. Improve heading specificity without changing the research topic.

   Headings should clarify the legal-domain Big Data/RAG/LLM contribution: legal data pipeline, MongoDB schema and chunking, retrieval design, Qwen3-4B LoRA/QLoRA fine-tuning, evaluation protocol, results, limitations, and future work. Alternative considered: leaving generic headings such as "Yêu cầu hệ thống" or "Các gợi ý nâng cao" unchanged. That would weaken the academic narrative.

3. Separate method, experiment, results, and discussion.

   The revised outline should avoid mixing system design, training setup, metrics, results, and limitations inside broad sections. Evaluation metrics such as BLEU, ROUGE, Exact Match, F1, citation accuracy, hallucination behavior, and response time should sit under evaluation setup, results, discussion, or limitations. Alternative considered: keeping all content under "Phương pháp và tư liệu". That makes the paper harder to evaluate scientifically.

4. Represent missing content as section descriptions with evidence requirements.

   When a section lacks enough source material, the implementation should insert a concise description such as "Mục này cần bổ sung..." and specify expected artifacts: dataset statistics, train/validation/test split, fine-tuning parameters, baseline comparison, retrieval settings, expert evaluation protocol, or error analysis. Alternative considered: drafting full paragraphs without source evidence. That risks unsupported claims.

## Risks / Trade-offs

- [Risk] DOCX styling may not map cleanly through a library edit -> Mitigation: preserve existing heading paragraph styles where possible and limit edits to text-level replacement/insertion.
- [Risk] The current paper may contain body text tied to old headings -> Mitigation: update heading text first, then add short descriptions for gaps so the next implementation pass can reconcile body paragraphs.
- [Risk] A stricter Q1-style structure may exceed the original 7-page constraint from earlier work -> Mitigation: keep headings and gap descriptions concise, and defer full content expansion to later paper-writing tasks.
- [Risk] Some sections need empirical data that is absent -> Mitigation: mark the exact missing evidence instead of inventing results.
