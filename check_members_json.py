"""
Script to check the structure of the members.json file.

This script loads the members.json file and prints the structure of the first member
to help diagnose issues with missing fields.
"""

import json
import os
import sys

def main():
    """Main entry point for the script."""
    # Define the path to the members.json file
    processed_dir = os.path.join(os.path.dirname(__file__), 'output', 'processed')
    members_file = os.path.join(processed_dir, 'members.json')
    
    # Check if the file exists
    if not os.path.exists(members_file):
        print(f"Error: Members data file '{members_file}' does not exist.")
        sys.exit(1)
    
    # Load the file
    try:
        with open(members_file, 'r') as f:
            members = json.load(f)
    except Exception as e:
        print(f"Error loading members.json: {e}")
        sys.exit(1)
    
    # Check if there are any members
    if not members:
        print("Error: No members found in the file.")
        sys.exit(1)
    
    # Print the structure of the first member
    first_member = members[0]
    print("First member structure:")
    print(json.dumps(first_member, indent=2))
    
    # Check for specific fields
    print("\nChecking for specific fields:")
    print(f"gender: {first_member.get('gender', 'NOT FOUND')}")
    print(f"insurance: {first_member.get('insurance', 'NOT FOUND')}")
    
    if first_member.get('insurance'):
        print(f"plan_name: {first_member['insurance'].get('plan_name', 'NOT FOUND')}")
        print(f"effective_date: {first_member['insurance'].get('effective_date', 'NOT FOUND')}")
    
    # Check all members for missing fields
    missing_gender = 0
    missing_plan_name = 0
    missing_effective_date = 0
    
    for member in members:
        if not member.get('gender'):
            missing_gender += 1
        
        if not member.get('insurance') or not member['insurance'].get('plan_name'):
            missing_plan_name += 1
        
        if not member.get('insurance') or not member['insurance'].get('effective_date'):
            missing_effective_date += 1
    
    print(f"\nOut of {len(members)} members:")
    print(f"Missing gender: {missing_gender} ({missing_gender/len(members)*100:.1f}%)")
    print(f"Missing plan_name: {missing_plan_name} ({missing_plan_name/len(members)*100:.1f}%)")
    print(f"Missing effective_date: {missing_effective_date} ({missing_effective_date/len(members)*100:.1f}%)")

if __name__ == "__main__":
    main()