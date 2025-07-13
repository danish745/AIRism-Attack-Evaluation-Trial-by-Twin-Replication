# AiRism-Attack-Evaluation (Trial-by-Twin-Replication)

This repository contains the complete codebase, data, models, and evaluation for reproducing the experiments described in the paper *Trial by Twin: Behavior-Predictive Trust in Autonomous Drone Swarms*.

## 🧠 Project Structure

```
AiRism-Attack-Evaluation/
├── attacks/                  # Jupyter notebooks for each attack type
├── trusted_execution/        # Notebooks for simulation and trusted analysis
├── data/                     # Simulation log datasets (normal + attacks)
├── results/
│   ├── coordination_plots/   # Coordination rate plots
│   ├── confusion_matrix_grid.png
│   ├── evaluation.png
│   └── *.ipynb               # Evaluation notebooks
├── README.md
└── requirements.txt
```

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
C:\\Users\\danis\\AirSim\\Unreal\\Environments\\Blocks
```

2. Start simulation:
```bash
cd C:\\Users\\danis\\AirSim\\PythonClient\\multirotor
python multi_drone.py
```

## ⚙️ AirSim settings.json

Create the following file at:
```
C:\\Users\\danis\\Documents\\AirSim\\settings.json
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

## 📄 Citation

```bibtex
@inproceedings{airism2025,
  title     = {AiRism-Attack-Evaluation: Trial-by-Twin for Behavior-Predictive Trust in Autonomous Drone Swarms},
  author    = {Your Name and Co-authors},
  booktitle = {Proceedings of the [Conference Name]},
  year      = {2025},
  url       = {https://github.com/yourusername/AiRism-Attack-Evaluation}
}
```

---