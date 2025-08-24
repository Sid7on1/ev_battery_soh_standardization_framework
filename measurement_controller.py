import logging
import time
from typing import Dict, List
from pyserial import Serial
from config_handler import ConfigHandler
from data_acquisition import DataAcquisition
from threading import Lock
from enum import Enum

# Constants
CHARGING_SESSION_TIMEOUT = 3600  # 1 hour
VOLTAGE_TOLERANCE = 0.1  # 0.1V
TEMPERATURE_TOLERANCE = 5  # 5°C
BALANCING_STATE_THRESHOLD = 0.5  # 0.5V

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChargingSessionStatus(Enum):
    INITIATED = 1
    IN_PROGRESS = 2
    TERMINATED = 3
    FAILED = 4

class MeasurementController:
    def __init__(self, config_handler: ConfigHandler, data_acquisition: DataAcquisition):
        """
        Initializes the MeasurementController instance.

        Args:
        - config_handler (ConfigHandler): Configuration handler instance.
        - data_acquisition (DataAcquisition): Data acquisition instance.
        """
        self.config_handler = config_handler
        self.data_acquisition = data_acquisition
        self.charging_session_status = ChargingSessionStatus.INITIATED
        self.lock = Lock()
        self.serial_connection = None

    def initiate_charging_session(self) -> bool:
        """
        Initiates a new charging session.

        Returns:
        - bool: True if the session was initiated successfully, False otherwise.
        """
        try:
            # Establish serial connection
            self.serial_connection = Serial(self.config_handler.get_serial_port(), self.config_handler.get_baudrate())
            # Send initiation command to the charging device
            self.serial_connection.write(b'initiate_charging_session')
            # Wait for confirmation
            response = self.serial_connection.readline().decode('utf-8')
            if response == 'charging_session_initiated':
                self.charging_session_status = ChargingSessionStatus.IN_PROGRESS
                logging.info('Charging session initiated successfully')
                return True
            else:
                logging.error('Failed to initiate charging session')
                return False
        except Exception as e:
            logging.error(f'Error initiating charging session: {e}')
            return False

    def monitor_voltage_range(self) -> bool:
        """
        Monitors the voltage range during the charging session.

        Returns:
        - bool: True if the voltage range is within the tolerance, False otherwise.
        """
        try:
            # Read voltage from the data acquisition device
            voltage = self.data_acquisition.read_voltage()
            # Check if the voltage is within the tolerance
            if abs(voltage - self.config_handler.get_target_voltage()) <= VOLTAGE_TOLERANCE:
                logging.info(f'Voltage is within tolerance: {voltage}V')
                return True
            else:
                logging.warning(f'Voltage is out of tolerance: {voltage}V')
                return False
        except Exception as e:
            logging.error(f'Error monitoring voltage range: {e}')
            return False

    def enforce_temperature_limits(self) -> bool:
        """
        Enforces the temperature limits during the charging session.

        Returns:
        - bool: True if the temperature is within the tolerance, False otherwise.
        """
        try:
            # Read temperature from the data acquisition device
            temperature = self.data_acquisition.read_temperature()
            # Check if the temperature is within the tolerance
            if abs(temperature - self.config_handler.get_target_temperature()) <= TEMPERATURE_TOLERANCE:
                logging.info(f'Temperature is within tolerance: {temperature}°C')
                return True
            else:
                logging.warning(f'Temperature is out of tolerance: {temperature}°C')
                return False
        except Exception as e:
            logging.error(f'Error enforcing temperature limits: {e}')
            return False

    def handle_balancing_states(self) -> bool:
        """
        Handles the balancing states during the charging session.

        Returns:
        - bool: True if the balancing state is within the threshold, False otherwise.
        """
        try:
            # Read balancing state from the data acquisition device
            balancing_state = self.data_acquisition.read_balancing_state()
            # Check if the balancing state is within the threshold
            if abs(balancing_state - self.config_handler.get_target_balancing_state()) <= BALANCING_STATE_THRESHOLD:
                logging.info(f'Balancing state is within threshold: {balancing_state}V')
                return True
            else:
                logging.warning(f'Balancing state is out of threshold: {balancing_state}V')
                return False
        except Exception as e:
            logging.error(f'Error handling balancing states: {e}')
            return False

    def terminate_session(self) -> bool:
        """
        Terminates the charging session.

        Returns:
        - bool: True if the session was terminated successfully, False otherwise.
        """
        try:
            # Send termination command to the charging device
            self.serial_connection.write(b'terminate_charging_session')
            # Wait for confirmation
            response = self.serial_connection.readline().decode('utf-8')
            if response == 'charging_session_terminated':
                self.charging_session_status = ChargingSessionStatus.TERMINATED
                logging.info('Charging session terminated successfully')
                return True
            else:
                logging.error('Failed to terminate charging session')
                return False
        except Exception as e:
            logging.error(f'Error terminating charging session: {e}')
            return False

    def get_charging_session_status(self) -> ChargingSessionStatus:
        """
        Gets the current charging session status.

        Returns:
        - ChargingSessionStatus: The current charging session status.
        """
        return self.charging_session_status

    def is_charging_session_in_progress(self) -> bool:
        """
        Checks if the charging session is in progress.

        Returns:
        - bool: True if the charging session is in progress, False otherwise.
        """
        return self.charging_session_status == ChargingSessionStatus.IN_PROGRESS

    def close_serial_connection(self) -> None:
        """
        Closes the serial connection.
        """
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None

class MeasurementControllerException(Exception):
    """
    Custom exception for MeasurementController.
    """
    pass

def main():
    # Create configuration handler instance
    config_handler = ConfigHandler()
    # Create data acquisition instance
    data_acquisition = DataAcquisition()
    # Create measurement controller instance
    measurement_controller = MeasurementController(config_handler, data_acquisition)
    # Initiate charging session
    if measurement_controller.initiate_charging_session():
        # Monitor voltage range
        while measurement_controller.is_charging_session_in_progress():
            if not measurement_controller.monitor_voltage_range():
                # Enforce temperature limits
                if not measurement_controller.enforce_temperature_limits():
                    # Handle balancing states
                    if not measurement_controller.handle_balancing_states():
                        # Terminate session
                        measurement_controller.terminate_session()
                        break
            time.sleep(1)
        # Close serial connection
        measurement_controller.close_serial_connection()
    else:
        logging.error('Failed to initiate charging session')

if __name__ == '__main__':
    main()