import argparse
import logging
import sys
from typing import Dict, List

import config_handler
import main_soh_analyzer
from config_handler import ConfigHandler
from main_soh_analyzer import MainSOHAnalyzer
from soh_calculator import SOHCalculator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CLIInterface:
    def __init__(self):
        self.config_handler = ConfigHandler()
        self.main_soh_analyzer = MainSOHAnalyzer()
        self.soh_calculator = SOHCalculator()

    def parse_arguments(self) -> argparse.Namespace:
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(description='SOH Analysis CLI Interface')
        parser.add_argument('-c', '--config', help='Path to configuration file')
        parser.add_argument('-i', '--interactive', action='store_true', help='Run in interactive mode')
        parser.add_argument('-r', '--results', help='Path to save results')
        parser.add_argument('-d', '--data', help='Path to raw data file')
        return parser.parse_args()

    def run_interactive_mode(self, args: argparse.Namespace) -> None:
        """Run the CLI interface in interactive mode."""
        while True:
            print('SOH Analysis CLI Interface')
            print('---------------------------')
            print('1. Run SOH analysis')
            print('2. Display results')
            print('3. Export raw data')
            print('4. Quit')
            choice = input('Enter your choice: ')
            if choice == '1':
                self.main_soh_analyzer.run_soh_analysis()
            elif choice == '2':
                self.display_results()
            elif choice == '3':
                self.export_raw_data(args.data)
            elif choice == '4':
                break
            else:
                print('Invalid choice. Please try again.')

    def display_results(self) -> None:
        """Display the results of the SOH analysis."""
        results = self.main_soh_analyzer.get_results()
        print('SOH Analysis Results:')
        print('---------------------')
        for key, value in results.items():
            print(f'{key}: {value}')

    def export_raw_data(self, data_path: str) -> None:
        """Export the raw data to a file."""
        try:
            with open(data_path, 'w') as f:
                f.write(self.main_soh_analyzer.get_raw_data())
            print(f'Raw data saved to {data_path}')
        except Exception as e:
            logger.error(f'Error exporting raw data: {e}')

    def run(self) -> None:
        """Run the CLI interface."""
        args = self.parse_arguments()
        if args.config:
            self.config_handler.load_config(args.config)
        if args.interactive:
            self.run_interactive_mode(args)
        else:
            self.main_soh_analyzer.run_soh_analysis()
            self.display_results()
            if args.results:
                self.export_raw_data(args.results)

def main() -> None:
    cli_interface = CLIInterface()
    cli_interface.run()

if __name__ == '__main__':
    main()