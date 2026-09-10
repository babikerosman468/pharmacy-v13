#!/usr/bin/env python3

import json


def show_data(title, filename):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"Records: {len(data)}")

        for item in data[:3]:
            print(json.dumps(item, ensure_ascii=False, indent=2))

    except FileNotFoundError:
        print(f"ERROR: File not found: {filename}")

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}")


def main():
    print("=" * 60)
    print("PHARMACY V13 — DATA INSPECTION")
    print("=" * 60)

    show_data(
        "PURCHASE DATA",
        "data/purchases.json"
    )

    show_data(
        "SUPPLIER DATA",
        "data/suppliers.json"
    )


if __name__ == "__main__":
    main()

