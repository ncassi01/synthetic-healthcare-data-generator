#!/usr/bin/env python
"""
Script to run the web application for the Synthetic Healthcare Data Viewer.

This script provides a convenient way to start the web application
and handles common command-line arguments.
"""

import argparse
import os
import sys
from web.app import app

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run the Synthetic Healthcare Data Viewer web application')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to run the web application on (default: 5000)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host to run the web application on (default: 127.0.0.1)')
    parser.add_argument('--debug', action='store_true',
                        help='Run the web application in debug mode')
    return parser.parse_args()

def main():
    """Main entry point for the script."""
    args = parse_args()
    
    # Check if output directory exists
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    if not os.path.exists(output_dir):
        print(f"Error: Output directory '{output_dir}' does not exist.")
        print("Please run the data generation pipeline first:")
        print("  python src/main.py --process --stats")
        sys.exit(1)
    
    # Check if processed data exists
    processed_dir = os.path.join(output_dir, 'processed')
    if not os.path.exists(processed_dir):
        print(f"Error: Processed data directory '{processed_dir}' does not exist.")
        print("Please run the data generation pipeline with the --process flag:")
        print("  python src/main.py --process --stats")
        sys.exit(1)
    
    # Check if members.json exists
    members_file = os.path.join(processed_dir, 'members.json')
    if not os.path.exists(members_file):
        print(f"Error: Members data file '{members_file}' does not exist.")
        print("Please run the data generation pipeline to generate member data:")
        print("  python src/main.py --process --stats")
        sys.exit(1)
    
    print(f"Starting Synthetic Healthcare Data Viewer on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    
    # Run the Flask application
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()