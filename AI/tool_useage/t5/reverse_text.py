# reverse_text.py

import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR: Expected a single string input.")
        sys.exit(1)

    text = sys.argv[1]
    reversed_text = text[::-1]
    print(f"REVERSED: {reversed_text}")
