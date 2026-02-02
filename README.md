# RAVEN - Simulator ("The Digital Twin")

![Raven Sim](https://img.shields.io/badge/Component-Simulator-purple) ![Status](https://img.shields.io/badge/Status-Active-success)

The **Simulator** provides a Gazebo-based virtual environment for developing and testing the Raven autonomous stack without physical hardware.

## 📚 Documentation
> **Full Technical Documentation:** [bosch-future-mobility-challenge-documentation.readthedocs-hosted.com](https://bosch-future-mobility-challenge-documentation.readthedocs-hosted.com)

---

## 🚀 Key Features

| Task ID | Feature Name | Description |
| :--- | :--- | :--- |
| **[008a]** | **Synthetic Data Generator** | Automated scripts to capture large-scale training datasets (Images + Labels). |
| **[Map]** | **BFMC Track 2025** | High-fidelity 3D model of the competition track including signs and traffic lights. |
| **[Car]** | **Raven Vehicle Model** | URDF model with simulated camera, IMU, and Ackermann steering physics. |

## 🛠️ Usage

### Launching the Simulation
```bash
# Launch the full environment with the car
roslaunch sim_pkg map_with_car.launch
```

### Data Collection
To run the synthetic data collection sequence:
```bash
roslaunch sim_pkg map_with_all_objects.launch
python3 src/utils/scripts/synthetic_capture.py
```
