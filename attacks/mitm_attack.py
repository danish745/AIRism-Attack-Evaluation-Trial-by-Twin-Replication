import matplotlib
matplotlib.use('TkAgg')

import airsim
import networkx as nx
import random
import matplotlib.pyplot as plt
import csv
import os
from dt_plugin import DigitalTwinPlugin

# === Init AirSim Client ===
client = airsim.MultirotorClient()
client.confirmConnection()
dt_plugin = DigitalTwinPlugin()

# === File Paths ===
folder_path = r"C:\Users\danis\Documents\AirSim"
csv_file_path = os.path.join(folder_path, "drone_simulation_log_mitm.csv")

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# === CSV Header ===
with open(csv_file_path, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "Iteration", "Drone", "Connected To", "Attack Type", "Trust Status",
        "Degree Centrality", "Betweenness Centrality", "Closeness Centrality", "Eigenvector Centrality",
        "Battery Level", "Sensor Functionality", "Relative Speed", "Location Accuracy",
        "Communication Intensity", "Communication Scale", "Latency", "Data Throughput",
        "Packet Loss", "Swarm Coordination Rate", "Trust Score",
        "Speed Match", "Sensor Match", "Centrality Match", "Total Times Attacked"
    ])

# === Drone Setup ===
drone_positions = {
    "Drone1": (10, 10, -5), "Drone2": (20, 10, -5), "Drone3": (15, 20, -5),
    "Drone4": (50, 50, -5), "Drone5": (60, 50, -5), "Drone6": (55, 60, -5),
    "Drone7": (90, 10, -5), "Drone8": (100, 10, -5), "Drone9": (95, 20, -5)
}
clusters = {
    "Cluster1": ["Drone1", "Drone2", "Drone3"],
    "Cluster2": ["Drone4", "Drone5", "Drone6"],
    "Cluster3": ["Drone7", "Drone8", "Drone9"]
}
all_drones = [drone for cluster in clusters.values() for drone in cluster]
removed_drones = set()
attack_count = {drone: 0 for drone in all_drones}

# === Drone Attribute Reset Function ===
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

# === Main Simulation Loop ===
for iteration in range(15):
    print(f"\n[INFO] Iteration {iteration}")

    # Reset every 5 iterations
    if iteration % 5 == 0 and iteration != 0:
        print("[INFO] Resetting graph and attributes...")
        removed_drones = set()
        attributes = reset_attributes()

    # === Initialize Network ===
    G = nx.Graph()
    for d in all_drones:
        if d not in removed_drones:
            G.add_node(d)

    for cluster, drones in clusters.items():
        valid = [d for d in drones if d not in removed_drones]
        for i in range(len(valid)):
            for j in range(i + 1, len(valid)):
                if random.random() > 0.5:
                    G.add_edge(valid[i], valid[j], weight=random.randint(10, 20))

    for i in range(len(all_drones)):
        for j in range(i + 1, len(all_drones)):
            if all_drones[i] in G.nodes and all_drones[j] in G.nodes:
                if random.random() > 0.7:
                    G.add_edge(all_drones[i], all_drones[j], weight=random.randint(10, 20))

    # === MITM Attack Logic ===
    def apply_mitm_attack():
        attacks = {d: "Trustworthy" for d in G.nodes()}
        target = random.choice([d for d in G.nodes() if d not in removed_drones])
        G.add_node("FakeNode")
        G.add_edge(target, "FakeNode")
        attacks[target] = "MITM Attack"
        attacks["FakeNode"] = "MITM Node"
        attack_count[target] += 1
        return attacks, target

    attacks, mitm_target = apply_mitm_attack()

    # === Centrality Calculations ===
    deg = nx.degree_centrality(G)
    bet = nx.betweenness_centrality(G)
    close = nx.closeness_centrality(G)
    try:
        eig = nx.eigenvector_centrality(G, max_iter=1000)
    except:
        eig = {}

    # === Log to CSV ===
    with open(csv_file_path, "a", newline="") as file:
        writer = csv.writer(file)
        for drone in list(G.nodes()):
            if drone.startswith("FakeNode") or drone in removed_drones:
                continue

            neighbors = list(G.neighbors(drone)) if drone in G.nodes() else []
            attack_type = attacks.get(drone, "")
            is_attacked = attack_type == "MITM Attack"

            predicted = {
                'speed': attributes['speed'][drone],
                'sensor_ok': 1,
                'centrality': deg.get(drone, 0)
            }

            actual = {
                'speed': predicted['speed'] + (random.uniform(0.3, 0.6) if is_attacked else 0),
                'sensor_ok': 0 if is_attacked else 1,
                'centrality': max(0.0, predicted['centrality'] - (0.3 if is_attacked else 0))
            }

            delta = dt_plugin.verify_drone(predicted, actual)

            writer.writerow([
                iteration, drone, neighbors, attack_type if attack_type != "Trustworthy" else "",
                "MALICIOUS" if any(v > 0.1 for v in delta.values()) else "TRUSTED",
                deg.get(drone, 0), bet.get(drone, 0), close.get(drone, 0), eig.get(drone, 0),
                attributes['battery'][drone], attributes['sensor'][drone], attributes['speed'][drone],
                attributes['location'][drone], attributes['intensity'][drone], attributes['scale'][drone],
                attributes['latency'][drone], attributes['throughput'][drone],
                attributes['packet'][drone], attributes['coord_rate'][drone], attributes['trust_score'][drone],
                "Matched" if delta['speed'] <= 0.1 else "Mismatched",
                "Matched" if delta['sensor'] <= 0.1 else "Mismatched",
                "Matched" if delta['centrality'] <= 0.1 else "Mismatched",
                attack_count[drone]
            ])

    # === Graph Visualization ===
    fig = plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=iteration)
    node_colors = [
        "purple" if attacks.get(n) == "MITM Attack" else
        "gray" if n == "FakeNode" else
        "green" for n in G.nodes()
    ]

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=900, edgecolors='black', linewidths=1.5)
    nx.draw_networkx_edges(G, pos, width=2, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=11, font_weight='bold')
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)

    legend_handles = [
        plt.Line2D([0], [0], marker='o', color='w', label='Trustworthy', markerfacecolor='green', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='MITM Attack', markerfacecolor='purple', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Fake Node', markerfacecolor='gray', markersize=10)
    ]
    plt.legend(handles=legend_handles, loc="upper left")
    plt.title(f"Iteration {iteration} - MITM Attack", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

    # === Remove Affected Drones ===
    print(f"[INFO] Isolating attacked drone: {mitm_target}")
    removed_drones.add(mitm_target)
    if mitm_target in G:
        G.remove_node(mitm_target)
    if "FakeNode" in G:
        G.remove_node("FakeNode")

print(f"\n✅ MITM Attack simulation complete. CSV saved to:\n{csv_file_path}")
