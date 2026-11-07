import json


def test_first_asset_id(app):
    assert app.generate_asset_id() == "IT-0001"


def test_next_asset_id_uses_highest_number(app):
    app.assets = [{"asset_id": "IT-0001"}, {"asset_id": "IT-0007"}, {"asset_id": "IT-0003"}]

    assert app.generate_asset_id() == "IT-0008"


def test_asset_id_ignores_malformed_ids(app):
    app.assets = [{"asset_id": "IT-abc"}, {"asset_id": "OTHER-9"}, {"asset_id": "IT-0002"}]

    assert app.generate_asset_id() == "IT-0003"


def test_asset_id_with_only_malformed_ids_restarts(app):
    app.assets = [{"asset_id": "garbage"}]

    assert app.generate_asset_id() == "IT-0001"


def test_find_asset_is_case_and_space_insensitive(app):
    asset = {"asset_id": "IT-0002"}
    app.assets = [asset]

    assert app.find_asset(" it-0002 ") is asset
    assert app.find_asset("IT-9999") is None


def test_serial_exists_detects_duplicates_case_insensitively(app):
    app.assets = [{"serial_number": "HP92831"}]

    assert app.serial_exists("hp92831") is True
    assert app.serial_exists("DELL111") is False


def test_serial_exists_ignores_the_asset_being_edited(app):
    asset = {"serial_number": "HP92831"}
    app.assets = [asset]

    assert app.serial_exists("HP92831", current_asset=asset) is False


def test_add_history_appends_entries(app):
    asset = {}

    app.add_history(asset, "Added")
    app.add_history(asset, "Assigned")

    assert [e["action"] for e in asset["history"]] == ["Added", "Assigned"]


def test_load_returns_empty_when_missing_or_corrupt(app):
    assert app.load_assets() == []

    with open(app.ASSETS_FILE, "w", encoding="utf-8") as f:
        f.write("{ broken")

    assert app.load_assets() == []


def test_load_returns_empty_when_json_is_not_a_list(app):
    with open(app.ASSETS_FILE, "w", encoding="utf-8") as f:
        json.dump({"asset_id": "IT-0001"}, f)

    assert app.load_assets() == []


def test_load_fills_defaults_for_old_records(app):
    with open(app.ASSETS_FILE, "w", encoding="utf-8") as f:
        json.dump([{"asset_id": "IT-0001", "serial_number": "X1"}], f)

    asset = app.load_assets()[0]

    assert asset["status"] == "Available"
    assert asset["assigned_user"] == "Unassigned"
    assert asset["department"] == "Unassigned"
    assert asset["history"] == []
    assert asset["warranty_expiry"] == "Unknown"


def test_save_then_load_round_trip(app):
    app.assets = [{
        "asset_id": "IT-0001",
        "serial_number": "X1",
        "assigned_user": "فراس",
    }]

    app.save_assets()
    loaded = app.load_assets()

    assert loaded[0]["assigned_user"] == "فراس"
    assert loaded[0]["asset_id"] == "IT-0001"
