# main.py
# ------------------------------------------------------------
# Symbolic System Entry Point
# ------------------------------------------------------------
import os
import glob

# Import the new test execution function
# This relies on 'tests' being a package (i.e., having a __init__.py file)
from tests.test_vector_space import run_all_tests


def cleanup_temp_files():
    """
    Deletes all .aux, .log, and .tex files from the current directory
    (the home directory where main.py is executed).
    """
    print("\n--- Starting Housekeeping: Removing temporary LaTeX files ---")
    
    patterns = ['*.aux', '*.log', '*.tex']
    deleted_count = 0
    
    for pattern in patterns:
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
                # print(f"Deleted: {file_path}") # Optional: show every file deleted
                deleted_count += 1
            except OSError as e:
                print(f"Error deleting {file_path}: {e}")
                
    if deleted_count > 0:
        print(f"✅ Cleanup complete. Total files removed: {deleted_count}.")
    else:
        print("✅ No temporary files found for cleanup.")
    print("-----------------------------------------------------------")


def main():
    """
    Main entry point for the symbolic system demo.
    Runs all defined test cases and performs cleanup.
    """
    print("Khwarizmi Symbolic System Initialized.")
    
    # Run all test cases
    run_all_tests()
    
    # Perform housekeeping after tests
    cleanup_temp_files()


if __name__ == "__main__":
    main()