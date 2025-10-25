# 📖 Hướng dẫn sử dụng AI Smart Scheduler

## 🎯 AI Smart Scheduler là gì?

AI Smart Scheduler là tính năng thông minh giúp bạn tự động tìm khung giờ họp tối ưu cho team mà không cần tìm kiếm thủ công. AI sẽ:
- Phân tích lịch bận của tất cả thành viên
- Học thói quen từ lịch sử đặt phòng
- Dự đoán xác suất tham dự
- Đề xuất 3 khung giờ tốt nhất

---

## 🚀 Cách sử dụng

### 1. Truy cập AI Smart Scheduler

**Cách 1:** Từ menu navigation
- Click vào **"AI Smart Scheduler"** trên thanh menu

**Cách 2:** Từ Dashboard
- Vào Dashboard
- Click nút **"AI Smart Scheduler"** trong phần "Thao tác nhanh"

**Cách 3:** Từ trang chủ
- Click nút **"Dùng AI ngay"** trong banner AI

---

### 2. Tìm khung giờ tối ưu

#### Bước 1: Click "Tìm ngay"
- Trên trang AI Smart Scheduler
- Click vào card **"Tìm Khung Giờ Tối Ưu"**
- Click nút **"Tìm ngay"**

#### Bước 2: Điền thông tin
Modal sẽ hiện ra với các trường:

**Thông tin cơ bản:**
- **Thời lượng meeting**: Chọn 30, 60, 90, hoặc 120 phút
- **Số ngày tìm kiếm**: Tìm trong 7, 14, 21, hoặc 30 ngày tới

**Tối ưu hóa:**
- **Mục tiêu tối ưu**:
  - `Cân bằng` (Khuyến nghị) - Tối ưu nhiều yếu tố
  - `Tối đa người tham dự` - Nhiều người nhất
  - `Tối đa xác suất` - Xác suất cao nhất
  - `Công bằng` - Không thiên vị nhóm nào
  - `Ưu tiên Mentor` - Ưu tiên có mentor

- **Số lượng đề xuất**: 3, 5, hoặc 10 slots

**Ràng buộc:**
- **Số người tối thiểu**: Ví dụ: 3 (chỉ đề xuất slots có ít nhất 3 người)
- **Khung giờ**: 
  - Giờ bắt đầu: Ví dụ 9 (9h sáng)
  - Giờ kết thúc: Ví dụ 18 (6h chiều)
- **Filter theo CLB** (tùy chọn): Chỉ Pro, Multi, GCC, hoặc tất cả

#### Bước 3: Xem kết quả
AI sẽ phân tích và hiển thị kết quả với:
- **Điểm số** của mỗi slot
- **Ngày giờ** cụ thể
- **Số người available** và **Kỳ vọng tham dự**
- **Số mentor** có thể tham gia
- **Top attendees** với xác suất tham dự

#### Bước 4: Chọn slot
- Click nút **"Chọn slot này"** 
- Bạn sẽ được chuyển đến form đặt phòng với thời gian đã điền sẵn

---

### 3. Tạo Poll tự động

#### Bước 1: Click "Tạo Poll"
- Trên trang AI Smart Scheduler
- Click vào card **"Tạo Poll Tự Động"**
- Click nút **"Tạo Poll"**

#### Bước 2: Điền thông tin
- **Tiêu đề Meeting**: Ví dụ "Weekly Team Sync"
- **Thời lượng**: 30, 60, 90, hoặc 120 phút
- **Số người tối thiểu**: Ví dụ 3

#### Bước 3: Xem Poll
AI tự động tạo poll với **3 khung giờ** dựa trên 3 mục tiêu:
1. **Tối đa người tham dự** - Slot có nhiều người nhất
2. **Cân bằng** - Slot cân bằng nhiều yếu tố
3. **Ưu tiên Mentor** - Slot có mentor

Mỗi option hiển thị:
- Thời gian
- Số người available
- Kỳ vọng tham dự
- Số mentor
- Điểm số

#### Bước 4: Chọn option
- Click nút **"Chọn"** trên option bạn thích
- Chuyển đến form đặt phòng

---

## 💡 Tips sử dụng hiệu quả

### 1. Chọn mục tiêu phù hợp

| Mục tiêu | Khi nào dùng | Ví dụ |
|----------|--------------|-------|
| **Cân bằng** | Hầu hết trường hợp | Meeting thường xuyên |
| **Tối đa người** | Cần nhiều người | All-hands meeting |
| **Tối đa xác suất** | Quan trọng, cần chắc chắn | Quarterly review |
| **Công bằng** | Tránh thiên vị | Cross-team sync |
| **Ưu tiên Mentor** | Cần hướng dẫn | Training, Workshop |

### 2. Điều chỉnh constraints

**Nếu không tìm thấy slot:**
- ✅ Giảm số người tối thiểu
- ✅ Tăng số ngày tìm kiếm
- ✅ Nới rộng khung giờ
- ✅ Bỏ filter CLB

**Nếu có quá nhiều slots:**
- ✅ Tăng số người tối thiểu
- ✅ Thu hẹp khung giờ
- ✅ Thêm filter CLB

### 3. Hiểu kết quả

**Điểm số (Score):**
- Cao hơn = Tốt hơn
- Kết hợp nhiều yếu tố: attendance, mentor, thời gian...

**Available vs Kỳ vọng:**
- **Available**: Số người không bận (theo lịch)
- **Kỳ vọng**: Số người thực tế sẽ tham dự (dựa trên xác suất)

**Xác suất tham dự:**
- Dựa trên lịch sử đặt phòng
- Học thói quen của từng user
- Càng cao càng đáng tin cậy

### 4. Khi nào dùng Poll?

✅ **Dùng Poll khi:**
- Không chắc chắn thời gian nào tốt nhất
- Muốn có nhiều lựa chọn
- Cần so sánh các mục tiêu khác nhau

✅ **Dùng Tìm slot khi:**
- Đã biết rõ mục tiêu
- Cần nhiều hơn 3 options
- Muốn custom constraints chi tiết

---

## 🎓 Ví dụ thực tế

### Scenario 1: Weekly Standup
**Mục tiêu:** Meeting hàng tuần, cần ổn định

**Cách làm:**
1. Chọn "Tìm khung giờ"
2. Thời lượng: 30 phút
3. Mục tiêu: **Cân bằng**
4. Số người tối thiểu: 5
5. Khung giờ: 9h - 18h
6. Số ngày: 7

**Kết quả:** AI đề xuất slot cân bằng tốt cho meeting định kỳ

---

### Scenario 2: Workshop với Mentor
**Mục tiêu:** Training, cần mentor hướng dẫn

**Cách làm:**
1. Chọn "Tạo Poll"
2. Tiêu đề: "Python Workshop"
3. Thời lượng: 120 phút
4. Số người tối thiểu: 8

**Kết quả:** Poll với 3 options, một trong đó ưu tiên mentor

---

### Scenario 3: All-hands Meeting
**Mục tiêu:** Cần tối đa số người tham dự

**Cách làm:**
1. Chọn "Tìm khung giờ"
2. Thời lượng: 60 phút
3. Mục tiêu: **Tối đa người tham dự**
4. Số người tối thiểu: 15
5. Khung giờ: 13h - 17h (tránh buổi sáng)
6. Số ngày: 14

**Kết quả:** Slot có nhiều người available nhất

---

## ❓ FAQ

### Q: AI học từ đâu?
**A:** AI học từ:
- Lịch sử booking của bạn và team
- Thời gian bận đã đánh dấu
- Pattern thói quen (giờ nào hay đặt phòng, ngày nào active...)

### Q: Kết quả có chính xác không?
**A:** 
- Càng nhiều data lịch sử → Càng chính xác
- User mới: xác suất dựa trên default (70%)
- User có lịch sử: xác suất học từ behavior thực tế

### Q: Tại sao không tìm thấy slot?
**A:** Có thể do:
- Constraints quá chặt (quá nhiều người, khung giờ hẹp...)
- Không đủ data về availability
- Thử nới lỏng constraints hoặc tăng số ngày

### Q: Sự khác biệt giữa các mục tiêu?
**A:** 
- **Cân bằng**: Tốt nhất cho hầu hết case
- **Tối đa người**: Quan tâm số lượng hơn chất lượng
- **Tối đa xác suất**: Đảm bảo attendance cao
- **Công bằng**: Không thiên vị một nhóm
- **Ưu tiên Mentor**: Tập trung vào mentor

### Q: Có thể lưu Poll không?
**A:** Hiện tại chưa có tính năng lưu poll. Bạn nên:
- Screenshot kết quả
- Hoặc chọn slot ngay và đặt phòng

### Q: AI có tự động đặt phòng không?
**A:** Không. AI chỉ **đề xuất**, bạn vẫn phải:
1. Chọn slot
2. Xác nhận thông tin
3. Đặt phòng thủ công

---

## 🆘 Troubleshooting

### Lỗi: "Không thể kết nối với AI Agent"
**Giải pháp:**
- Refresh trang
- Kiểm tra internet
- Thử lại sau vài giây

### Lỗi: "Không tìm thấy slot"
**Giải pháp:**
1. Giảm số người tối thiểu
2. Tăng số ngày tìm kiếm
3. Nới rộng khung giờ
4. Bỏ filter CLB

### Kết quả không như mong đợi
**Kiểm tra:**
- Đã cập nhật thời gian bận chưa?
- Có đủ lịch sử booking chưa?
- Constraints có hợp lý không?

---

## 📞 Hỗ trợ

Cần trợ giúp? Liên hệ:
- Admin CLB của bạn
- Hoặc email: support@clubsync.ai

---

**Chúc bạn sử dụng AI Smart Scheduler hiệu quả! 🎉**
