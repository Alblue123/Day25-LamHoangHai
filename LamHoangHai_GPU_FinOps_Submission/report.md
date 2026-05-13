# BÁO CÁO KẾT QUẢ LAB: GPU FINOPS & COST OPTIMIZATION

**Sinh viên:** Lam Hoang Hai  
**MSSV:** 2A202600090  
**Ngày hoàn thành:** 13/05/2026

---

## 1. Giới thiệu
Mục tiêu của bài lab là tìm hiểu và thực hành các nguyên tắc FinOps trong quản lý tài nguyên GPU. Bài lab tập trung vào việc giám sát (monitoring), tối ưu hóa chi phí (cost optimization) thông qua Spot Instances, Autoscaling và phân tích lãng phí tài nguyên.

---

## 2. Phân tích chi tiết các phần

### Part 1-4: Giám sát và Quản lý Cluster
- **Cluster Monitoring:** Hệ thống đã giám sát thành công 4 nodes với tổng cộng 8 GPUs (T4, A100, V100). Hiệu suất sử dụng (utilization) trung bình đạt mức cao (~82.1%).
- **Workload & Billing:** Các workload (ResNet, BERT, LLM) đã được xử lý và ghi nhận chi phí thực tế. Tổng chi phí ghi nhận là $2.4552, trong đó đã tiết kiệm được $2.6018 nhờ sử dụng Spot Instances.
- **Spot Instances:** Việc sử dụng cơ chế đấu giá Spot giúp giảm chi phí đáng kể (~32-70%). Hệ thống đã xử lý thành công sự kiện preemption (thu hồi tài nguyên) mà vẫn đảm bảo tính liên tục của công việc.
- **Autoscaling:** Chính sách autoscaling đã được cấu hình lại với ngưỡng 70%. Hệ thống đã tự động kích hoạt scale-up từ 4 lên 5 nodes khi utilization vượt ngưỡng.

### Part 5-7: Tối ưu hóa và Quy trình FinOps
- **Waste Analysis:** Báo cáo ghi nhận tỷ lệ lãng phí trung bình khoảng 16.8% do tài nguyên idle. Ước tính có thể tiết kiệm tới $1668/tháng nếu tối ưu hóa triệt để.
- **Recommendations:** Hệ thống đề xuất chuyển đổi các workload không khẩn cấp sang Spot Instances và lập lịch chạy vào giờ thấp điểm.
- **Full Workflow:** Đã thực hiện quy trình tối ưu hóa khép kín từ khâu submit workload -> monitoring -> scaling -> cost snapshot.

### Part 8: Real GPU Training (FP32 vs AMP)
- **Kết quả:** Quá trình huấn luyện mô hình ResNet-18 trên GPU thực tế cho thấy Mixed Precision (AMP) giúp giảm thời gian huấn luyện từ ~120s xuống còn ~75s (giảm khoảng 37.5%).
- **Chi phí:** Nhờ thời gian chạy ngắn hơn, chi phí huấn luyện trên GPU thực tế cũng giảm tương ứng, giúp tối ưu hóa ngân sách dự án.

### Part 8.5: Advanced Cost Optimization
- **Multi-GPU Scaling:** Phân tích cho thấy hiệu suất scaling giảm dần khi tăng số lượng GPU (8 GPUs đạt ~76% efficiency). Do đó, việc chọn số lượng GPU tối ưu là cực kỳ quan trọng để cân bằng giữa thời gian và chi phí.
- **Project Forecasting:** Dự báo ngân sách cho dự án với độ tin cậy 95%, giúp doanh nghiệp chủ động trong kế hoạch tài chính.
- **Strategy Design:** Kết hợp AMP và Spot Instances cho dự án LLM Fine-tuning giúp giảm chi phí tới 74.5%, đưa dự án từ mức vượt ngân sách về mức an toàn ($1,497 so với $5,000 budget).

---

## 3. Kết luận và Học hỏi
- **Kỹ năng đạt được:** Sử dụng Docker để giả lập cluster GPU, gọi API quản lý billing, cấu hình chính sách autoscaling dựa trên chi phí.
- **Bài học:** FinOps không chỉ là tiết kiệm tiền mà là việc đưa ra các quyết định sáng suốt dựa trên dữ liệu để tối đa hóa giá trị kinh doanh từ mỗi USD chi cho Cloud/GPU.
- **Ứng dụng:** Các chiến lược như AMP và Spot Instances nên được ưu tiên hàng đầu trong mọi dự án Deep Learning để tiết kiệm tài nguyên.

---
*Báo cáo được tạo tự động dựa trên kết quả thực thi Notebook.*
