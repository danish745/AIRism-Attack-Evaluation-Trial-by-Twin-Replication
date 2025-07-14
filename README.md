# AiRism-Attack-Evaluation (Trial-by-Twin-Replication)

This repository contains the complete codebase, data, models, and evaluation for reproducing the experiments described in the paper *Trial by Twin: Behavior-Predictive Trust in Autonomous Drone Swarms*.

## 🧠 Project Structure

```
AiRism-Attack-Evaluation/
├── attacks/                # Python scripts for attack scenarios (e.g., sybil_attack.py)
├── data/                   # AirSim-generated drone log CSVs for each attack
├── ml_notebook/            # Jupyter notebooks for ML modeling and evaluation
│   └── evaluation_table.ipynb
├── ml_script/              # ML pipeline scripts (training, trust scoring, prediction)
├── result/                 # Output images and plots (e.g., sybil_attack_prediction.png)
├── LICENSE                 # License file (MIT)
├── README.md               # Project overview and documentation
└── requirements.txt        # Python dependencies


## 🛠️ Setup Instructions

1. Clone the repository:
```bash
git clone <repo-url>
cd AiRism-Attack-Evaluation
```

2. Create a Python environment and install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure Unreal Engine & AirSim Plugin are installed.

## 🚀 Run the Simulation

1. Open **Blocks environment** in Unreal Engine:
```bash
<pre> <code> C:\user\Directory\Unreal\Environments\Blocks </code> </pre>

2. Start simulation:
```bash
<pre> <code> cd C:\Users\YourUsername\AirSim\PythonClient\multirotor </code> </pre>
python multi_drone.py
```

## ⚙️ AirSim settings.json

Create the following file at:
```
<pre> <code> directory/AirSim/settings.json </code> </pre>
```

```json
{
  "SettingsVersion": 1.2,
  "SimMode": "Multirotor",
  "Vehicles": {
    "Drone1": {"VehicleType": "SimpleFlight", "X": 0, "Y": 0, "Z": 0},
    "Drone2": {"VehicleType": "SimpleFlight", "X": 10, "Y": 0, "Z": 0},
    "Drone3": {"VehicleType": "SimpleFlight", "X": 0, "Y": 10, "Z": 0}
  }
}
```

## 📊 How to Run Analysis

- Use `trusted_execution/` for trusted swarm behavior
- Use `attacks/` for ML evaluations of adversarial attacks
- Use `results/` notebooks to reproduce confusion matrices and evaluation tables
