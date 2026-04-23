# Streaming Hadoop với R

---

## **PHẦN 1: MỞ ĐẦU**

---

## Slide 1: Bìa chính
**Streaming Hadoop với R**
- Chủ đề: Khai thác Hadoop bằng ngôn ngữ R
- Thời gian: 1 tiếng 30 phút
- Người thuyết trình: [Tên người trình bày]

---

## Slide 2: Mục lục
**Nội dung trình bày**
1. Phần Mở Đầu - Giới thiệu Hadoop Streaming
2. Cấu trúc và Cú pháp cấu hình
3. Lập trình MapReduce bằng R
4. Thực thi, Giám sát và Khám phá Kết quả
5. Phần Nâng cao - Gói HadoopStreaming
6. Kết luận và Hỏi đáp

---

## Slide 3: Hadoop là gì?
*(Mục 1: Phần Mở Đầu)*
**Tổng quan về Hadoop**
- Framework mã nguồn mở xử lý Big Data
- Lưu trữ và xử lý dữ liệu lớn phân tán trên cụm máy
- Core Hadoop gồm: HDFS (lưu trữ) và MapReduce (xử lý)
- Được phát triển bởi Apache Software Foundation

---

## Slide 4: HDFS - Hệ thống tệp phân tán
*(Mục 1: Phần Mở Đầu)*
**Hadoop Distributed File System**
- Lưu trữ dữ liệu lớn trên nhiều máy chủ
- Tự động sao chép dữ liệu (replication)
- Chịu lỗi cao (fault tolerance)
- Truy cập dữ liệu qua các lệnh CLI

---

## Slide 5: MapReduce - Mô hình xử lý
*(Mục 1: Phần Mở Đầu)*
**Xử lý song song dữ liệu lớn**
- Map: Xử lý dữ liệu song song trên nhiều node
- Reduce: Tổng hợp kết quả từ các Map
- Shuffle & Sort: Tự động sắp xếp dữ liệu giữa Map và Reduce
- Chạy trên cụm Hadoop cluster

---

## Slide 6: R - Ngôn ngữ phân tích dữ liệu
*(Mục 1: Phần Mở Đầu)*
**Giới thiệu về R**
- Ngôn ngữ lập trình cho phân tích thống kê và đồ họa
- Cộng đồng mạnh mẽ với hàng nghìn gói thư viện
- Được sử dụng rộng rãi bởi Data Scientists
- Xử lý dữ liệu, thống kê, học máy

---

## Slide 7: Hadoop Streaming là gì?
*(Mục 1: Phần Mở Đầu)*
**Cầu nối giữa R và Hadoop**
- Tiện ích đi kèm Hadoop
- Cho phép viết MapReduce bằng ngôn ngữ khác (R, Python...)
- Không cần lập trình Java
- Dữ liệu truyền qua stdin/stdout

---

## Slide 8: Ưu điểm của Hadoop Streaming
*(Mục 1: Phần Mở Đầu)*
**Tại sao nên dùng?**
- Tận dụng kỹ năng R có sẵn
- Không cần học Java để dùng Hadoop
- Cộng đồng R mạnh cho phân tích dữ liệu
- Đơn giản, dễ tiếp cận

---

## **PHẦN 2: CẤU TRÚC VÀ CÚ PHÁP CẤU HÌNH**

---

## Slide 8: Cấu trúc MapReduce Job
*(Mục 2: Cấu trúc và Cú pháp cấu hình)*
**Thành phần chính**
- Hadoop Cluster (Resource Manager)
- Data Flow qua Streaming
- Mapper & Reducer viết bằng R
- Kết quả lưu vào HDFS

---

## Slide 9: Cú pháp lệnh thực thi
*(Mục 2: Cấu trúc và Cú pháp cấu hình)*
**Cấu trúc câu lệnh**
```bash
bin/hadoop command [generic Options] [streaming Options]
```

---

## Slide 10: Các tham số bắt buộc
*(Mục 2: Cấu trúc và Cú pháp cấu hình)*
**Streaming Options cần thiết**
- `-jar`: Chạy thư viện Java streaming
- `-input`: Thư mục dữ liệu đầu vào HDFS
- `-output`: Thư mục lưu kết quả trên HDFS
- `-file`: Sao chép tài nguyên đến TaskTrackers
- `-mapper`: Khai báo tệp Mapper
- `-reducer`: Khai báo tệp Reducer

---

## Slide 11: Ví dụ lệnh Hadoop Streaming
*(Mục 2: Cấu trúc và Cú pháp cấu hình)*
**Cấu hình cơ bản**
```bash
bin/hadoop jar hadoop-streaming.jar \
  -input /input/data \
  -output /output/result \
  -mapper mapper.R \
  -reducer reducer.R \
  -file mapper.R \
  -file reducer.R
```

---

## Slide 12: Các tham số tùy chọn
*(Mục 2: Cấu trúc và Cú pháp cấu hình)*
**Tùy chỉnh thêm**
- `-inputformat`: Định dạng dữ liệu đầu vào
- `-outputformat`: Định dạng dữ liệu đầu ra
- `-combiner`: Kết hợp đầu ra Mapper
- `-numReduceTasks`: Số lượng Reducers
- `-partitioner`: Phân chia dữ liệu theo Key

---

## **PHẦN 3: LẬP TRÌNH MAPREDUCE BẰNG R**

---

## Slide 13: Thiết kế luồng xử lý bằng R
*(Mục 3: Lập trình MapReduce bằng R)*
**Không cần Java Driver**
- Không cần cấu hình Driver class
- Chỉ cần viết script cho Mapper và Reducer
- Rất đơn giản và trực tiếp

---

## Slide 14: Lập trình Mapper bằng R
*(Mục 3: Lập trình MapReduce bằng R)*
**Cấu trúc cơ bản**
```r
# mapper.R
input <- file("stdin", "r")
while (length(line <- readLines(input, n=1)) > 0) {
  # Xử lý dòng dữ liệu
  words <- unlist(strsplit(line, " "))
  for (w in words) {
    cat(w, "1\n")
  }
}
close(input)
```

---

## Slide 15: Giải thích Mapper
*(Mục 3: Lập trình MapReduce bằng R)*
**Các bước thực hiện**
1. Thiết lập kết nối stdin
2. Đọc từng dòng văn bản (readLines)
3. Tách chuỗi bằng strsplit
4. Xuất cặp (key, value) ra stdout

---

## Slide 16: Lập trình Reducer bằng R
*(Mục 3: Lập trình MapReduce bằng R)*
**Cấu trúc cơ bản**
```r
# reducer.R
input <- file("stdin", "r")
current_key <- NULL
count <- 0
while (length(line <- readLines(input, n=1)) > 0) {
  parts <- strsplit(line, " ")
  key <- parts[[1]][1]
  val <- as.integer(parts[[1]][2])
  # Xử lý logic tổng hợp
}
close(input)
```

---

## Slide 17: Giải thích Reducer
*(Mục 3: Lập trình MapReduce bằng R)*
**Các bước thực hiện**
1. Đọc cặp (key, value) đã sắp xếp
2. Gom nhóm theo Key
3. Áp dụng logic tổng hợp
4. In kết quả ra stdout

---

## Slide 18: Các hàm R cơ bản
*(Mục 3: Lập trình MapReduce bằng R)*
**I/O functions trong R**
- `file()`: Mở kết nối file
- `stdin()`: Luồng đầu vào chuẩn
- `stdout()`: Luồng đầu ra chuẩn
- `readLines()`: Đọc từng dòng
- `write()`/`cat()`: Ghi dữ liệu
- `sink()`: Chuyển hướng output

---

## **PHẦN 4: THỰC THI, GIÁM SÁT VÀ ĐÁNH GIÁ KẾT QUẢ**

---

## Slide 19: Kiểm thử nội bộ
*(Mục 4: Thực thi, Giám sát và Khám phá Kết quả)*
**Local Testing trước khi deploy**
```bash
cat input.csv | Rscript mapper.R | sort | Rscript reducer.R
```
- Phát hiện lỗi logic trước khi đưa lên Hadoop
- Tiết kiệm thời gian và tài nguyên

---

## Slide 20: Thực thi Job
*(Mục 4: Thực thi, Giám sát và Khám phá Kết quả)*
**Cách chạy Job**
- Từ Terminal/Command Prompt trực tiếp
- Từ R/RStudio console:
```r
system("bin/hadoop jar hadoop-streaming.jar \
  -input /input/data \
  -output /output/result \
  -mapper mapper.R \
  -reducer reducer.R")
```

---

## Slide 21: Theo dõi tiến độ
*(Mục 4: Thực thi, Giám sát và Khám phá Kết quả)*
**JobTracker Web Console**
- Xem % hoàn thành Map và Reduce
- Kiểm tra log chi tiết
- Gỡ lỗi khi task thất bại
- Thông tin tài nguyên sử dụng

---

## Slide 22: Giám sát Job
*(Mục 4: Thực thi, Giám sát và Khám phá Kết quả)*
**Các trạng thái Job**
- Running: Đang chạy
- Succeeded: Hoàn thành thành công
- Failed: Thất bại
- Pending: Đang chờ

---

## Slide 23: Khám phá kết quả
*(Mục 4: Thực thi, Giám sát và Khám phá Kết quả)*
**Đọc output từ HDFS**
- Thư mục `_logs`: Log chi tiết
- File `_SUCCESS`: Xác nhận thành công
- Xem kết quả:
```bash
bin/hadoop dfs -cat /output/result/part-*
```

---

## Slide 24: Đọc kết quả từ R
*(Mục 4: Thực thi, Giám sát và Khám phá Kết quả)*
**Sử dụng system() trong RStudio**
```r
result <- system("bin/hadoop dfs -cat /output/result/part-*", 
                intern = TRUE)
print(result)
```

---

## **PHẦN 5: PHẦN NÂNG CAO - GÓI HADOOPSTREAMING**

---

## Slide 25: HadoopStreaming Package
*(Mục 5: Phần Nâng cao - Gói HadoopStreaming)*
**Giới thiệu gói hỗ trợ**
- Framework do David S. Rosenberg phát triển
- Đơn giản hóa việc gọi streaming commands
- Không cần viết lệnh dài và phức tạp

---

## Slide 26: Tính năng đặc biệt
*(Mục 5: Phần Nâng cao - Gói HadoopStreaming)*
**Chunkwise Data Reading**
- Đọc/ghi dữ liệu theo từng khối (chunk)
- Ngăn chặn quá tải bộ nhớ khi xử lý Big Data
- Hỗ trợ nhiều định dạng dữ liệu

---

## Slide 27: Hàm hsTableReader
*(Mục 5: Phần Nâng cao - Gói HadoopStreaming)*
**Đọc dữ liệu dạng bảng**
```r
hsTableReader(file, nrows = -1, ...,
              colClasses = NULL, verbose = TRUE)
```
- Đọc dữ liệu với định dạng bảng
- Hỗ trợ chỉ định số dòng đọc

---

## Slide 28: Hàm hsKeyValReader
*(Mục 5: Phần Nâng cao - Gói HadoopStreaming)*
**Đọc dữ liệu dạng Key-Value**
```r
hsKeyValReader(file, verbose = TRUE)
```
- Đọc dữ liệu ở cấu trúc cặp (key-value)
- Phù hợp với dữ liệu đã qua Shuffle

---

## Slide 29: Hàm hsLineReader
*(Mục 5: Phần Nâng cao - Gói HadoopStreaming)*
**Đọc dòng văn bản thô**
```r
hsLineReader(file, skip = 0, n = -1, verbose = TRUE)
```
- Trả về vector chuỗi
- Đọc dòng văn bản thô

---

## Slide 30: Ví dụ Word Count
*(Mục 5: Phần Nâng cao - Gói HadoopStreaming)*
**Kịch bản đếm từ với HadoopStreaming**
- Dữ liệu: Văn bản tiểu thuyết
- Mapper: Tách từ, đếm mỗi từ xuất hiện 1 lần
- Reducer: Tổng hợp số lần xuất hiện của mỗi từ

---

## Slide 31: Demo Word Count
*(Mục 5: Phần Nâng cao - Gói HadoopStreaming)*
**Triển khai thực tế**
1. Chuẩn bị dữ liệu văn bản
2. Chạy MapReduce job
3. Thu thập và phân tích kết quả

---

## **PHẦN 6: KẾT LUẬN VÀ HỎI ĐÁP**

---

## Slide 32: Tóm tắt phần 1
*(Mục 6: Kết luận và Hỏi đáp)*
**Hadoop Streaming**
- Cầu nối giữa R và Hadoop
- Cho phép lập trình MapReduce bằng R
- Không cần học Java

---

## Slide 33: Tóm tắt phần 2
*(Mục 6: Kết luận và Hỏi đáp)*
**Các điểm chính**
- Cú pháp và tham số cấu hình
- Lập trình Mapper và Reducer bằng R
- Kiểm thử và giám sát job
- HadoopStreaming package

---

## Slide 34: Cơ hội nghề nghiệp
*(Mục 6: Kết luận và Hỏi đáp)*
**Big Data với R**
- Data Scientists phân tích Big Data bằng R
- Không cần xây dựng nền tảng lại từ đầu
- Tận dụng kỹ năng R có sẵn

---

## Slide 35: Hỏi và Đáp
*(Mục 6: Kết luận và Hỏi đáp)*
**Q&A**
- Cảm ơn các bạn đã lắng nghe!
- Thắc mắc và câu hỏi?
