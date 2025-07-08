# word_counter.py

import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR: Expected a single string input.")
        sys.exit(1)

    text = sys.argv[1]
    word_count = len(text.strip().split())
    print(f"WORD_COUNT: {word_count}")
