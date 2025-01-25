import argparse
from wubi import wubi_dict


def get_wubi_code(chars):
    """Get Wubi codes for a list of Chinese characters"""
    results = []
    for char in chars:
        # Check if character exists in wubi dictionary
        if char in wubi_dict:
            # Get the Wubi code directly from the dictionary
            code = wubi_dict[char].strip()
            results.append(f"{char}: {code}")
        else:
            results.append(f"{char}: Not found in Wubi encoding")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get Wubi codes for Chinese characters"
    )
    parser.add_argument("chars", nargs="+", help="Chinese characters to encode")
    args = parser.parse_args()

    codes = get_wubi_code(args.chars)
    print("\n".join(codes))
