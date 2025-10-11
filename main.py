# main.py
# ------------------------------------------------------------
# Symbolic System Entry Point
# ------------------------------------------------------------

# Import the new test execution function
# This relies on 'tests' being a package (i.e., having a __init__.py file)
from tests.test_vector_space import run_all_tests


def main():
    """
    Main entry point for the symbolic system demo.
    Runs all defined test cases.
    """
    print("Khwarizmi Symbolic System Initialized.")
    
    # Run all test cases
    run_all_tests()


if __name__ == "__main__":
    main()