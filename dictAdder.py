
from pywubi import wubi
import argparse


def wubi_coder(input_chars: str, dict_file: str) -> str:
    # Get Wubi codes if not found in dictionary
    codes = wubi(input_chars, single=False)
    new_entry = input_chars + "\t" + "".join(codes)
    # Check dictionary first
    with open(dict_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith(input_chars + "\t"):
                return f"[{new_entry}] already exists in dictionary"

    with open(dict_file, "a", encoding="utf-8") as f:
        f.write(new_entry + "\n")
    return f"[{new_entry}] added"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check dictionary and get Wubi codes for Chinese characters"
    )
    parser.add_argument("chars", nargs="+", help="Chinese characters to check/encode")
    parser.add_argument(
        "-d", "--dict", required=True, help="Path to the RIME dictionary file"
    )
    args = parser.parse_args()
    input_chars = "".join(args.chars)
    res = wubi_coder(input_chars, args.dict)
    print(res)
