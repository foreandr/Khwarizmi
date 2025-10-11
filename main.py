# main.py
# ------------------------------------------------------------
# Symbolic System Entry Point
# ------------------------------------------------------------
import os
import glob
import shutil # Still needed for deleting subdirectories (if any)

# Import the new test execution function
# This relies on 'tests' being a package (i.e., having a __init__.py file)
from tests.test_vector_space import run_all_tests


def cleanup_pdf_folder(folder_path="pdf_folder"):
    """
    Deletes ALL files and subdirectories inside the specified folder,
    but keeps the folder itself intact.
    """
    print(f"\n--- Starting Pre-Test Cleanup: Emptying '{folder_path}' ---")
    
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        deleted_count = 0
        # The pattern '*' matches all files and directories inside the folder
        files_and_dirs = glob.glob(os.path.join(folder_path, '*'))
        
        for item in files_and_dirs:
            try:
                if os.path.isfile(item) or os.path.islink(item):
                    os.remove(item)  # Delete files
                elif os.path.isdir(item):
                    shutil.rmtree(item)  # Recursively delete subdirectories
                deleted_count += 1
            except OSError as e:
                print(f"❌ Error deleting {item}: {e}")
                
        if deleted_count > 0:
            print(f"✅ Successfully removed {deleted_count} items from '{folder_path}'.")
        else:
             print(f"✅ Folder '{folder_path}' was already empty.")
    else:
        # If the folder doesn't exist, we can optionally create it to ensure
        # it's there for the tests, but for pure cleanup, we just note it.
        print(f"✅ Folder '{folder_path}' does not exist, no cleanup needed.")
        
    print("---------------------------------------------------------------")


def cleanup_temp_files():
    """
    Deletes all .aux, .log, and .tex files from the current directory
    (the home directory where main.py is executed).
    """
    # ... (Rest of the cleanup_temp_files function remains the same)
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
    
    # --- Corrected Pre-Test Cleanup: Empties the folder ---
    cleanup_pdf_folder()
    
    # Run all test cases
    run_all_tests()
    
    # Perform housekeeping after tests
    cleanup_temp_files()


if __name__ == "__main__":
    main()