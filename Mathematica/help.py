import os

def file_lengths_in_current_dir():
    """Evaluate and print the byte size and line count of all files in ./"""
    cwd = os.getcwd()
    print(f"Scanning directory: {cwd}\n")

    for filename in os.listdir(cwd):
        path = os.path.join(cwd, filename)

        # Skip directories
        if os.path.isdir(path):
            continue

        try:
            # Get file size (in bytes)
            size_bytes = os.path.getsize(path)

            # Count lines (if text-readable)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    num_lines = sum(1 for _ in f)
            except UnicodeDecodeError:
                num_lines = "N/A (binary file)"

            print(f"{filename:40} | {size_bytes:10} bytes | {num_lines} lines")

        except Exception as e:
            print(f"Error reading {filename}: {e}")

if __name__ == "__main__":
    file_lengths_in_current_dir()
