from pywubi import wubi
import argparse


dict_file = "/home/xinyu/.config/ibus/rime/wubi86_jidian_user.dict.yaml"


def wubi_coder(input_chars: str) -> str:
    # Check dictionary first
    with open(dict_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith(input_chars + "\t"):
                return f"{input_chars} already exists in dictionary"

    # Get Wubi codes if not found in dictionary
    codes = wubi(input_chars, single=False)
    new_entry = input_chars + "\t" + "".join(codes)
    with open(dict_file, "a", encoding="utf-8") as f:
        f.write(new_entry + "\n")
    return new_entry


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check dictionary and get Wubi codes for Chinese characters"
    )
    parser.add_argument("chars", nargs="+", help="Chinese characters to check/encode")
    args = parser.parse_args()
    input_chars = "".join(args.chars)
    res = wubi_coder(input_chars)
    print(res, "added")
