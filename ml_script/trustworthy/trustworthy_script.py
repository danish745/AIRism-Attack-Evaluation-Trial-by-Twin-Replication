import matplotlib
matplotlib.use('TkAgg')  # Use Tkinter-based backend for displaying graphs

import airsim
import networkx as nx
import random
import time
import matplotlib.pyplot as plt
import pandas as pd
import csv
import os
from dt_plugin import DigitalTwinPlugin

# Initialize AirSim Client
client = airsim.MultirotorClient()
client.confirmConnection()

dt_plugin = DigitalTwinPlugin()

# **CSV File Path**
folder_path = r"C:\Users\danis\Documents\AirSim"
csv_file_path = os.path.join(folder_path, "drone_simulation_log.csv")

# Ensure the folder exists
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Initialize CSV file with new metrics
with open(csv_file_path, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "Iteration", "Drone", "Connected To", "Degree Centrality", "Betweenness Centrality", "Closeness Centrality", "Eigenvector Centrality", 
        "Battery Level", "Sensor Functionality", "Relative Speed", "Location Accuracy", "Communication Intensity", "Communication Scale", 
        "Scale-Intensity Centrality", "Latency", "Data Throughput", "Packet Loss", "Swarm Coordination Rate",
        "Speed Match", "Centrality Match", "Sensor Match", "Trust Status"
    ])

# **Drone positions**
drone_positions = {
    "Drone1": (10, 10, -5), "Drone2": (20, 10, -5), "Drone3": (15, 20, -5),
    "Drone4": (50, 50, -5), "Drone5": (60, 50, -5), "Drone6": (55, 60, -5),
    "Drone7": (90, 10, -5), "Drone8": (100, 10, -5), "Drone9": (95, 20, -5)
}

# Define clusters
clusters = {
    "Cluster1": ["Drone1", "Drone2", "Drone3"],
    "Cluster2": ["Drone4", "Drone5", "Drone6"],
    "Cluster3": ["Drone7", "Drone8", "Drone9"]
}

# Enable API control and arm drones
all_drones = [drone for cluster in clusters.values() for drone in cluster]
for drone in all_drones:
    client.enableApiControl(True, drone)
    client.armDisarm(True, drone)
    client.moveToPositionAsync(
        x=drone_positions[drone][0] + random.uniform(-5, 5),
        y=drone_positions[drone][1] + random.uniform(-5, 5),
        z=drone_positions[drone][2],
        velocity=2,
        vehicle_name=drone
    )

# Create a communication network graph
G = nx.Graph()
comm_frequency = {}

# Assign battery levels, sensor functionality, and communication range
battery_levels = {drone: random.randint(50, 100) for drone in all_drones}
sensor_functionality = {drone: random.uniform(0.8, 1.0) for drone in all_drones}
relative_speeds = {drone: random.uniform(0.8, 1.2) for drone in all_drones}
location_accuracy = {drone: random.uniform(0.9, 1.0) for drone in all_drones}
communication_intensity = {drone: random.randint(5, 20) for drone in all_drones}
communication_scale = {drone: random.randint(1, 3) for drone in all_drones}
latency = {drone: random.uniform(0.01, 0.1) for drone in all_drones}
data_throughput = {drone: random.randint(100, 500) for drone in all_drones}
packet_loss = {drone: random.uniform(0.0, 0.05) for drone in all_drones}
swarm_coordination_rate = {drone: random.uniform(0.8, 1.0) for drone in all_drones}

# Add nodes and set communication frequency
for drone in all_drones:
    G.add_node(drone)
    comm_frequency[drone] = random.randint(5, 15)

# Establish intra-cluster communication links with randomness
for cluster, drones in clusters.items():
    for i in range(len(drones)):
        for j in range(i + 1, len(drones)):
            if random.random() > 0.5:
                weight = random.randint(10, 20)
                G.add_edge(drones[i], drones[j], weight=weight)

# Ensure some inter-cluster links
for i in range(len(all_drones)):
    for j in range(i + 1, len(all_drones)):
        if random.random() > 0.7:
            weight = random.randint(10, 20)
            G.add_edge(all_drones[i], all_drones[j], weight=weight)

# **Compute centrality metrics**
def compute_centrality():
    if len(G.nodes) == 0:
        return {}, {}, {}, {}
    return nx.degree_centrality(G), nx.betweenness_centrality(G), nx.closeness_centrality(G), nx.eigenvector_centrality(G, max_iter=1000)

# **Log Data to CSV (ensures data is written)**
def log_data_to_csv(iteration, degree_centrality, betweenness_centrality, closeness_centrality, eigenvector_centrality):
    def label(delta_val):
        return "Matched" if delta_val < 0.1 else "Mismatched"

    with open(csv_file_path, "a", newline="") as file:
        writer = csv.writer(file)
        for drone in all_drones:
            connected_drones = list(G.neighbors(drone)) if drone in G.nodes else "Disconnected"

            actual_data = dt_plugin.get_actual_metrics(drone)
            actual_data['centrality'] = degree_centrality.get(drone, 0)

            predicted_data = {
                'speed': actual_data['speed'],
                'centrality': degree_centrality.get(drone, 0),
                'sensor_ok': actual_data['sensor_ok']
            }

            delta = dt_plugin.verify_drone(predicted_data, actual_data)
            is_trustworthy = all(v < 0.1 for v in delta.values())

            writer.writerow([
                iteration, drone, connected_drones,
                degree_centrality.get(drone, 0), betweenness_centrality.get(drone, 0), closeness_centrality.get(drone, 0), eigenvector_centrality.get(drone, 0),
                battery_levels[drone], sensor_functionality[drone], actual_data['speed'], location_accuracy[drone],
                communication_intensity[drone], communication_scale[drone], communication_intensity[drone] * communication_scale[drone],
                latency[drone], data_throughput[drone], packet_loss[drone], swarm_coordination_rate[drone],
                label(delta['speed']), label(delta['centrality']), label(delta['sensor']),
                "TRUSTED" if is_trustworthy else "MALICIOUS"
            ])
    print(f"[INFO] CSV Data Logged for Iteration {iteration}")

# **Plot network graph dynamically with improved readability**
def plot_network(iteration):
    if len(G.nodes) == 0:
        print("[ERROR] All drones were removed! No network to display.")
        return

    plt.figure(figsize=(10, 8))
    pos = nx.fruchterman_reingold_layout(G)
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=700, edgecolors='black')
    edges = G.edges(data=True)
    edge_widths = [max(0.2, data['weight'] / 15) for _, _, data in edges]
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='black')
    edge_labels = {(u, v): d["weight"] for u, v, d in edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    plt.title(f"Drone Communication Network - Iteration {iteration}", fontsize=14)
    plt.show(block=True)

# **Run simulation loop**
for iteration in range(5):
    print(f"\n[INFO] Iteration {iteration+1}")
    degree_centrality, betweenness_centrality, closeness_centrality, eigenvector_centrality = compute_centrality()
    log_data_to_csv(iteration, degree_centrality, betweenness_centrality, closeness_centrality, eigenvector_centrality)
    plot_network(iteration)
    time.sleep(0.5)

print(f"\n[INFO] Simulation completed. Data saved at: {csv_file_path}")
