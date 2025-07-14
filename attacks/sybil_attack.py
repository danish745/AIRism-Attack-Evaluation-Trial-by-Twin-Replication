import matplotlib
matplotlib.use('TkAgg')

import airsim
import networkx as nx
import random
import matplotlib.pyplot as plt
import csv
import os
from dt_plugin import DigitalTwinPlugin

# === Setup ===
client = airsim.MultirotorClient()
client.confirmConnection()
dt_plugin = DigitalTwinPlugin()

folder_path = r"C:\Users\danis\Documents\AirSim"
csv_file_path = os.path.join(folder_path, "drone_sybil_attack.csv")

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# === CSV Headers ===
with open(csv_file_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Iteration", "Drone", "Connected To", "Attack Type", "Trust Status",
        "Degree Centrality", "Betweenness Centrality", "Closeness Centrality", "Eigenvector Centrality",
        "Battery Level", "Sensor Functionality", "Relative Speed", "Location Accuracy",
        "Communication Intensity", "Communication Scale", "Latency", "Data Throughput",
        "Packet Loss", "Swarm Coordination Rate", "Trust Score",
        "Speed Match", "Sensor Match", "Centrality Match", "Total Times Attacked"
    ])

# === Drone Setup ===
drone_positions = {f"Drone{i+1}": (10 + i*10, 10 + (i//3)*10, -5) for i in range(9)}
all_drones = list(drone_positions.keys())
removed_drones = set()
attack_count = {d: 0 for d in all_drones}
sybil_counter = 0

# === Attribute Reset ===
def reset_attributes():
    return {
        'battery': {d: random.randint(50, 100) for d in all_drones},
        'sensor': {d: random.uniform(0.8, 1.0) for d in all_drones},
        'speed': {d: random.uniform(0.8, 1.2) for d in all_drones},
        'location': {d: random.uniform(0.9, 1.0) for d in all_drones},
        'intensity': {d: random.randint(5, 20) for d in all_drones},
        'scale': {d: random.randint(1, 3) for d in all_drones},
        'latency': {d: random.uniform(0.01, 0.1) for d in all_drones},
        'throughput': {d: random.randint(100, 500) for d in all_drones},
        'packet': {d: random.uniform(0.0, 0.05) for d in all_drones},
        'coord_rate': {d: random.uniform(0.8, 1.0) for d in all_drones},
        'trust_score': {d: random.uniform(0.7, 1.0) for d in all_drones}
    }

attributes = reset_attributes()

# === Simulation Loop ===
for iteration in range(15):
    print(f"\n[INFO] Iteration {iteration}")

    if iteration % 5 == 0 and iteration != 0:
        print("[INFO] Resetting network and attributes...")
        removed_drones.clear()
        sybil_counter = 0
        attributes = reset_attributes()

    G = nx.Graph()
    current_drones = [d for d in all_drones if d not in removed_drones]
    for d in current_drones:
        G.add_node(d)

    for i in range(len(current_drones)):
        for j in range(i+1, len(current_drones)):
            if random.random() > 0.5:
                G.add_edge(current_drones[i], current_drones[j], weight=random.randint(10, 20))

    # === Sybil Attack Logic ===
    attacks = {d: "" for d in G.nodes()}
    targets = random.sample(current_drones, random.randint(1, 2))

    for target in targets:
        sybil_name = f"Sybil_{sybil_counter}"
        sybil_counter += 1
        G.add_node(sybil_name)
        G.add_edge(sybil_name, target, weight=random.randint(5, 15))
        attacks[target] = "Sybil Impersonated"
        attacks[sybil_name] = "Sybil Node"
        attack_count[target] += 1

    # === Centralities ===
    deg = nx.degree_centrality(G)
    bet = nx.betweenness_centrality(G)
    close = nx.closeness_centrality(G)
    try:
        eig = nx.eigenvector_centrality(G, max_iter=1000)
    except:
        eig = {}

    # === Write to CSV ===
    with open(csv_file_path, "a", newline="") as file:
        writer = csv.writer(file)
        for node in G.nodes():
            if node.startswith("Sybil_"):
                continue

            neighbors = list(G.neighbors(node))
            attack_type = attacks.get(node, "")

            predicted = {
                'speed': attributes['speed'][node],
                'sensor_ok': 1,
                'centrality': deg.get(node, 0)
            }

            actual = predicted.copy()
            if node in targets:
                actual['speed'] += random.uniform(0.3, 0.6)
                actual['sensor_ok'] = 0
                actual['centrality'] = max(0, predicted['centrality'] - 0.3)

            delta = {
                'speed': abs(predicted['speed'] - actual['speed']),
                'sensor': abs(predicted['sensor_ok'] - actual['sensor_ok']),
                'centrality': abs(predicted['centrality'] - actual['centrality'])
            }

            trust = "MALICIOUS" if any(v > 0.1 for v in delta.values()) else "TRUSTED"

            writer.writerow([
                iteration, node, neighbors, attack_type,
                trust,
                deg.get(node, 0), bet.get(node, 0), close.get(node, 0), eig.get(node, 0),
                attributes['battery'][node], attributes['sensor'][node], attributes['speed'][node], attributes['location'][node],
                attributes['intensity'][node], attributes['scale'][node], attributes['latency'][node], attributes['throughput'][node],
                attributes['packet'][node], attributes['coord_rate'][node], attributes['trust_score'][node],
                "Matched" if delta['speed'] <= 0.1 else "Mismatched",
                "Matched" if delta['sensor'] <= 0.1 else "Mismatched",
                "Matched" if delta['centrality'] <= 0.1 else "Mismatched",
                attack_count[node]
            ])

    # === Visualization ===
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=iteration)
    node_colors = []
    for n in G.nodes():
        if n.startswith("Sybil_"):
            node_colors.append("purple")
        elif n in targets:
            node_colors.append("orange")
        else:
            node_colors.append("green")

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=900, edgecolors='black')
    nx.draw_networkx_edges(G, pos, width=2)
    nx.draw_networkx_labels(G, pos, font_size=10)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)

    legend = [
        plt.Line2D([0], [0], marker='o', color='w', label='Trustworthy', markerfacecolor='green', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Sybil Impersonated', markerfacecolor='orange', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Sybil Node', markerfacecolor='purple', markersize=10)
    ]
    plt.legend(handles=legend, loc="upper left")
    plt.title(f"Iteration {iteration} - Sybil Attack")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

    for target in targets:
        removed_drones.add(target)
        print(f"[⚠️] Drone removed due to Sybil attack: {target}")

print(f"\n✅ Sybil Attack simulation complete. CSV saved to:\n{csv_file_path}")
