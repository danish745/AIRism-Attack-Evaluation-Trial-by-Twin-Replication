# ------------------------- Data Manipulation Attack Simulation -------------------------
import matplotlib
matplotlib.use('TkAgg')

import airsim
import networkx as nx
import random
import time
import matplotlib.pyplot as plt
import csv
import os
from dt_plugin import DigitalTwinPlugin

client = airsim.MultirotorClient()
client.confirmConnection()
dt_plugin = DigitalTwinPlugin()

folder_path = r"C:\\Users\\danis\\Documents\\AirSim"
csv_file_path = os.path.join(folder_path, "drone_simulation_log_data_manipulation.csv")

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

# === Initial Drone Setup ===
drone_positions = {
    f"Drone{i+1}": (10 + i*10, 10 + (i//3)*10, -5) for i in range(9)
}
clusters = {
    "Cluster1": ["Drone1", "Drone2", "Drone3"],
    "Cluster2": ["Drone4", "Drone5", "Drone6"],
    "Cluster3": ["Drone7", "Drone8", "Drone9"]
}
all_drones = [drone for cluster in clusters.values() for drone in cluster]
removed_drones = set()
attack_count = {drone: 0 for drone in all_drones}

# === Graph and Drone State Variables ===
def initialize_network():
    G = nx.Graph()
    for d in all_drones:
        G.add_node(d)

    for cluster, drones in clusters.items():
        for i in range(len(drones)):
            for j in range(i+1, len(drones)):
                if random.random() > 0.5:
                    G.add_edge(drones[i], drones[j], weight=random.randint(10, 20))

    for i in range(len(all_drones)):
        for j in range(i+1, len(all_drones)):
            if random.random() > 0.7:
                G.add_edge(all_drones[i], all_drones[j], weight=random.randint(10, 20))

    return G

def initialize_drone_states():
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
        'trust_score': {d: random.uniform(0.7, 1.0) for d in all_drones},
    }

# Initialize once at start
G = initialize_network()
drone_state = initialize_drone_states()

# -------- Attack Logic --------
def apply_data_manipulation_attack():
    attacks = {d: "Trustworthy" for d in G.nodes()}
    target = random.choice([d for d in G.nodes() if d not in removed_drones])
    attacks[target] = "Data Manipulation"
    attack_count[target] += 1
    return attacks, target

# -------- Main Loop --------
for iteration in range(15):
    print(f"\n[INFO] Iteration {iteration}")

    # === Reset every 5 iterations ===
    if iteration % 5 == 0 and iteration != 0:
        print("[INFO] Resetting clusters and drone states...")
        removed_drones.clear()
        G = initialize_network()
        drone_state = initialize_drone_states()
        print("[INFO] Reset complete.\n")

    attacks, attacked_drone = apply_data_manipulation_attack()

    deg = nx.degree_centrality(G)
    bet = nx.betweenness_centrality(G)
    close = nx.closeness_centrality(G)
    try:
        eig = nx.eigenvector_centrality(G)
    except:
        eig = {}

    with open(csv_file_path, "a", newline="") as file:
        writer = csv.writer(file)

        for drone in list(G.nodes()):
            if drone in removed_drones:
                continue

            neighbors = list(G.neighbors(drone)) if drone in G.nodes() else []
            attack_type = attacks.get(drone, "")

            predicted = {
                'speed': drone_state['speed'][drone],
                'sensor_ok': 1,
                'centrality': deg.get(drone, 0)
            }

            actual = {
                'speed': predicted['speed'] + (random.uniform(0.3, 0.6) if attack_type == "Data Manipulation" else 0),
                'sensor_ok': 0 if attack_type == "Data Manipulation" else 1,
                'centrality': max(0.0, predicted['centrality'] - (0.3 if attack_type == "Data Manipulation" else 0))
            }

            delta = {
                'speed': abs(predicted['speed'] - actual['speed']),
                'sensor': abs(predicted['sensor_ok'] - actual['sensor_ok']),
                'centrality': abs(predicted['centrality'] - actual['centrality'])
            }

            writer.writerow([
                iteration, drone, neighbors, attack_type if attack_type != "Trustworthy" else "",
                "MALICIOUS" if any(v > 0.1 for v in delta.values()) else "TRUSTED",
                deg.get(drone, 0), bet.get(drone, 0), close.get(drone, 0), eig.get(drone, 0),
                drone_state['battery'][drone], drone_state['sensor'][drone], drone_state['speed'][drone],
                drone_state['location'][drone], drone_state['intensity'][drone], drone_state['scale'][drone],
                drone_state['latency'][drone], drone_state['throughput'][drone],
                drone_state['packet'][drone], drone_state['coord_rate'][drone], drone_state['trust_score'][drone],
                "Mismatched" if delta['speed'] > 0.1 else "Matched",
                "Mismatched" if delta['sensor'] > 0.1 else "Matched",
                "Mismatched" if delta['centrality'] > 0.1 else "Matched",
                attack_count[drone]
            ])

    # === Visualization ===
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=iteration)
    node_colors = ["yellow" if attacks.get(n) == "Data Manipulation" else "green" for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=900, edgecolors='black')
    nx.draw_networkx_edges(G, pos, width=2)
    nx.draw_networkx_labels(G, pos, font_size=10)

    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)

    legend_handles = [
        plt.Line2D([0], [0], marker='o', color='w', label='Trustworthy', markerfacecolor='green', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Data Manipulation', markerfacecolor='yellow', markersize=10)
    ]
    plt.legend(handles=legend_handles, loc="upper left")
    plt.title(f"Iteration {iteration} - Data Manipulation Attack")
    plt.axis('off')
    plt.show()

    # === Remove the attacked drone ===
    print(f"[INFO] Removing manipulated drone: {attacked_drone}")
    removed_drones.add(attacked_drone)
    if attacked_drone in G:
        G.remove_node(attacked_drone)
