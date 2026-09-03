import csv
import json
import os
from datetime import datetime, date


ASSETS_FILE = "assets.json"


def current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def valid_date(date_string):
    if not date_string:
        return True

    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def parse_date(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def calculate_asset_age(purchase_date):
    purchase = parse_date(purchase_date)

    if purchase is None:
        return "Unknown"

    today = date.today()

    if purchase > today:
        return "Invalid purchase date"

    months = (today.year - purchase.year) * 12 + (today.month - purchase.month)

    if today.day < purchase.day:
        months -= 1

    years = months // 12
    remaining_months = months % 12

    if years > 0 and remaining_months > 0:
        return f"{years} year(s), {remaining_months} month(s)"

    if years > 0:
        return f"{years} year(s)"

    return f"{remaining_months} month(s)"


def warranty_status(warranty_expiry):
    expiry = parse_date(warranty_expiry)

    if expiry is None:
        return "Unknown"

    today = date.today()
    days_remaining = (expiry - today).days

    if days_remaining < 0:
        return "Expired"

    if days_remaining == 0:
        return "Expires Today"

    if days_remaining <= 90:
        return f"Expiring Soon ({days_remaining} days)"

    return "Active"


def add_history(asset, action):
    asset.setdefault("history", [])

    asset["history"].append({
        "timestamp": current_timestamp(),
        "action": action
    })


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
            asset.setdefault("purchase_date", "Unknown")
            asset.setdefault("warranty_expiry", "Unknown")
            asset.setdefault("history", [])

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


def display_asset(asset):
    purchase_date = asset.get("purchase_date", "Unknown")
    warranty_expiry = asset.get("warranty_expiry", "Unknown")

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
    print(f"Purchase Date: {purchase_date}")
    print(f"Asset Age: {calculate_asset_age(purchase_date)}")
    print(f"Warranty Expiry: {warranty_expiry}")
    print(f"Warranty Status: {warranty_status(warranty_expiry)}")
    print(f"Added: {asset.get('created_at', 'Unknown')}")

    if asset.get("assigned_at"):
        print(f"Assigned At: {asset['assigned_at']}")

    if asset.get("returned_at"):
        print(f"Last Returned: {asset['returned_at']}")

    if asset.get("retired_at"):
        print(f"Retired At: {asset['retired_at']}")

    print(f"Last Updated: {asset.get('updated_at', 'Unknown')}")


def add_asset():
    print("\n================================")
    print("           ADD ASSET")
    print("================================")

    asset_type = input("Asset Type: ").strip()
    brand = input("Brand: ").strip()
    model = input("Model: ").strip()
    serial_number = input("Serial Number: ").strip()
    location = input("Location: ").strip()
    purchase_date = input("Purchase Date (YYYY-MM-DD): ").strip()
    warranty_expiry = input("Warranty Expiry (YYYY-MM-DD): ").strip()

    if not asset_type:
        print("\nAsset type cannot be empty.")
        return

    if not serial_number:
        print("\nSerial number cannot be empty.")
        return

    if serial_exists(serial_number):
        print("\nAn asset with this serial number already exists.")
        return

    if purchase_date and not valid_date(purchase_date):
        print("\nInvalid purchase date. Use YYYY-MM-DD.")
        return

    if warranty_expiry and not valid_date(warranty_expiry):
        print("\nInvalid warranty expiry date. Use YYYY-MM-DD.")
        return

    if purchase_date and warranty_expiry:
        purchase = parse_date(purchase_date)
        warranty = parse_date(warranty_expiry)

        if warranty < purchase:
            print("\nWarranty expiry cannot be before the purchase date.")
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
        "location": location if location else "Unknown",
        "purchase_date": purchase_date if purchase_date else "Unknown",
        "warranty_expiry": warranty_expiry if warranty_expiry else "Unknown",
        "created_at": timestamp,
        "updated_at": timestamp,
        "assigned_at": "",
        "returned_at": "",
        "retired_at": "",
        "history": []
    }

    add_history(asset, "Asset added to inventory")

    assets.append(asset)
    save_assets()

    print(f"\nAsset {asset['asset_id']} added successfully.")


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
        "Enter Asset ID, serial number, brand, model, user, department, location, or type: "
    ).strip().lower()

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

    add_history(asset, f"Assigned to {user} - {department}")

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

    if asset.get("status") == "Retired":
        print("\nA retired asset cannot be returned.")
        return

    if asset.get("assigned_user", "Unassigned") == "Unassigned":
        print(f"\nAsset {asset['asset_id']} is not currently assigned.")
        return

    previous_user = asset.get("assigned_user", "Unknown")
    previous_department = asset.get("department", "Unknown")

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

    add_history(asset, f"Returned from {previous_user} - {previous_department}")

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
    new_purchase_date = input(f"Purchase Date [{asset.get('purchase_date', 'Unknown')}]: ").strip()
    new_warranty_expiry = input(f"Warranty Expiry [{asset.get('warranty_expiry', 'Unknown')}]: ").strip()

    if new_serial and serial_exists(new_serial, asset):
        print("\nAnother asset already uses this serial number.")
        return

    if new_purchase_date and not valid_date(new_purchase_date):
        print("\nInvalid purchase date. Use YYYY-MM-DD.")
        return

    if new_warranty_expiry and not valid_date(new_warranty_expiry):
        print("\nInvalid warranty expiry date. Use YYYY-MM-DD.")
        return

    final_purchase_date = new_purchase_date if new_purchase_date else asset.get("purchase_date", "Unknown")
    final_warranty_expiry = new_warranty_expiry if new_warranty_expiry else asset.get("warranty_expiry", "Unknown")

    purchase = parse_date(final_purchase_date)
    warranty = parse_date(final_warranty_expiry)

    if purchase and warranty and warranty < purchase:
        print("\nWarranty expiry cannot be before the purchase date.")
        return

    changes = []

    if new_type and new_type != asset.get("type"):
        old_value = asset.get("type", "Unknown")
        asset["type"] = new_type
        changes.append(f"Type changed from {old_value} to {new_type}")

    if new_brand and new_brand != asset.get("brand"):
        old_value = asset.get("brand", "Unknown")
        asset["brand"] = new_brand
        changes.append(f"Brand changed from {old_value} to {new_brand}")

    if new_model and new_model != asset.get("model"):
        old_value = asset.get("model", "Unknown")
        asset["model"] = new_model
        changes.append(f"Model changed from {old_value} to {new_model}")

    if new_serial and new_serial != asset.get("serial_number"):
        old_value = asset.get("serial_number", "Unknown")
        asset["serial_number"] = new_serial
        changes.append(f"Serial number changed from {old_value} to {new_serial}")

    if new_location and new_location != asset.get("location"):
        old_value = asset.get("location", "Unknown")
        asset["location"] = new_location
        changes.append(f"Location changed from {old_value} to {new_location}")

    if new_purchase_date and new_purchase_date != asset.get("purchase_date"):
        old_value = asset.get("purchase_date", "Unknown")
        asset["purchase_date"] = new_purchase_date
        changes.append(f"Purchase date changed from {old_value} to {new_purchase_date}")

    if new_warranty_expiry and new_warranty_expiry != asset.get("warranty_expiry"):
        old_value = asset.get("warranty_expiry", "Unknown")
        asset["warranty_expiry"] = new_warranty_expiry
        changes.append(f"Warranty expiry changed from {old_value} to {new_warranty_expiry}")

    if not changes:
        print("\nNo changes were made.")
        return

    asset["updated_at"] = current_timestamp()

    for change in changes:
        add_history(asset, change)

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

    reason = input("Retirement reason: ").strip()

    if not reason:
        reason = "No reason provided"

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

    add_history(asset, f"Asset retired - Reason: {reason}")

    save_assets()

    print(f"\nAsset {asset['asset_id']} retired successfully.")


def filter_assets():
    print("\n================================")
    print("          FILTER ASSETS")
    print("================================")

    if not assets:
        print("\nNo assets available.")
        return

    print("\nFilter by:")
    print("1. Status")
    print("2. Asset Type")
    print("3. Department")
    print("4. Location")

    choice = input("\nSelect filter: ").strip()
    results = []

    if choice == "1":
        print("\nStatus:")
        print("1. Available")
        print("2. In Use")
        print("3. Retired")

        status_choice = input("Select status: ").strip()

        status_options = {
            "1": "Available",
            "2": "In Use",
            "3": "Retired"
        }

        selected_status = status_options.get(status_choice)

        if selected_status is None:
            print("\nInvalid status.")
            return

        results = [asset for asset in assets if asset.get("status") == selected_status]

    elif choice == "2":
        asset_type = input("Enter Asset Type: ").strip().lower()

        if not asset_type:
            print("\nAsset type cannot be empty.")
            return

        results = [asset for asset in assets if asset_type in asset.get("type", "").lower()]

    elif choice == "3":
        department = input("Enter Department: ").strip().lower()

        if not department:
            print("\nDepartment cannot be empty.")
            return

        results = [asset for asset in assets if department in asset.get("department", "").lower()]

    elif choice == "4":
        location = input("Enter Location: ").strip().lower()

        if not location:
            print("\nLocation cannot be empty.")
            return

        results = [asset for asset in assets if location in asset.get("location", "").lower()]

    else:
        print("\nInvalid filter option.")
        return

    if not results:
        print("\nNo assets match this filter.")
        return

    print(f"\nFound {len(results)} matching asset(s):")

    for asset in results:
        display_asset(asset)


def asset_statistics():
    print("\n================================")
    print("        ASSET STATISTICS")
    print("================================")

    if not assets:
        print("\nNo assets available.")
        return

    total_assets = len(assets)

    available_count = 0
    in_use_count = 0
    retired_count = 0
    assigned_count = 0
    unassigned_count = 0

    active_warranty_count = 0
    expiring_warranty_count = 0
    expired_warranty_count = 0
    unknown_warranty_count = 0

    type_counts = {}
    department_counts = {}
    location_counts = {}

    for asset in assets:
        status = asset.get("status", "Available")
        asset_type = asset.get("type", "Unknown")
        department = asset.get("department", "Unassigned")
        location = asset.get("location", "Unknown")

        if status == "Available":
            available_count += 1
        elif status == "In Use":
            in_use_count += 1
        elif status == "Retired":
            retired_count += 1

        if asset.get("assigned_user", "Unassigned") == "Unassigned":
            unassigned_count += 1
        else:
            assigned_count += 1

        warranty = warranty_status(asset.get("warranty_expiry", "Unknown"))

        if warranty == "Active":
            active_warranty_count += 1
        elif warranty.startswith("Expiring Soon") or warranty == "Expires Today":
            expiring_warranty_count += 1
        elif warranty == "Expired":
            expired_warranty_count += 1
        else:
            unknown_warranty_count += 1

        type_counts[asset_type] = type_counts.get(asset_type, 0) + 1
        location_counts[location] = location_counts.get(location, 0) + 1

        if department != "Unassigned":
            department_counts[department] = department_counts.get(department, 0) + 1

    print(f"\nTotal Assets: {total_assets}")

    print("\nStatus:")
    print(f"Available: {available_count}")
    print(f"In Use: {in_use_count}")
    print(f"Retired: {retired_count}")

    print("\nAssignment:")
    print(f"Assigned Assets: {assigned_count}")
    print(f"Unassigned Assets: {unassigned_count}")

    print("\nWarranty:")
    print(f"Active: {active_warranty_count}")
    print(f"Expiring Soon: {expiring_warranty_count}")
    print(f"Expired: {expired_warranty_count}")
    print(f"Unknown: {unknown_warranty_count}")

    print("\nAsset Types:")

    for asset_type, count in sorted(type_counts.items()):
        print(f"{asset_type}: {count}")

    print("\nLocations:")

    for location, count in sorted(location_counts.items()):
        print(f"{location}: {count}")

    if department_counts:
        print("\nDepartments:")

        for department, count in sorted(department_counts.items()):
            print(f"{department}: {count}")

    active_assets = available_count + in_use_count
    active_percentage = (active_assets / total_assets) * 100
    utilization_rate = (in_use_count / total_assets) * 100

    print(f"\nActive Asset Rate: {active_percentage:.1f}%")
    print(f"Asset Utilization Rate: {utilization_rate:.1f}%")


def view_asset_history():
    print("\n================================")
    print("          ASSET HISTORY")
    print("================================")

    if not assets:
        print("\nNo assets available.")
        return

    asset_id = input("Enter Asset ID: ").strip()
    asset = find_asset(asset_id)

    if asset is None:
        print("\nAsset not found.")
        return

    print(f"\nAsset ID: {asset['asset_id']}")
    print(f"Device: {asset.get('brand', '')} {asset.get('model', '')}")
    print(f"Serial Number: {asset.get('serial_number', '')}")
    print(f"Current Status: {asset.get('status', 'Unknown')}")

    history = asset.get("history", [])

    if not history:
        print("\nNo activity history available for this asset.")
        return

    print("\nActivity History:")

    for entry in history:
        timestamp = entry.get("timestamp", "Unknown")
        action = entry.get("action", "Unknown activity")
        print(f"[{timestamp}] {action}")


def warranty_alerts():
    print("\n================================")
    print("         WARRANTY ALERTS")
    print("================================")

    if not assets:
        print("\nNo assets available.")
        return

    expired_assets = []
    expiring_assets = []

    today = date.today()

    for asset in assets:
        if asset.get("status") == "Retired":
            continue

        expiry = parse_date(asset.get("warranty_expiry"))

        if expiry is None:
            continue

        days_remaining = (expiry - today).days

        if days_remaining < 0:
            expired_assets.append((asset, days_remaining))
        elif days_remaining <= 90:
            expiring_assets.append((asset, days_remaining))

    expired_assets.sort(key=lambda item: item[1])
    expiring_assets.sort(key=lambda item: item[1])

    if not expired_assets and not expiring_assets:
        print("\nNo warranty alerts.")
        return

    if expired_assets:
        print("\nExpired Warranties:")

        for asset, days_remaining in expired_assets:
            print("\n--------------------------------")
            print(f"Asset ID: {asset['asset_id']}")
            print(f"Device: {asset.get('brand', '')} {asset.get('model', '')}")
            print(f"Warranty Expiry: {asset.get('warranty_expiry')}")
            print(f"Expired {abs(days_remaining)} day(s) ago")

    if expiring_assets:
        print("\nExpiring Within 90 Days:")

        for asset, days_remaining in expiring_assets:
            print("\n--------------------------------")
            print(f"Asset ID: {asset['asset_id']}")
            print(f"Device: {asset.get('brand', '')} {asset.get('model', '')}")
            print(f"Warranty Expiry: {asset.get('warranty_expiry')}")

            if days_remaining == 0:
                print("Warranty expires today")
            else:
                print(f"Days Remaining: {days_remaining}")


def export_asset_report():
    print("\n================================")
    print("       EXPORT ASSET REPORT")
    print("================================")

    if not assets:
        print("\nNo assets available.")
        return

    asset_id = input("Enter Asset ID: ").strip()
    asset = find_asset(asset_id)

    if asset is None:
        print("\nAsset not found.")
        return

    filename = f"{asset['asset_id'].lower()}_report.txt"

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write("IT ASSET REPORT\n")
            file.write("================================\n\n")

            file.write(f"Asset ID: {asset.get('asset_id', 'Unknown')}\n")
            file.write(f"Type: {asset.get('type', 'Unknown')}\n")
            file.write(f"Brand: {asset.get('brand', 'Unknown')}\n")
            file.write(f"Model: {asset.get('model', 'Unknown')}\n")
            file.write(f"Serial Number: {asset.get('serial_number', 'Unknown')}\n")
            file.write(f"Status: {asset.get('status', 'Unknown')}\n")
            file.write(f"Assigned User: {asset.get('assigned_user', 'Unassigned')}\n")
            file.write(f"Department: {asset.get('department', 'Unassigned')}\n")
            file.write(f"Location: {asset.get('location', 'Unknown')}\n")

            purchase_date = asset.get("purchase_date", "Unknown")
            warranty_expiry = asset.get("warranty_expiry", "Unknown")

            file.write(f"Purchase Date: {purchase_date}\n")
            file.write(f"Asset Age: {calculate_asset_age(purchase_date)}\n")
            file.write(f"Warranty Expiry: {warranty_expiry}\n")
            file.write(f"Warranty Status: {warranty_status(warranty_expiry)}\n")

            file.write(f"Created: {asset.get('created_at', 'Unknown')}\n")
            file.write(f"Last Updated: {asset.get('updated_at', 'Unknown')}\n")

            if asset.get("assigned_at"):
                file.write(f"Assigned At: {asset['assigned_at']}\n")

            if asset.get("returned_at"):
                file.write(f"Last Returned: {asset['returned_at']}\n")

            if asset.get("retired_at"):
                file.write(f"Retired At: {asset['retired_at']}\n")

            file.write("\nACTIVITY HISTORY\n")
            file.write("================================\n")

            history = asset.get("history", [])

            if history:
                for entry in history:
                    timestamp = entry.get("timestamp", "Unknown")
                    action = entry.get("action", "Unknown activity")
                    file.write(f"[{timestamp}] {action}\n")
            else:
                file.write("No activity history available.\n")

            file.write("\n================================\n")
            file.write(f"Report Generated: {current_timestamp()}\n")
            file.write("Generated by IT Asset Inventory Manager\n")

        print(f"\nTXT report created successfully: {filename}")

    except OSError as error:
        print(f"\nUnable to create report: {error}")


def export_inventory_csv():
    print("\n================================")
    print("       EXPORT INVENTORY CSV")
    print("================================")

    if not assets:
        print("\nNo assets available.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"asset_inventory_{timestamp}.csv"

    fieldnames = [
        "Asset ID",
        "Type",
        "Brand",
        "Model",
        "Serial Number",
        "Status",
        "Assigned User",
        "Department",
        "Location",
        "Purchase Date",
        "Asset Age",
        "Warranty Expiry",
        "Warranty Status",
        "Created",
        "Last Updated",
        "Assigned At",
        "Last Returned",
        "Retired At",
        "History Entries"
    ]

    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for asset in assets:
                purchase_date = asset.get("purchase_date", "Unknown")
                warranty_expiry = asset.get("warranty_expiry", "Unknown")

                writer.writerow({
                    "Asset ID": asset.get("asset_id", "Unknown"),
                    "Type": asset.get("type", "Unknown"),
                    "Brand": asset.get("brand", "Unknown"),
                    "Model": asset.get("model", "Unknown"),
                    "Serial Number": asset.get("serial_number", "Unknown"),
                    "Status": asset.get("status", "Unknown"),
                    "Assigned User": asset.get("assigned_user", "Unassigned"),
                    "Department": asset.get("department", "Unassigned"),
                    "Location": asset.get("location", "Unknown"),
                    "Purchase Date": purchase_date,
                    "Asset Age": calculate_asset_age(purchase_date),
                    "Warranty Expiry": warranty_expiry,
                    "Warranty Status": warranty_status(warranty_expiry),
                    "Created": asset.get("created_at", "Unknown"),
                    "Last Updated": asset.get("updated_at", "Unknown"),
                    "Assigned At": asset.get("assigned_at", ""),
                    "Last Returned": asset.get("returned_at", ""),
                    "Retired At": asset.get("retired_at", ""),
                    "History Entries": len(asset.get("history", []))
                })

        print(f"\nCSV export created successfully: {filename}")

    except OSError as error:
        print(f"\nUnable to create CSV export: {error}")


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
        print("8. Filter Assets")
        print("9. Asset Statistics")
        print("10. View Asset History")
        print("11. Warranty Alerts")
        print("12. Export Asset Report (TXT)")
        print("13. Export Inventory (CSV)")
        print("14. Exit")

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
            filter_assets()

        elif choice == "9":
            asset_statistics()

        elif choice == "10":
            view_asset_history()

        elif choice == "11":
            warranty_alerts()

        elif choice == "12":
            export_asset_report()

        elif choice == "13":
            export_inventory_csv()

        elif choice == "14":
            print("\nExiting IT Asset Manager...")
            break

        else:
            print("\nInvalid option. Please select 1-14.")


if __name__ == "__main__":
    main()
