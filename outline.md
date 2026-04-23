Streaming Hadoop với R
I. Phần Mở Đầu (Giới thiệu về Hadoop Streaming)
•	Hadoop Streaming là gì? 
o	Là một tiện ích đi kèm với Hadoop, cho phép tạo và chạy các công việc (jobs) MapReduce sử dụng bất kỳ tập lệnh (script) hoặc tệp thực thi nào đóng vai trò là Mapper và/hoặc Reducer,.
•	Cơ chế hoạt động: 
o	Hoạt động tương tự như toán tử pipe (|) trong Linux.
o	Tệp văn bản đầu vào được đưa qua luồng chuẩn (stdin) để làm đầu vào cho Mapper, và đầu ra (stdout) của Mapper lại tiếp tục làm đầu vào cho Reducer.
o	Cuối cùng, Reducer ghi đầu ra (output) vào thư mục HDFS.
•	Ưu điểm: 
o	Cho phép các công việc MapReduce được lập trình bằng các ngôn ngữ Non-Java (không phải Java) như R, Python, Ruby, C++, Bash, v.v., chạy trên cụm máy chủ Hadoop,.
o	Rất hữu ích đối với các nhà phân tích R, giúp họ khai thác sức mạnh của Hadoop mà không cần chuyển đổi logic sang Java.
II. Cấu Trúc Và Cú Pháp Cấu Hình (Hadoop Streaming Options)
•	Thành phần chính của một MapReduce Job: Phải có một luồng dữ liệu từ Hadoop Cluster truyền qua luồng xử lý Mapper & Reducer được viết bằng R, sau đó trả về Hadoop Streaming.
•	Cú pháp lệnh thực thi: bin/hadoop command [generic Options] [streaming Options].
•	Các tham số bắt buộc (Streaming Options): 
o	-jar: Chạy thư viện Java chứa tính năng streaming của Hadoop.
o	-input và -output: Chỉ định vị trí dữ liệu đầu vào và thư mục lưu đầu ra trên HDFS.
o	-file: Sao chép các tệp tài nguyên (ví dụ: Mapper, Reducer) đến các Node thực thi (Tasktrackers) ở local.
o	-mapper và -reducer: Khai báo tệp thực thi xử lý kịch bản Map và Reduce.
•	Một số tham số tùy chọn nổi bật: -inputformat và -outputformat (định dạng dữ liệu), -combiner (kết hợp đầu ra của Mapper trước khi đưa vào Reducer), -numReduceTasks (khai báo số lượng Reducers), v.v..
III. Lập Trình Ứng Dụng MapReduce Bằng R
•	Thiết kế luồng xử lý bằng R: Do chúng ta không sử dụng Java, việc cấu hình Driver class là không bắt buộc, chỉ cần viết kịch bản cho Mapper và Reducer.
•	Lập trình Mapper (ví dụ: mapper.R): 
o	Thiết lập kết nối với luồng đầu vào stdin,.
o	Sử dụng vòng lặp while để đọc từng dòng văn bản (ví dụ: readLines(input, n=1)).
o	Sử dụng hàm tách chuỗi (strsplit) để trích xuất cấu trúc (key, value) và gửi kết quả ra stdout qua hàm print() hoặc write().
•	Lập trình Reducer (ví dụ: reducer.R): 
o	Đọc các cặp (key, value) đã được tự động sắp xếp từ đầu ra của Mapper (qua stdin).
o	Sử dụng vòng lặp và câu lệnh if...else để gom nhóm dữ liệu theo Key,.
o	Áp dụng logic tổng hợp và in kết quả ra lại stdout để lưu vào HDFS.
•	Các hàm R cơ bản thông dụng: Giới thiệu ngắn gọn các hàm liên quan đến xử lý I/O như file(), write(), print(), close(), stdin(), stdout(), và sink(),.
IV. Thực Thi, Giám Sát Và Khám Phá Kết Quả
•	Kiểm thử nội bộ (Local Testing): Trước khi đưa lên Hadoop, có thể chạy thử kịch bản R bằng lệnh Linux thông thường: cat input.csv | mapper.R | sort | reducer.R để phát hiện lỗi logic.
•	Thực thi Job: 
o	Có thể chạy trực tiếp từ Terminal / Command Prompt,.
o	Hoặc chạy từ R/RStudio console sử dụng hàm system() để gọi lệnh hệ thống.
•	Theo dõi và Giám sát: 
o	Sử dụng JobTracker console qua giao diện web để theo dõi tiến độ thời gian thực (% hoàn thành Map và Reduce), kiểm tra log, gỡ lỗi khi task bị thất bại (failed),.
•	Đọc Kết quả (Exploring Output): 
o	Khi công việc thành công, HDFS sẽ sinh ra các thư mục _logs và _SUCCESS.
o	Sử dụng lệnh bin/hadoop dfs -cat /thu_muc_ouput/part-* để in kết quả ra màn hình Console (có thể thông qua hàm system() trong RStudio),.
V. Phần Nâng Cao: Tối Ưu Hóa Bằng Gói R HadoopStreaming
•	Giới thiệu gói HadoopStreaming: Đây là một framework đơn giản do David S. Rosenberg phát triển, dùng để chạy MapReduce dễ dàng hơn mà không cần gọi các lệnh streaming quá dài và phức tạp.
•	Tính năng đặc biệt: 
o	Chunkwise data reading: Cho phép đọc/ghi dữ liệu theo từng khối (chunk-wise), giúp ngăn chặn các vấn đề về quá tải bộ nhớ khi làm việc với Big Data.
o	Hỗ trợ nhiều định dạng dữ liệu và gọi tham số dòng lệnh một cách mạnh mẽ.
•	Các hàm quan trọng để đọc dữ liệu: 
o	hsTableReader: Hàm đọc dữ liệu với định dạng bảng.
o	hsKeyValReader: Hàm đọc dữ liệu tồn tại ở cấu trúc cặp (key-value).
o	hsLineReader: Hàm đọc dòng văn bản thô, trả về vectơ chuỗi.
•	Ví dụ minh hoạ: Kịch bản đếm từ (Word count) bằng gói HadoopStreaming với dữ liệu văn bản tiểu thuyết,,,.
VI. Kết Luận & Thảo Luận (Q&A)
•	Tóm tắt lại vai trò của Hadoop Streaming như cầu nối giữa hệ sinh thái phần mềm R và cụm tính toán Hadoop.
•	Cơ hội để các nhà Khoa học Dữ liệu (Data Scientists) phân tích Big Data ngay với ngôn ngữ R quen thuộc mà không cần tốn thời gian xây dựng nền tảng lại từ đầu bằng Java.
•	Hỏi và đáp.
Lưu ý cho người thuyết trình: Bạn có thể chuẩn bị sẵn một máy ảo (Ví dụ: Ubuntu) có cài đặt Hadoop và RStudio để demo trực tiếp cách phân tích bộ dữ liệu (như bài toán phân nhóm trang web hay phân tích cổ phiếu đã trình bày ở phần giữa sách) bằng R console nhằm tăng tính trực quan.

