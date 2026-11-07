from datetime import date, timedelta

import pytest


def test_valid_date_accepts_iso_and_empty(app):
    assert app.valid_date("2026-03-15") is True
    assert app.valid_date("") is True


@pytest.mark.parametrize("bad", ["15-03-2026", "2026/03/15", "2026-13-01", "hello"])
def test_valid_date_rejects_bad_formats(app, bad):
    assert app.valid_date(bad) is False


def test_parse_date_returns_none_for_garbage(app):
    assert app.parse_date("2026-03-15") == date(2026, 3, 15)
    assert app.parse_date("nope") is None
    assert app.parse_date(None) is None


def test_asset_age_unknown_for_bad_date(app):
    assert app.calculate_asset_age("Unknown") == "Unknown"


def test_asset_age_rejects_future_purchase(app):
    future = (date.today() + timedelta(days=10)).isoformat()

    assert app.calculate_asset_age(future) == "Invalid purchase date"


def test_asset_age_today_is_zero_months(app):
    assert app.calculate_asset_age(date.today().isoformat()) == "0 month(s)"


def test_asset_age_formats_years_and_months(app):
    today = date.today()
    purchase = date(today.year - 2, today.month, 1)
    age = app.calculate_asset_age(purchase.isoformat())

    assert age.startswith("2 year(s)")


def test_warranty_status_variants(app):
    today = date.today()

    assert app.warranty_status("Unknown") == "Unknown"
    assert app.warranty_status((today - timedelta(days=1)).isoformat()) == "Expired"
    assert app.warranty_status(today.isoformat()) == "Expires Today"
    assert app.warranty_status((today + timedelta(days=30)).isoformat()) == "Expiring Soon (30 days)"
    assert app.warranty_status((today + timedelta(days=90)).isoformat()) == "Expiring Soon (90 days)"
    assert app.warranty_status((today + timedelta(days=91)).isoformat()) == "Active"
