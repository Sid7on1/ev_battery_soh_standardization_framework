import os
import json
import logging
import yaml
from typing import Dict, List, Tuple
from enum import Enum
from threading import Lock

# Define constants and configuration
CONFIG_FILE = 'vehicle_config.yaml'
PARAMETERS_FILE = 'measurement_parameters.json'
REFERENCE_VALUES_FILE = 'reference_values.json'

# Define logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Define file handler and set level to debug
file_handler = logging.FileHandler('config_handler.log')
file_handler.setLevel(logging.DEBUG)

# Create formatter and add it to the file handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

class ConfigError(Exception):
    """Base class for configuration-related exceptions."""
    pass

class InvalidConfigError(ConfigError):
    """Raised when the configuration is invalid."""
    pass

class ConfigHandler:
    """Manages vehicle-specific configurations and measurement parameters."""

    def __init__(self, config_file: str = CONFIG_FILE, parameters_file: str = PARAMETERS_FILE, reference_values_file: str = REFERENCE_VALUES_FILE):
        """
        Initializes the ConfigHandler instance.

        Args:
        - config_file (str): The path to the configuration file.
        - parameters_file (str): The path to the measurement parameters file.
        - reference_values_file (str): The path to the reference values file.
        """
        self.config_file = config_file
        self.parameters_file = parameters_file
        self.reference_values_file = reference_values_file
        self.config = None
        self.parameters = None
        self.reference_values = None
        self.lock = Lock()

    def load_vehicle_config(self) -> Dict:
        """
        Loads the vehicle configuration from the configuration file.

        Returns:
        - A dictionary containing the vehicle configuration.

        Raises:
        - InvalidConfigError: If the configuration file is invalid.
        """
        try:
            with self.lock:
                with open(self.config_file, 'r') as file:
                    self.config = yaml.safe_load(file)
                    if not self.config:
                        raise InvalidConfigError("Invalid configuration file")
                    return self.config
        except yaml.YAMLError as e:
            logger.error(f"Failed to load configuration: {e}")
            raise InvalidConfigError("Invalid configuration file")

    def validate_parameters(self, parameters: Dict) -> bool:
        """
        Validates the measurement parameters.

        Args:
        - parameters (Dict): A dictionary containing the measurement parameters.

        Returns:
        - True if the parameters are valid, False otherwise.
        """
        required_keys = ['voltage_range', 'current_range', 'temperature_range']
        for key in required_keys:
            if key not in parameters:
                logger.error(f"Missing required parameter: {key}")
                return False
        return True

    def update_voltage_ranges(self, voltage_ranges: List[Tuple[float, float]]) -> None:
        """
        Updates the voltage ranges in the measurement parameters.

        Args:
        - voltage_ranges (List[Tuple[float, float]]): A list of tuples containing the voltage ranges.
        """
        try:
            with self.lock:
                if not self.parameters:
                    self.load_parameters()
                self.parameters['voltage_range'] = voltage_ranges
                with open(self.parameters_file, 'w') as file:
                    json.dump(self.parameters, file)
        except Exception as e:
            logger.error(f"Failed to update voltage ranges: {e}")

    def store_reference_values(self, reference_values: Dict) -> None:
        """
        Stores the reference values in the reference values file.

        Args:
        - reference_values (Dict): A dictionary containing the reference values.
        """
        try:
            with self.lock:
                with open(self.reference_values_file, 'w') as file:
                    json.dump(reference_values, file)
        except Exception as e:
            logger.error(f"Failed to store reference values: {e}")

    def load_parameters(self) -> Dict:
        """
        Loads the measurement parameters from the parameters file.

        Returns:
        - A dictionary containing the measurement parameters.

        Raises:
        - InvalidConfigError: If the parameters file is invalid.
        """
        try:
            with self.lock:
                with open(self.parameters_file, 'r') as file:
                    self.parameters = json.load(file)
                    if not self.parameters:
                        raise InvalidConfigError("Invalid parameters file")
                    return self.parameters
        except json.JSONDecodeError as e:
            logger.error(f"Failed to load parameters: {e}")
            raise InvalidConfigError("Invalid parameters file")

    def get_reference_values(self) -> Dict:
        """
        Gets the reference values from the reference values file.

        Returns:
        - A dictionary containing the reference values.

        Raises:
        - InvalidConfigError: If the reference values file is invalid.
        """
        try:
            with self.lock:
                with open(self.reference_values_file, 'r') as file:
                    self.reference_values = json.load(file)
                    if not self.reference_values:
                        raise InvalidConfigError("Invalid reference values file")
                    return self.reference_values
        except json.JSONDecodeError as e:
            logger.error(f"Failed to load reference values: {e}")
            raise InvalidConfigError("Invalid reference values file")

class VehicleConfig:
    """Represents a vehicle configuration."""

    def __init__(self, config: Dict):
        """
        Initializes the VehicleConfig instance.

        Args:
        - config (Dict): A dictionary containing the vehicle configuration.
        """
        self.config = config

    def get_parameter(self, parameter: str) -> str:
        """
        Gets a parameter from the vehicle configuration.

        Args:
        - parameter (str): The name of the parameter.

        Returns:
        - The value of the parameter.
        """
        return self.config.get(parameter)

class MeasurementParameters:
    """Represents measurement parameters."""

    def __init__(self, parameters: Dict):
        """
        Initializes the MeasurementParameters instance.

        Args:
        - parameters (Dict): A dictionary containing the measurement parameters.
        """
        self.parameters = parameters

    def get_parameter(self, parameter: str) -> str:
        """
        Gets a parameter from the measurement parameters.

        Args:
        - parameter (str): The name of the parameter.

        Returns:
        - The value of the parameter.
        """
        return self.parameters.get(parameter)

def main():
    config_handler = ConfigHandler()
    config = config_handler.load_vehicle_config()
    vehicle_config = VehicleConfig(config)
    parameters = config_handler.load_parameters()
    measurement_parameters = MeasurementParameters(parameters)
    print(vehicle_config.get_parameter('vehicle_id'))
    print(measurement_parameters.get_parameter('voltage_range'))

if __name__ == '__main__':
    main()