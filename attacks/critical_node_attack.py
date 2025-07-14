# Critical Node Attack Simulation - ML-Compatible Version with Graphs
import matplotlib
matplotlib.use('TkAgg')

import airsim
import networkx as nx
import random
import matplotlib.pyplot as plt
import csv
import os
from dt_plugin import DigitalTwinPlugin

client = airsim.MultirotorClient()
client.confirmConnection()
dt_plugin = DigitalTwinPlugin()

folder_path = r"C:\Users\danis\Documents\AirSim"
csv_file_path = os.path.join(folder_path, "drone_simulation_log_critical_node.csv")

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

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

# === Drone & Cluster Setup ===
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
for drone in all_drones:
    client.enableApiControl(True, drone)
    client.armDisarm(True, drone)

# === Drone State Reset Function ===
def reset_drone_states():
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

# === Init Simulation State ===
active_drones = all_drones.copy()
attacked_history = {}
attack_count_per_drone = {drone: 0 for drone in all_drones}
drone_state = reset_drone_states()

# === Main Loop ===
for iteration in range(15):
    print(f"\n[INFO] Iteration {iteration}")

    if iteration % 5 == 0 and iteration != 0:
        print("[INFO] Resetting network and drone states...")
        active_drones = all_drones.copy()
        drone_state = reset_drone_states()
        attacked_history.clear()

    G = nx.Graph()
    for d in active_drones:
        G.add_node(d)

    for cluster, drones in clusters.items():
        filtered = [d for d in drones if d in active_drones]
        for i in range(len(filtered)):
            for j in range(i + 1, len(filtered)):
                if random.random() > 0.5:
                    G.add_edge(filtered[i], filtered[j], weight=random.randint(10, 20))

    for i in range(len(active_drones)):
        for j in range(i + 1, len(active_drones)):
            if random.random() > 0.7:
                G.add_edge(active_drones[i], active_drones[j], weight=random.randint(10, 20))

    attacks = {drone: "Trustworthy" for drone in active_drones}
    centrality = nx.betweenness_centrality(G)
    critical = sorted(centrality, key=centrality.get, reverse=True)[:2]
    for d in critical:
        attacks[d] = "Critical Node Attack"

    attacked_this_round = [d for d in active_drones if attacks[d] == "Critical Node Attack"]
    attacked_history[iteration] = attacked_this_round
    for d in attacked_this_round:
        attack_count_per_drone[d] += 1
        active_drones.remove(d)

    deg = nx.degree_centrality(G)
    bet = nx.betweenness_centrality(G)
    close = nx.closeness_centrality(G)
    try:
        eig = nx.eigenvector_centrality(G, max_iter=1000)
    except:
        eig = {}

    with open(csv_file_path, "a", newline="") as file:
        writer = csv.writer(file)
        for drone in G.nodes:
            neighbors = list(G.neighbors(drone)) if drone in G.nodes() else "Removed"
            attack_type = attacks.get(drone, "None")

            predicted = {
                'speed': drone_state['speed'][drone],
                'sensor_ok': 1,
                'centrality': deg.get(drone, 0)
            }

            actual = predicted.copy()
            if attack_type != "Trustworthy":
                actual['speed'] += random.uniform(0.3, 0.6)
                actual['sensor_ok'] = 0
                actual['centrality'] = max(0.0, actual['centrality'] - 0.3)

            delta = dt_plugin.verify_drone(predicted, actual)

            writer.writerow([
                iteration, drone, neighbors, attack_type,
                "TRUSTED" if all(v <= 0.1 for v in delta.values()) else "MALICIOUS",
                deg.get(drone, 0), bet.get(drone, 0), close.get(drone, 0), eig.get(drone, 0),
                drone_state['battery'][drone], drone_state['sensor'][drone], drone_state['speed'][drone],
                drone_state['location'][drone], drone_state['intensity'][drone], drone_state['scale'][drone],
                drone_state['latency'][drone], drone_state['throughput'][drone],
                drone_state['packet'][drone], drone_state['coord_rate'][drone],
                drone_state['trust_score'][drone],
                "Matched" if delta['speed'] <= 0.1 else "Mismatched",
                "Matched" if delta['sensor'] <= 0.1 else "Mismatched",
                "Matched" if delta['centrality'] <= 0.1 else "Mismatched",
                attack_count_per_drone[drone]
            ])

    # === Visualization ===
    fig = plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=iteration, k=1.5)
    color_map = {"Trustworthy": "green", "Critical Node Attack": "red"}
    node_colors = [color_map.get(attacks.get(d, "Trustworthy"), "gray") for d in G.nodes()]

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=900, edgecolors='black', linewidths=1.5)
    nx.draw_networkx_edges(G, pos, width=2, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=11, font_weight='bold')
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, font_color='black')

    legend_handles = [
        plt.Line2D([0], [0], marker='o', color='w', label='Trustworthy', markerfacecolor='green', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Critical Node Attack', markerfacecolor='red', markersize=10)
    ]
    plt.legend(handles=legend_handles, loc="upper left")
    plt.title(f"Iteration {iteration} - Critical Node Attack", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    manager = plt.get_current_fig_manager()
    try:
        manager.canvas.manager.window.attributes('-topmost', 1)
    except Exception:
        pass
    plt.show()
    plt.close(fig)

print(f"\n✅ [Done] Critical Node Attack simulation complete. CSV saved to:\n{csv_file_path}")
