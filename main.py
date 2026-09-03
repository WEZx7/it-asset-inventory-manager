import json
import os
from datetime import datetime


ASSETS_FILE = "assets.json"


def load_assets():
    if not os.path.exists(ASSETS_FILE):
        return []

    try:
        with open(ASSETS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_assets():
    with open(ASSETS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            assets,
            file,
            indent=4,
            ensure_ascii=False
        )


def generate_asset_id():
    if not assets:
        return "IT-0001"

    highest_id = max(
        int(asset["asset_id"].split("-")[1])
        for asset in assets
    )

    return f"IT-{highest_id + 1:04d}"


def add_asset():
    print("\n================================")
    print("           ADD ASSET")
    print("================================")

    asset_type = input("Asset Type: ").strip()
    brand = input("Brand: ").strip()
    model = input("Model: ").strip()
    serial_number = input("Serial Number: ").strip()
    location = input("Location: ").strip()

    if not asset_type:
        print("\nAsset type cannot be empty.")
        return

    if not serial_number:
        print("\nSerial number cannot be empty.")
        return

    for asset in assets:
        if asset["serial_number"].lower() == serial_number.lower():
            print("\nAn asset with this serial number already exists.")
            return

    asset = {
        "asset_id": generate_asset_id(),
        "type": asset_type,
        "brand": brand,
        "model": model,
        "serial_number": serial_number,
        "status": "Available",
        "assigned_user": "Unassigned",
        "department": "Unassigned",
        "location": location,
        "created_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    assets.append(asset)
    save_assets()

    print(
        f"\nAsset {asset['asset_id']} "
        f"added successfully."
    )


def display_asset(asset):
    print("\n--------------------------------")
    print(f"Asset ID: {asset['asset_id']}")
    print(f"Type: {asset['type']}")
    print(f"Brand: {asset['brand']}")
    print(f"Model: {asset['model']}")
    print(f"Serial Number: {asset['serial_number']}")
    print(f"Status: {asset['status']}")
    print(f"Assigned User: {asset['assigned_user']}")
    print(f"Department: {asset['department']}")
    print(f"Location: {asset['location']}")
    print(f"Added: {asset['created_at']}")


def view_assets():
    print("\n================================")
    print("          ALL ASSETS")
    print("================================")

    if not assets:
        print("\nNo assets available.")
        return

    for asset in assets:
        display_asset(asset)


def search_assets():
    print("\n================================")
    print("         SEARCH ASSETS")
    print("================================")

    if not assets:
        print("\nNo assets available.")
        return

    search_term = input(
        "Enter Asset ID, serial number, brand, model, or type: "
    ).strip().lower()

    results = []

    for asset in assets:
        searchable_values = [
            asset["asset_id"],
            asset["serial_number"],
            asset["brand"],
            asset["model"],
            asset["type"],
            asset["status"],
            asset["assigned_user"],
            asset["department"],
            asset["location"]
        ]

        if any(
            search_term in str(value).lower()
            for value in searchable_values
        ):
            results.append(asset)

    if not results:
        print("\nNo matching assets found.")
        return

    print(
        f"\nFound {len(results)} matching asset(s):"
    )

    for asset in results:
        display_asset(asset)


assets = load_assets()


def main():
    while True:
        print("\n================================")
        print("        IT ASSET MANAGER")
        print("================================")
        print("1. Add Asset")
        print("2. View Assets")
        print("3. Search Assets")
        print("4. Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            add_asset()

        elif choice == "2":
            view_assets()

        elif choice == "3":
            search_assets()

        elif choice == "4":
            print("\nExiting IT Asset Manager...")
            break

        else:
            print("\nInvalid option. Please select 1-4.")


if __name__ == "__main__":
    main()
