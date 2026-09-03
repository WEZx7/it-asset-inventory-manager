import json
import os
from datetime import datetime


ASSETS_FILE = "assets.json"


def current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_assets():
    if not os.path.exists(ASSETS_FILE):
        return []

    try:
        with open(ASSETS_FILE, "r", encoding="utf-8") as file:
            loaded_assets = json.load(file)

        if not isinstance(loaded_assets, list):
            return []

        for asset in loaded_assets:
            asset.setdefault("status", "Available")
            asset.setdefault("assigned_user", "Unassigned")
            asset.setdefault("department", "Unassigned")
            asset.setdefault("location", "Unknown")
            asset.setdefault("created_at", "Unknown")
            asset.setdefault("updated_at", "Unknown")
            asset.setdefault("assigned_at", "")
            asset.setdefault("returned_at", "")
            asset.setdefault("retired_at", "")

        return loaded_assets

    except (json.JSONDecodeError, OSError):
        return []


def save_assets():
    try:
        with open(ASSETS_FILE, "w", encoding="utf-8") as file:
            json.dump(assets, file, indent=4, ensure_ascii=False)

    except OSError as error:
        print(f"\nUnable to save assets: {error}")


def generate_asset_id():
    if not assets:
        return "IT-0001"

    numbers = []

    for asset in assets:
        asset_id = asset.get("asset_id", "")

        if asset_id.startswith("IT-"):
            try:
                numbers.append(int(asset_id.split("-")[1]))
            except ValueError:
                pass

    if not numbers:
        return "IT-0001"

    return f"IT-{max(numbers) + 1:04d}"


def find_asset(asset_id):
    asset_id = asset_id.strip().upper()

    for asset in assets:
        if asset.get("asset_id", "").upper() == asset_id:
            return asset

    return None


def serial_exists(serial_number, current_asset=None):
    for asset in assets:
        if asset is current_asset:
            continue

        if asset.get("serial_number", "").lower() == serial_number.lower():
            return True

    return False


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

    if serial_exists(serial_number):
        print("\nAn asset with this serial number already exists.")
        return

    timestamp = current_timestamp()

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
        "created_at": timestamp,
        "updated_at": timestamp,
        "assigned_at": "",
        "returned_at": "",
        "retired_at": ""
    }

    assets.append(asset)
    save_assets()

    print(f"\nAsset {asset['asset_id']} added successfully.")


def display_asset(asset):
    print("\n--------------------------------")
    print(f"Asset ID: {asset.get('asset_id', 'Unknown')}")
    print(f"Type: {asset.get('type', 'Unknown')}")
    print(f"Brand: {asset.get('brand', 'Unknown')}")
    print(f"Model: {asset.get('model', 'Unknown')}")
    print(f"Serial Number: {asset.get('serial_number', 'Unknown')}")
    print(f"Status: {asset.get('status', 'Available')}")
    print(f"Assigned User: {asset.get('assigned_user', 'Unassigned')}")
    print(f"Department: {asset.get('department', 'Unassigned')}")
    print(f"Location: {asset.get('location', 'Unknown')}")
    print(f"Added: {asset.get('created_at', 'Unknown')}")

    if asset.get("assigned_at"):
        print(f"Assigned At: {asset['assigned_at']}")

    if asset.get("returned_at"):
        print(f"Last Returned: {asset['returned_at']}")

    if asset.get("retired_at"):
        print(f"Retired At: {asset['retired_at']}")

    print(f"Last Updated: {asset.get('updated_at', 'Unknown')}")


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

    search_term = input("Enter Asset ID, serial number, brand, model, user, or type: ").strip().lower()

    if not search_term:
        print("\nSearch cannot be empty.")
        return

    results = []

    for asset in assets:
        searchable_values = [
            asset.get("asset_id", ""),
            asset.get("serial_number", ""),
            asset.get("brand", ""),
            asset.get("model", ""),
            asset.get("type", ""),
            asset.get("status", ""),
            asset.get("assigned_user", ""),
            asset.get("department", ""),
            asset.get("location", "")
        ]

        if any(search_term in str(value).lower() for value in searchable_values):
            results.append(asset)

    if not results:
        print("\nNo matching assets found.")
        return

    print(f"\nFound {len(results)} matching asset(s):")

    for asset in results:
        display_asset(asset)


def assign_asset():
    print("\n================================")
    print("          ASSIGN ASSET")
    print("================================")

    if not assets:
        print("\nNo assets available.")
        return

    asset_id = input("Enter Asset ID: ").strip()
    asset = find_asset(asset_id)

    if asset is None:
        print("\nAsset not found.")
        return

    if asset.get("status") == "In Use":
        print(f"\nAsset {asset['asset_id']} is already assigned to {asset.get('assigned_user', 'Unknown')}.")
        return

    if asset.get("status") == "Retired":
        print("\nA retired asset cannot be assigned.")
        return

    print(f"\nAsset: {asset['asset_id']}")
    print(f"Device: {asset.get('brand', '')} {asset.get('model', '')}")
    print(f"Current Status: {asset.get('status', 'Available')}")

    user = input("Assign to user: ").strip()
    department = input("Department: ").strip()

    if not user:
        print("\nUser name cannot be empty.")
        return

    if not department:
        department = "Unknown"

    timestamp = current_timestamp()

    asset["assigned_user"] = user
    asset["department"] = department
    asset["status"] = "In Use"
    asset["assigned_at"] = timestamp
    asset["returned_at"] = ""
    asset["updated_at"] = timestamp

    save_assets()

    print(f"\nAsset {asset['asset_id']} assigned to {user} successfully.")


def return_asset():
    print("\n================================")
    print("          RETURN ASSET")
    print("================================")

    if not assets:
        print("\nNo assets available.")
        return

    asset_id = input("Enter Asset ID: ").strip()
    asset = find_asset(asset_id)

    if asset is None:
        print("\nAsset not found.")
        return

    if asset.get("assigned_user", "Unassigned") == "Unassigned":
        print(f"\nAsset {asset['asset_id']} is not currently assigned.")
        return

    previous_user = asset.get("assigned_user", "Unknown")

    print(f"\nAsset: {asset['asset_id']}")
    print(f"Assigned User: {previous_user}")

    confirm = input("Return this asset? (yes/no): ").strip().lower()

    if confirm not in ["yes", "y"]:
        print("\nReturn cancelled.")
        return

    timestamp = current_timestamp()

    asset["assigned_user"] = "Unassigned"
    asset["department"] = "Unassigned"
    asset["status"] = "Available"
    asset["returned_at"] = timestamp
    asset["updated_at"] = timestamp

    save_assets()

    print(f"\nAsset {asset['asset_id']} returned successfully.")
    print(f"Previous User: {previous_user}")


def update_asset():
    print("\n================================")
    print("          UPDATE ASSET")
    print("================================")

    if not assets:
        print("\nNo assets available.")
        return

    asset_id = input("Enter Asset ID: ").strip()
    asset = find_asset(asset_id)

    if asset is None:
        print("\nAsset not found.")
        return

    print("\nCurrent Asset Information:")
    display_asset(asset)

    print("\nLeave a field blank to keep the current value.")

    new_type = input(f"Asset Type [{asset.get('type', '')}]: ").strip()
    new_brand = input(f"Brand [{asset.get('brand', '')}]: ").strip()
    new_model = input(f"Model [{asset.get('model', '')}]: ").strip()
    new_serial = input(f"Serial Number [{asset.get('serial_number', '')}]: ").strip()
    new_location = input(f"Location [{asset.get('location', '')}]: ").strip()

    if new_serial and serial_exists(new_serial, asset):
        print("\nAnother asset already uses this serial number.")
        return

    if new_type:
        asset["type"] = new_type

    if new_brand:
        asset["brand"] = new_brand

    if new_model:
        asset["model"] = new_model

    if new_serial:
        asset["serial_number"] = new_serial

    if new_location:
        asset["location"] = new_location

    asset["updated_at"] = current_timestamp()

    save_assets()

    print(f"\nAsset {asset['asset_id']} updated successfully.")


def retire_asset():
    print("\n================================")
    print("          RETIRE ASSET")
    print("================================")

    if not assets:
        print("\nNo assets available.")
        return

    asset_id = input("Enter Asset ID: ").strip()
    asset = find_asset(asset_id)

    if asset is None:
        print("\nAsset not found.")
        return

    if asset.get("status") == "Retired":
        print(f"\nAsset {asset['asset_id']} is already retired.")
        return

    if asset.get("status") == "In Use":
        print("\nThis asset is currently assigned to a user.")
        print("Return the asset before retiring it.")
        return

    print(f"\nAsset: {asset['asset_id']}")
    print(f"Device: {asset.get('brand', '')} {asset.get('model', '')}")
    print(f"Serial Number: {asset.get('serial_number', '')}")
    print(f"Current Status: {asset.get('status', 'Available')}")

    confirm = input("Retire this asset? (yes/no): ").strip().lower()

    if confirm not in ["yes", "y"]:
        print("\nRetirement cancelled.")
        return

    timestamp = current_timestamp()

    asset["status"] = "Retired"
    asset["assigned_user"] = "Unassigned"
    asset["department"] = "Unassigned"
    asset["retired_at"] = timestamp
    asset["updated_at"] = timestamp

    save_assets()

    print(f"\nAsset {asset['asset_id']} retired successfully.")


assets = load_assets()


def main():
    while True:
        print("\n================================")
        print("        IT ASSET MANAGER")
        print("================================")
        print("1. Add Asset")
        print("2. View Assets")
        print("3. Search Assets")
        print("4. Assign Asset to User")
        print("5. Return Asset")
        print("6. Update Asset")
        print("7. Retire Asset")
        print("8. Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            add_asset()

        elif choice == "2":
            view_assets()

        elif choice == "3":
            search_assets()

        elif choice == "4":
            assign_asset()

        elif choice == "5":
            return_asset()

        elif choice == "6":
            update_asset()

        elif choice == "7":
            retire_asset()

        elif choice == "8":
            print("\nExiting IT Asset Manager...")
            break

        else:
            print("\nInvalid option. Please select 1-8.")


if __name__ == "__main__":
    main()
