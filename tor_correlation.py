#!/usr/bin/env python3
"""
TOR Time Correlation with Graphs - IMPROVED VISUALIZATION
"""

import requests
import json
import matplotlib.pyplot as plt
import networkx as nx

# ============== PART 1: FETCH TOR DATA ==============

def fetch_tor_data():
    """Download real TOR relay data from the internet"""
    print("[*] Fetching TOR network data from Onionoo API...")
    url = "https://onionoo.torproject.org/summary"
    response = requests.get(url)
    return response.json()

# ============== PART 2: EXTRACT NODES ==============

def extract_nodes(tor_data):
    """Separate entry and exit nodes"""
    entry_nodes = []
    exit_nodes = []
    
    for relay in tor_data['relays']:
        flags = relay.get('flags', [])
        nickname = relay.get('nickname', relay.get('fingerprint', 'unknown')[:16])
        
        node_info = {
            'nickname': nickname,
            'addresses': relay.get('addresses', [])
        }
        
        if 'Exit' in flags:
            exit_nodes.append(node_info)
        else:
            entry_nodes.append(node_info)
    
    return entry_nodes, exit_nodes

# ============== PART 3: TRAFFIC DATA ==============

class TrafficFlow:
    def __init__(self, node_id, node_name, timestamp, bytes_transferred):
        self.node_id = node_id
        self.node_name = node_name
        self.timestamp = timestamp
        self.bytes = bytes_transferred

def create_sample_traffic():
    """Create example traffic data"""
    entry_traffic = [
        TrafficFlow('e1', 'relay_guard_1', 100.0, 1000),
        TrafficFlow('e1', 'relay_guard_1', 101.0, 500),
        TrafficFlow('e1', 'relay_guard_1', 102.0, 1500),
        TrafficFlow('e1', 'relay_guard_1', 103.0, 2000),
    ]
    
    exit_traffic = [
        TrafficFlow('x1', 'relay_exit_7', 103.2, 1000),
        TrafficFlow('x1', 'relay_exit_7', 104.2, 500),
        TrafficFlow('x1', 'relay_exit_7', 105.2, 1500),
        TrafficFlow('x1', 'relay_exit_7', 106.2, 2000),
    ]
    
    return entry_traffic, exit_traffic

# ============== PART 4: CORRELATION ==============

def find_correlations(entry_flows, exit_flows, time_window=5):
    """Find matching traffic patterns"""
    matches = []
    
    for entry in entry_flows:
        for exit in exit_flows:
            byte_diff = abs(entry.bytes - exit.bytes)
            
            if byte_diff < 100:
                delay = exit.timestamp - entry.timestamp
                
                if 0 < delay < time_window:
                    byte_score = (1 - (byte_diff / max(entry.bytes, exit.bytes))) * 50
                    timing_score = (1 - (delay / time_window)) * 50
                    confidence = byte_score + timing_score
                    
                    matches.append({
                        'entry_node': entry.node_name,
                        'exit_node': exit.node_name,
                        'confidence': confidence,
                        'delay': delay,
                        'bytes': entry.bytes
                    })
    
    return matches

# ============== PART 5: BEAUTIFUL VISUALIZATION ==============

def plot_simple_correlation(match):
    """Draw a beautiful entry → exit graph"""
    G = nx.DiGraph()
    G.add_node(match['entry_node'], type='entry')
    G.add_node(match['exit_node'], type='exit')
    G.add_edge(match['entry_node'], match['exit_node'])
    
    fig, ax = plt.subplots(figsize=(14, 8), facecolor='#f0f0f0')
    
    # Position nodes
    pos = {
        match['entry_node']: (0, 0),
        match['exit_node']: (3, 0)
    }
    
    # Draw edges FIRST (so they appear behind nodes)
    nx.draw_networkx_edges(
        G, pos,
        arrowstyle='-|>',
        arrowsize=40,
        width=4,
        edge_color='#2E86AB',
        connectionstyle='arc3,rad=0.1',
        ax=ax
    )
    
    # Draw nodes with custom colors
    entry_color = '#E63946'  # Beautiful red
    exit_color = '#06A77D'   # Beautiful green
    
    node_colors = [entry_color, exit_color]
    
    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=5000,
        ax=ax,
        edgecolors='#1D3557',
        linewidths=3
    )
    
    # Draw labels with better formatting
    labels = {
        match['entry_node']: f"{match['entry_node']}\n(ENTRY)",
        match['exit_node']: f"{match['exit_node']}\n(EXIT)"
    }
    
    nx.draw_networkx_labels(
        G, pos,
        labels=labels,
        font_size=11,
        font_weight='bold',
        font_color='white',
        ax=ax
    )
    
    # Add information box
    info_text = f"""
    Confidence: {match['confidence']:.1f}%
    Delay: {match['delay']:.2f} seconds
    Data Volume: {match['bytes']} bytes
    """
    
    ax.text(
        1.5, -1.2,
        info_text,
        fontsize=12,
        bbox=dict(boxstyle='round,pad=0.8', facecolor='#1D3557', edgecolor='#E63946', linewidth=2, alpha=0.9),
        color='white',
        ha='center',
        weight='bold'
    )
    
    # Title
    ax.set_title(
        'TOR Traffic Correlation Detected',
        fontsize=16,
        fontweight='bold',
        pad=20,
        color='#1D3557'
    )
    
    ax.set_xlim(-1, 4)
    ax.set_ylim(-2, 1)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('correlation_graph.png', dpi=300, facecolor='#f0f0f0')
    print("[+] Beautiful graph saved as 'correlation_graph.png'")
    plt.show()

def plot_timeline(entry_traffic, exit_traffic):
    """Draw beautiful timeline of traffic"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), facecolor='#f0f0f0')
    
    entry_times = [f.timestamp for f in entry_traffic]
    entry_bytes = [f.bytes for f in entry_traffic]
    exit_times = [f.timestamp for f in exit_traffic]
    exit_bytes = [f.bytes for f in exit_traffic]
    
    # Entry traffic plot
    ax1.plot(entry_times, entry_bytes, marker='o', color='#E63946', linewidth=3, 
            markersize=10, label='Entry Node Traffic', markeredgecolor='#1D3557', markeredgewidth=2)
    ax1.fill_between(entry_times, entry_bytes, alpha=0.3, color='#E63946')
    ax1.set_title('Traffic Entering TOR (Entry Node)', fontsize=13, fontweight='bold', color='#1D3557')
    ax1.set_ylabel('Bytes Transferred', fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--', color='#999')
    ax1.set_facecolor('#ffffff')
    ax1.legend(fontsize=10, loc='upper left')
    
    # Exit traffic plot
    ax2.plot(exit_times, exit_bytes, marker='s', color='#06A77D', linewidth=3,
            markersize=10, label='Exit Node Traffic', markeredgecolor='#1D3557', markeredgewidth=2)
    ax2.fill_between(exit_times, exit_bytes, alpha=0.3, color='#06A77D')
    ax2.set_title('Traffic Exiting TOR (Exit Node)', fontsize=13, fontweight='bold', color='#1D3557')
    ax2.set_xlabel('Time (seconds)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Bytes Transferred', fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--', color='#999')
    ax2.set_facecolor('#ffffff')
    ax2.legend(fontsize=10, loc='upper left')
    
    plt.tight_layout()
    plt.savefig('timeline_graph.png', dpi=300, facecolor='#f0f0f0')
    print("[+] Beautiful timeline saved as 'timeline_graph.png'")
    plt.show()

# ============== MAIN ==============

def main():
    print("\n" + "="*70)
    print("TOR TIME CORRELATION WITH GRAPHS (IMPROVED VISUALIZATION)")
    print("="*70 + "\n")
    
    # Step 1: Fetch real TOR data
    tor_data = fetch_tor_data()
    entry_nodes, exit_nodes = extract_nodes(tor_data)
    print(f"[✓] Fetched TOR data")
    print(f"    Entry nodes: {len(entry_nodes)}")
    print(f"    Exit nodes: {len(exit_nodes)}\n")
    
    # Step 2: Create sample traffic
    entry_traffic, exit_traffic = create_sample_traffic()
    print(f"[✓] Created sample traffic data\n")
    
    # Step 3: Find correlations
    correlations = find_correlations(entry_traffic, exit_traffic)
    print(f"[✓] Found {len(correlations)} correlation(s)\n")
    
    for i, match in enumerate(correlations, 1):
        print(f"Match #{i}:")
        print(f"  Entry: {match['entry_node']}")
        print(f"  Exit: {match['exit_node']}")
        print(f"  Confidence: {match['confidence']:.1f}%")
        print(f"  Delay: {match['delay']:.2f} seconds\n")
    
    # Step 4: Visualize
    if correlations:
        print("[*] Generating beautiful visualizations...")
        plot_simple_correlation(correlations[0])
        plot_timeline(entry_traffic, exit_traffic)
        print("[✓] Done!\n")

if __name__ == "__main__":
    main()
