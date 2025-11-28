# Network Simulation Final Project - Group 

> Phân tích hiệu năng mạng Ad-hoc với cơ chế RTS/CTS sử dụng NS-3

## Mục lục

- [Giới thiệu](#giới-thiệu)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
- [Phân tích kết quả](#phân-tích-kết-quả)
- [Kết luận](#kết-luận)

---

## Giới thiệu

Project này nghiên cứu hiệu năng mạng Ad-hoc (peer-to-peer wireless network) với việc bật/tắt cơ chế RTS/CTS (Request to Send / Clear to Send).

### Mục tiêu

1. So sánh hiệu năng mạng khi RTS/CTS bật vs tắt
2. Phân tích ảnh hưởng của số lượng nodes (2-30 nodes)
3. Đánh giá tác động của packet size (512B - 2000B)
4. Xác định điểm tối ưu để bật/tắt RTS/CTS

### Mô hình mạng

- **Topology**: Ad-hoc (không có Access Point)
- **Layout**: Grid 5×N positions
- **Standard**: IEEE 802.11ax (Wi-Fi 6)
- **Protocol**: UDP Echo client-server
- **RTS/CTS Threshold**: 1000 bytes
  - Packet < 1000B → RTS/CTS DISABLED
  - Packet ≥ 1000B → RTS/CTS ENABLED

### Metrics phân tích

- **Throughput** (Kbps): Băng thông thực tế
- **Delay** (ms): Độ trễ trung bình
- **Packet Loss** (%): Tỷ lệ mất gói
- **Jitter** (ms): Dao động độ trễ

---

## Yêu cầu hệ thống

### NS-3
- NS-3 version 3.x trở lên
- Operating System: Linux (Ubuntu 20.04+ khuyến nghị)
- Compiler: g++ 9.0+

### Python
- Python 3.8+
- Libraries: matplotlib, numpy

```bash
pip install matplotlib numpy
```

---

## Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/mindt102/NSFinalProject.git
cd NSFinalProject
```

### 2. Copy source code vào NS-3

```bash
# Copy file C++ vào thư mục scratch của NS-3
cp csma-ca.cc /path/to/ns-3-dev/scratch/
```

### 3. Build NS-3

```bash
cd /path/to/ns-3-dev
./ns3 build
```

---

---

## Hướng dẫn sử dụng

### Chạy simulation cơ bản

```bash
cd ns-3-dev
./ns3 run "csma-ca --nNodes=10 --packetSize=512"
```

### Các tham số command line

```
--nNodes=N              Số lượng nodes (default: 2)
--packetSize=SIZE       Kích thước packet bytes (default: 512)
--maxPackets=N          Số packets tối đa mỗi client (default: 10)
--interval=N            Khoảng cách giữa packets (giây) (default: 1)
--simTime=N             Thời gian simulation (giây) (default: 15)
--verbose=true/false    Bật logging (default: false)
--pcap=true/false       Bật PCAP capture (default: false)
--collectData=true      Chạy từ 2-30 nodes tự động
```

### Ví dụ sử dụng

```bash
# Test với 10 nodes, packet 512B, RTS/CTS OFF
./ns3 run "csma-ca --nNodes=10 --packetSize=512 --verbose=true"

# Test với 10 nodes, packet 1500B, RTS/CTS ON
./ns3 run "csma-ca --nNodes=10 --packetSize=1500 --verbose=true"

# Thu thập dữ liệu toàn diện (2-30 nodes)
./ns3 run "csma-ca --collectData=true --packetSize=512"
```

### Chạy tất cả thí nghiệm

```bash
# Tự động chạy tất cả thí nghiệm
bash run_all_experiments.sh
```

Script sẽ tự động:
1. Test với packet 512B (RTS/CTS OFF) từ 2-30 nodes
2. Test với packet 2000B (RTS/CTS ON) từ 2-30 nodes
3. Test với nhiều packet sizes khác nhau
4. Lưu kết quả vào thư mục results/

---

## Phân tích kết quả

### 1. Phân tích một file XML

```bash
python3 analyze_metrics.py final-10-nodes.xml
```

Output:
- Terminal: Chi tiết 4 metrics + trạng thái từng client
- File CSV: metrics_10nodes.csv

### 2. Phân tích tất cả files

```bash
python3 analyze_metrics.py --all
```

Output:
- Terminal: Tóm tắt tất cả files
- File CSV: metrics_data.csv (tổng hợp)

### 3. Vẽ biểu đồ

```bash
python3 plot_metrics.py
```

Tạo 4 file biểu đồ PNG:
- **4_metrics_analysis.png**: 4 metrics chính (2×2 grid)
- **combined_overview.png**: Throughput vs Delay, Loss vs Lost Clients
- **client_status.png**: Trạng thái Active vs Lost clients
- **all_metrics_dashboard.png**: Dashboard tổng hợp

### 4. So sánh RTS/CTS

```bash
python3 compare_rts_cts.py
```

Yêu cầu: Cần có 2 thư mục results_no_rts/ và results_with_rts/

---

## Kết luận

### Khi nên BẬT RTS/CTS

1. **Số nodes nhiều (>10 nodes)**
   - Xác suất collision tăng cao
   - Hidden node problem nghiêm trọng

2. **Packet size lớn (≥1000 bytes)**
   - Overhead RTS/CTS nhỏ hơn so với data
   - Cost của collision cao hơn

3. **Yêu cầu reliability cao**
   - Mission-critical applications
   - Không chấp nhận mất packet

### Khi nên TẮT RTS/CTS

1. **Số nodes ít (<5 nodes)**
   - Collision rate tự nhiên thấp
   - Overhead không đáng giá

2. **Packet size nhỏ (<1000 bytes)**
   - RTS/CTS overhead lớn hơn data
   - Làm giảm throughput

3. **Yêu cầu latency thấp**
   - Real-time applications (VoIP, gaming)
   - Delay sensitivity cao

### Số liệu thực nghiệm

Với 30 nodes:

| Metric | 512B (RTS/CTS OFF) | 2000B (RTS/CTS ON) | Cải thiện |
|--------|--------------------|--------------------|-----------|
| Packet Loss | 52.3% | 18.7% | -64% |
| Lost Clients | 68.5% | 12.4% | -82% |
| Throughput | 145 Kbps | 387 Kbps | +167% |
| Delay | 2.8 ms | 4.2 ms | +50% |

**Trade-off**: Chấp nhận delay cao hơn 50% để đổi lấy giảm 64% packet loss và tăng 167% throughput.

---

## References

### NS-3 Documentation
- NS-3 Official: https://www.nsnam.org/
- Wi-Fi Module: https://www.nsnam.org/docs/models/html/wifi.html
- FlowMonitor: https://www.nsnam.org/docs/models/html/flow-monitor.html

### Ad-hoc Network
- Wi-Fi Simple Ad-hoc Example: https://www.nsnam.org/doxygen/wifi-simple-adhoc_8cc_source.html
- IEEE 802.11 Standard: https://standards.ieee.org/standard/802_11-2020.html

### RTS/CTS Mechanism
- Disable RTS/CTS: https://ns-3-users.narkive.com/LFdwIHU6/disable-rts-cts

---

## Contact

**GitHub Repository**: https://github.com/mindt102/NSFinalProject.git

**Group Members**: Group 03

---

Last Updated: November 28, 2024
