"""
This module should contain only the things relevant to the badge being computed
by shields.io
"""

import decimal
import json
import urllib.parse

import httpx


def get_badge_color(
    rate: decimal.Decimal,
    minimum_green: decimal.Decimal,
    minimum_orange: decimal.Decimal,
) -> str:
    if rate >= minimum_green:
        return "brightgreen"
    elif rate >= minimum_orange:
        return "orange"
    else:
        return "red"


def get_evolution_badge_color(
    rate_before: decimal.Decimal | None,
    rate_after: decimal.Decimal,
) -> str:
    if rate_before is None or rate_after > rate_before:
        return "brightgreen"
    elif rate_after == rate_before:
        return "blue"
    else:
        return "orange"


def compute_badge_endpoint_data(
    line_rate: decimal.Decimal,
    color: str,
) -> str:
    badge = {
        "schemaVersion": 1,
        "label": "Coverage",
        "message": f"{int(line_rate)}%",
        "color": color,
    }

    return json.dumps(badge)


def compute_badge_image(
    line_rate: decimal.Decimal, color: str, http_session: httpx.Client
) -> str:
    return http_session.get(
        "https://img.shields.io/static/v1?"
        + urllib.parse.urlencode(
            {
                "label": "Coverage",
                "message": f"{int(line_rate)}%",
                "color": color,
            }
        )
    ).text


def get_static_badge_url(label: str, message: str, color: str) -> str:
    return "https://img.shields.io/badge/" + urllib.parse.quote(
        f"{label}-{message}-{color}.svg"
    )


def get_endpoint_url(endpoint_url: str) -> str:
    return f"https://img.shields.io/endpoint?url={endpoint_url}"


def get_dynamic_url(endpoint_url: str) -> str:
    return "https://img.shields.io/badge/dynamic/json?" + urllib.parse.urlencode(
        {
            "color": "brightgreen",
            "label": "coverage",
            "query": "$.message",
            "url": endpoint_url,
        }
    )
