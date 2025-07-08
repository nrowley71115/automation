#!/usr/bin/env python3
"""
Program to convert a list of negative numbers into an Excel formula that sums their absolute values.
Automatically copies the result to the Mac clipboard.
"""

import subprocess
import sys

def copy_to_clipboard(text):
    """Copy text to Mac clipboard using pbcopy."""
    try:
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))
        return True
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        return False

def format_numbers_to_excel(numbers):
    """Convert list of negative numbers to Excel sum formula with absolute values."""
    # Convert to absolute values
    abs_numbers = [abs(float(num)) for num in numbers if num.strip()]
    
    # Format as Excel formula
    formula = "=" + "+".join(str(num) for num in abs_numbers)
    return formula

def main():
    print("Enter negative numbers (one per line). Press Enter on empty line to finish:")
    print("Example:")
    print("-44.9")
    print("-49.38")
    print("(empty line to finish)")
    print()
    
    numbers = []
    while True:
        try:
            line = input().strip()
            if not line:  # Empty line means we're done
                break
            
            # Try to parse as float to validate
            float(line)
            numbers.append(line)
            
        except ValueError:
            print(f"Invalid number: '{line}'. Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
    
    if not numbers:
        print("No numbers entered. Exiting.")
        return
    
    # Generate Excel formula
    excel_formula = format_numbers_to_excel(numbers)
    
    # Display result
    print("\nInput numbers:")
    for num in numbers:
        print(f"  {num}")
    
    print(f"\nExcel formula:")
    print(f'"{excel_formula}"')
    
    # Copy to clipboard
    if copy_to_clipboard(excel_formula):
        print("\n✅ Formula copied to clipboard!")
    else:
        print("\n❌ Failed to copy to clipboard")
    
    print("\nYou can now paste this formula directly into an Excel cell.")

if __name__ == "__main__":
    main()
