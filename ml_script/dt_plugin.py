import airsim

class DigitalTwinPlugin:
    def __init__(self):
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()

    def get_actual_metrics(self, drone_id):
        """
        Retrieves the actual state of the drone from AirSim.
        Returns a dictionary with speed, centrality (placeholder), and sensor_ok (placeholder).
        """
        state = self.client.getMultirotorState(vehicle_name=drone_id)
        velocity = state.kinematics_estimated.linear_velocity
        speed = (velocity.x_val**2 + velocity.y_val**2 + velocity.z_val**2) ** 0.5

        sensor_ok = 1  # Placeholder: can be updated to real sensor checks
        centrality = 0.75  # Placeholder: optional real-time metric injection

        return {
            'speed': round(speed, 2),
            'sensor_ok': sensor_ok,
            'centrality': centrality
        }

    def verify_communication(self, sender_id, receiver_id, predicted_data):
        """
        Compares a drone's self-reported (predicted) state with its actual state in AirSim.
        Prints a trust check summary and returns the delta values and a trustworthiness flag.
        """
        actual = self.get_actual_metrics(sender_id)

        delta = {
            'speed': abs(predicted_data['speed'] - actual['speed']),
            'centrality': abs(predicted_data['centrality'] - actual['centrality']),
            'sensor': abs(predicted_data['sensor_ok'] - actual['sensor_ok'])
        }

        is_trustworthy = all(v < 0.1 for v in delta.values())

        print(f"[TRUST CHECK] {receiver_id} verified {sender_id}: "
              f"ΔSpeed={delta['speed']:.2f}, ΔCentrality={delta['centrality']:.2f}, ΔSensor={delta['sensor']} "
              f"=> {'TRUSTED ✅' if is_trustworthy else 'MALICIOUS ⚠️'}")

        return delta, is_trustworthy

    def verify_drone(self, predicted_data, actual_data):
        """
        Directly compares predicted and actual drone data.
        Useful for swarm-wide logging (used in multi_drone.py).
        """
        return {
            'speed': abs(predicted_data['speed'] - actual_data['speed']),
            'centrality': abs(predicted_data['centrality'] - actual_data['centrality']),
            'sensor': abs(predicted_data['sensor_ok'] - actual_data['sensor_ok'])
        }
