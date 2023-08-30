import decimal

import pytest

from coverage_comment import badge


@pytest.mark.parametrize(
    "rate, expected",
    [
        (decimal.Decimal("10"), "red"),
        (decimal.Decimal("80"), "orange"),
        (decimal.Decimal("99"), "brightgreen"),
    ],
)
def test_get_badge_color(rate, expected):
    color = badge.get_badge_color(
        rate=rate,
        minimum_green=decimal.Decimal("90"),
        minimum_orange=decimal.Decimal("60"),
    )
    assert color == expected


@pytest.mark.parametrize(
    "rate1, rate2, expected",
    [
        (decimal.Decimal("70"), decimal.Decimal("80"), "brightgreen"),
        (None, decimal.Decimal("10"), "brightgreen"),
        (decimal.Decimal("85"), decimal.Decimal("85"), "blue"),
        (decimal.Decimal("80"), decimal.Decimal("70"), "orange"),
    ],
)
def test_get_evolution_badge_color(rate1, rate2, expected):
    color = badge.get_evolution_badge_color(
        rate_before=rate1,
        rate_after=rate2,
    )
    assert color == expected


def test_compute_badge_endpoint_data():
    badge_data = badge.compute_badge_endpoint_data(
        line_rate=decimal.Decimal("27.42"), color="red"
    )
    expected = """{"schemaVersion": 1, "label": "Coverage", "message": "27%", "color": "red"}"""
    assert badge_data == expected


def test_compute_badge_image(session):
    session.register(
        "GET", "https://img.shields.io/static/v1?label=Coverage&message=27%25&color=red"
    )(text="foo")

    badge_data = badge.compute_badge_image(
        line_rate=decimal.Decimal("27.42"), color="red", http_session=session
    )

    assert badge_data == "foo"


def test_get_static_badge_url():
    assert (
        badge.get_static_badge_url(label="Label", message="100% > 99%", color="green")
        == "https://img.shields.io/badge/Label-100%25%20%3E%2099%25-green.svg"
    )


def test_get_endpoint_url():
    url = badge.get_endpoint_url(endpoint_url="https://foo")
    expected = "https://img.shields.io/endpoint?url=https://foo"

    assert url == expected


def test_get_dynamic_url():
    url = badge.get_dynamic_url(endpoint_url="https://foo")
    expected = "https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Ffoo"

    assert url == expected
