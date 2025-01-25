from pywubi import wubi
import argparse


def wubi_coder(input_chars: str) -> str:
    # Get Wubi codes and print results
    codes = wubi(input_chars, single=False)
    # print("\n".join(codes))
    return input_chars + "\t" + "".join(codes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get Wubi codes for Chinese characters"
    )
    parser.add_argument("chars", nargs="+", help="Chinese characters to encode")
    args = parser.parse_args()
    # Join the character arguments into a single string
    input_chars = "".join(args.chars)
    res = wubi_coder(input_chars)
    # example usage:
    # python main.py 你好
    # 你好	qvbh
