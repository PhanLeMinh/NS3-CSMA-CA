import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
import glob
import os

def parse_flowmonitor_xml(filename):
    """
    Parse FlowMonitor XML file and extract important metrics
    """
    tree = ET.parse(filename)
    root = tree.getroot()
    
    # Extract number of nodes from filename (e.g., final-2-nodes.xml -> 2)
    num_nodes = int(filename.split('-')[1])
    
    # Initialize counters
    total_clients = 0
    lost_clients = 0
    total_tx_packets = 0
    total_rx_packets = 0
    total_lost_packets = 0
    total_delay = 0
    total_throughput = 0
    
    flows_data = []
    
    # Parse FlowStats
    for flow in root.findall('.//FlowStats/Flow'):
        flow_id = flow.get('flowId')
        
        # Safely get attributes with default values
        tx_packets = int(flow.get('txPackets', 0))
        rx_packets = int(flow.get('rxPackets', 0))
        lost_packets = int(flow.get('lostPackets', 0))
        tx_bytes = int(flow.get('txBytes', 0))
        rx_bytes = int(flow.get('rxBytes', 0))
        
        # Extract time information (in nanoseconds)
        time_first_tx_str = flow.get('timeFirstTxPacket', '+0ns')
        time_last_rx_str = flow.get('timeLastRxPacket', '+0ns')
        
        time_first_tx = float(time_first_tx_str.replace('ns', '').replace('+', '').replace('e', 'e'))
        time_last_rx = float(time_last_rx_str.replace('ns', '').replace('+', '').replace('e', 'e'))
        
        # Calculate duration in seconds
        duration = (time_last_rx - time_first_tx) / 1e9 if time_last_rx > time_first_tx else 0
        
        # Calculate throughput (bytes/second)
        throughput = (rx_bytes * 8) / duration if duration > 0 else 0  # in bits per second
        
        # Extract delay (in nanoseconds)
        delay_sum_str = flow.get('delaySum', '+0ns')
        delay_sum = float(delay_sum_str.replace('ns', '').replace('+', '').replace('e', 'e'))
        avg_delay = (delay_sum / rx_packets) / 1e6 if rx_packets > 0 else 0  # convert to milliseconds
        
        flows_data.append({
            'flow_id': flow_id,
            'tx_packets': tx_packets,
            'rx_packets': rx_packets,
            'lost_packets': lost_packets,
            'tx_bytes': tx_bytes,
            'rx_bytes': rx_bytes,
            'throughput_bps': throughput,
            'avg_delay_ms': avg_delay,
            'duration_s': duration
        })
        
        total_tx_packets += tx_packets
        total_rx_packets += rx_packets
        total_lost_packets += lost_packets
        total_throughput += throughput
        
    # Parse Ipv4FlowClassifier to identify client flows
    for flow in root.findall('.//Ipv4FlowClassifier/Flow'):
        src_addr = flow.get('sourceAddress')
        dst_addr = flow.get('destinationAddress')
        dst_port = flow.get('destinationPort')
        
        # Identify client->server flows (destination port 9 is the server)
        if dst_port == '9':
            total_clients += 1
            flow_id = flow.get('flowId')
            
            # Check if this client lost all packets
            for flow_stat in flows_data:
                if flow_stat['flow_id'] == flow_id:
                    if flow_stat['rx_packets'] == 0:
                        lost_clients += 1
                    break
    
    # Calculate packet loss rate
    packet_loss_rate = (total_lost_packets / total_tx_packets * 100) if total_tx_packets > 0 else 0
    
    # Calculate lost client ratio
    lost_client_ratio = (lost_clients / total_clients * 100) if total_clients > 0 else 0
    
    return {
        'num_nodes': num_nodes,
        'total_clients': total_clients,
        'lost_clients': lost_clients,
        'lost_client_ratio': lost_client_ratio,
        'total_tx_packets': total_tx_packets,
        'total_rx_packets': total_rx_packets,
        'total_lost_packets': total_lost_packets,
        'packet_loss_rate': packet_loss_rate,
        'avg_throughput_bps': total_throughput / len(flows_data) if flows_data else 0,
        'flows': flows_data
    }

def analyze_all_files(pattern='final-*-nodes.xml'):
    """
    Analyze all FlowMonitor XML files matching the pattern
    """
    files = sorted(glob.glob(pattern), key=lambda x: int(x.split('-')[1]))
    
    if not files:
        print(f"Không tìm thấy file nào với pattern: {pattern}")
        return None
    
    results = []
    
    print("=" * 80)
    print("PHÂN TÍCH KẾT QUẢ MÔ PHỎNG MẠNG AD-HOC")
    print("=" * 80)
    print()
    
    for filename in files:
        print(f"Đang phân tích: {filename}")
        result = parse_flowmonitor_xml(filename)
        results.append(result)
        
        # Print summary for each file
        print(f"  Số nodes: {result['num_nodes']}")
        print(f"  Số clients: {result['total_clients']}")
        print(f"  Clients bị mất kết nối: {result['lost_clients']} ({result['lost_client_ratio']:.2f}%)")
        print(f"  Tổng packets gửi: {result['total_tx_packets']}")
        print(f"  Tổng packets nhận: {result['total_rx_packets']}")
        print(f"  Tỷ lệ mất gói: {result['packet_loss_rate']:.2f}%")
        print(f"  Throughput trung bình: {result['avg_throughput_bps']/1000:.2f} Kbps")
        print()
    
    return results

def plot_results(results):
    """
    Create visualizations from the analysis results
    """
    if not results:
        print("Không có dữ liệu để vẽ biểu đồ")
        return
    
    nodes = [r['num_nodes'] for r in results]
    lost_client_ratio = [r['lost_client_ratio'] for r in results]
    packet_loss_rate = [r['packet_loss_rate'] for r in results]
    throughput = [r['avg_throughput_bps']/1000 for r in results]  # Convert to Kbps
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Phân tích hiệu suất mạng Ad-hoc (RTS/CTS disabled)', fontsize=16, fontweight='bold')
    
    # Plot 1: Lost Client Ratio
    axes[0, 0].plot(nodes, lost_client_ratio, 'ro-', linewidth=2, markersize=8)
    axes[0, 0].set_xlabel('Số lượng nodes', fontsize=12)
    axes[0, 0].set_ylabel('Tỷ lệ clients mất kết nối (%)', fontsize=12)
    axes[0, 0].set_title('Tỷ lệ clients mất kết nối theo số nodes', fontsize=13, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].set_xlim(left=0)
    axes[0, 0].set_ylim(bottom=0)
    
    # Plot 2: Packet Loss Rate
    axes[0, 1].plot(nodes, packet_loss_rate, 'bs-', linewidth=2, markersize=8)
    axes[0, 1].set_xlabel('Số lượng nodes', fontsize=12)
    axes[0, 1].set_ylabel('Tỷ lệ mất gói (%)', fontsize=12)
    axes[0, 1].set_title('Tỷ lệ mất gói theo số nodes', fontsize=13, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].set_xlim(left=0)
    axes[0, 1].set_ylim(bottom=0)
    
    # Plot 3: Throughput
    axes[1, 0].plot(nodes, throughput, 'g^-', linewidth=2, markersize=8)
    axes[1, 0].set_xlabel('Số lượng nodes', fontsize=12)
    axes[1, 0].set_ylabel('Throughput trung bình (Kbps)', fontsize=12)
    axes[1, 0].set_title('Throughput trung bình theo số nodes', fontsize=13, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].set_xlim(left=0)
    axes[1, 0].set_ylim(bottom=0)
    
    # Plot 4: Total packets received
    total_rx = [r['total_rx_packets'] for r in results]
    axes[1, 1].plot(nodes, total_rx, 'mo-', linewidth=2, markersize=8)
    axes[1, 1].set_xlabel('Số lượng nodes', fontsize=12)
    axes[1, 1].set_ylabel('Tổng số packets nhận được', fontsize=12)
    axes[1, 1].set_title('Tổng packets nhận được theo số nodes', fontsize=13, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_xlim(left=0)
    axes[1, 1].set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig('network_analysis_results.png', dpi=300, bbox_inches='tight')
    print("\n✓ Đã lưu biểu đồ vào file: network_analysis_results.png")
    plt.show()

def export_to_csv(results, filename='analysis_results.csv'):
    """
    Export results to CSV file
    """
    if not results:
        print("Không có dữ liệu để xuất")
        return
    
    import csv
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Số Nodes', 
            'Số Clients', 
            'Clients mất kết nối', 
            'Tỷ lệ lost clients (%)',
            'Total TX Packets',
            'Total RX Packets',
            'Total Lost Packets',
            'Packet Loss Rate (%)',
            'Avg Throughput (Kbps)'
        ])
        
        for r in results:
            writer.writerow([
                r['num_nodes'],
                r['total_clients'],
                r['lost_clients'],
                f"{r['lost_client_ratio']:.2f}",
                r['total_tx_packets'],
                r['total_rx_packets'],
                r['total_lost_packets'],
                f"{r['packet_loss_rate']:.2f}",
                f"{r['avg_throughput_bps']/1000:.2f}"
            ])
    
    print(f"✓ Đã xuất kết quả ra file: {filename}")

if __name__ == "__main__":
    # Analyze all XML files
    results = analyze_all_files('final-*-nodes.xml')
    
    if results:
        # Plot the results
        plot_results(results)
        
        # Export to CSV
        export_to_csv(results)
        
        print("\n" + "=" * 80)
        print("HOÀN THÀNH PHÂN TÍCH!")
        print("=" * 80)
    else:
        print("\nVui lòng chạy simulation để tạo các file XML trước:")
        print("  ./ns3 run 'csma-ca --collectData=true'")