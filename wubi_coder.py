import argparse
from pywubi import wubi

def main():
    parser = argparse.ArgumentParser(
        description="Get Wubi codes for Chinese characters"
    )
    parser.add_argument("chars", nargs="+", help="Chinese characters to encode")
    args = parser.parse_args()
    # Join the character arguments into a single string
    input_chars = "".join(args.chars)
    # Get Wubi codes and print results
    codes = wubi(input_chars, single=False)
    print("\n".join(codes))

if __name__ == "__main__":
    main()
