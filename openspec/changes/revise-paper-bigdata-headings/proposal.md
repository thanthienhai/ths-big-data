## Why

`paper_bigdata_filled.docx` đã có nội dung chính cho đề tài trợ lý pháp lý thông minh dựa trên Big Data, RAG và tinh chỉnh mô hình Qwen3-4B, nhưng hệ thống đầu mục vẫn cần được rà soát lại theo chuẩn bài báo khoa học. Việc chỉnh sửa đầu mục dựa trực tiếp trên nội dung hiện có trong DOCX giúp paper có mạch nghiên cứu rõ hơn, tách bạch phương pháp - thực nghiệm - kết quả - thảo luận, và chỉ ra chính xác những phần còn thiếu cần bổ sung.

## What Changes

- Rà soát toàn bộ các heading hiện có trong `paper_bigdata_filled.docx` theo tiêu chí bài báo khoa học: mạch lập luận, vai trò từng mục, mức độ phù hợp với đề tài trợ lý pháp lý Big Data/RAG/LLM, và tính cân đối giữa dữ liệu, phương pháp, thực nghiệm, kết quả, thảo luận.
- Sửa hoặc thay thế các đầu mục chung chung hoặc chưa đúng vai trò học thuật, đặc biệt các mục chưa tách rõ kiến trúc hệ thống, dữ liệu pháp luật, truy xuất RAG, fine-tuning, thiết lập đánh giá, kết quả và hạn chế.
- Bổ sung các đầu mục còn thiếu cùng mô tả ngắn cho nội dung cần viết trong từng mục, ví dụ khoảng trống nghiên cứu, baseline, thiết lập thực nghiệm, giao thức đánh giá thủ công, phân tích lỗi, giới hạn và hướng phát triển.
- Giữ nội dung bằng tiếng Việt, văn phong nghiên cứu, có thể dùng trực tiếp để tiếp tục hoàn thiện paper.
- Không thêm kết quả thực nghiệm hoặc khẳng định kỹ thuật chưa có căn cứ; các phần thiếu phải được mô tả như nội dung cần bổ sung, không bịa số liệu.
- Bỏ qua `outline.md`, slide và các dàn ý ngoài DOCX khi xác định đề tài hoặc cấu trúc chính.

## Capabilities

### New Capabilities

- `academic-paper-heading-revision`: Defines requirements for revising and supplementing the heading structure of `paper_bigdata_filled.docx` into a coherent Vietnamese academic paper about a legal-domain Big Data/RAG/LLM assistant, with descriptions for missing sections.

### Modified Capabilities

- None.

## Impact

- Affects the document editing workflow for `paper_bigdata_filled.docx`.
- Requires inspecting the existing DOCX heading structure and content in `paper_bigdata_filled.docx`.
- No application code, APIs, runtime dependencies, or database schemas are expected to change.
