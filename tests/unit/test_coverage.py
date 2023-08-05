import decimal
import json
import pathlib

import pytest

from coverage_comment import coverage, subprocess


def test_collapse_lines():
    assert list(
        coverage.collapse_lines([1, 2, 3, 5, 6, 8, 11, 12, 17, 18, 19, 20, 21, 99])
    ) == [(1, 3), (5, 6), (8, 8), (11, 12), (17, 21), (99, 99)]


@pytest.mark.parametrize(
    "num_covered, num_total, expected_coverage",
    [
        (0, 10, "0"),
        (0, 0, "1"),
        (5, 0, "1"),
        (5, 10, "0.5"),
        (1, 100, "0.01"),
    ],
)
def test_compute_coverage(num_covered, num_total, expected_coverage):
    assert coverage.compute_coverage(num_covered, num_total) == decimal.Decimal(
        expected_coverage
    )


def test_get_coverage_info(mocker, coverage_json, coverage_obj):
    run = mocker.patch(
        "coverage_comment.subprocess.run", return_value=json.dumps(coverage_json)
    )

    result = coverage.get_coverage_info(merge=True, coverage_path=pathlib.Path("."))

    assert run.call_args_list == [
        mocker.call("coverage", "combine", path=pathlib.Path(".")),
        mocker.call("coverage", "json", "-o", "-", path=pathlib.Path(".")),
    ]

    assert result == coverage_obj


def test_get_coverage_info__no_merge(mocker, coverage_json):
    run = mocker.patch(
        "coverage_comment.subprocess.run", return_value=json.dumps(coverage_json)
    )

    coverage.get_coverage_info(merge=False, coverage_path=pathlib.Path("."))

    assert (
        mocker.call("coverage", "combine", path=pathlib.Path("."))
        not in run.call_args_list
    )


def test_get_coverage_info__error_base(mocker, get_logs):
    mocker.patch(
        "coverage_comment.subprocess.run", side_effect=subprocess.SubProcessError
    )

    with pytest.raises(subprocess.SubProcessError):
        coverage.get_coverage_info(merge=False, coverage_path=pathlib.Path("."))

    assert not get_logs("ERROR")


def test_get_coverage_info__error_no_source(mocker, get_logs):
    mocker.patch(
        "coverage_comment.subprocess.run",
        side_effect=subprocess.SubProcessError("No source for code: bla"),
    )

    with pytest.raises(subprocess.SubProcessError):
        coverage.get_coverage_info(merge=False, coverage_path=pathlib.Path("."))

    assert get_logs("ERROR", "Cannot read")


def test_generate_coverage_html_files(mocker):
    run = mocker.patch(
        "coverage_comment.subprocess.run",
    )

    coverage.generate_coverage_html_files(
        destination=pathlib.Path("/tmp/foo"), coverage_path=pathlib.Path(".")
    )

    assert run.call_args_list == [
        mocker.call(
            "coverage",
            "html",
            "--skip-empty",
            "--directory",
            "/tmp/foo",
            path=pathlib.Path("."),
        ),
    ]


def test_generate_coverage_markdown(mocker):
    run = mocker.patch("coverage_comment.subprocess.run", return_value="foo")

    result = coverage.generate_coverage_markdown(coverage_path=pathlib.Path("."))

    assert run.call_args_list == [
        mocker.call(
            "coverage",
            "report",
            "--format=markdown",
            "--show-missing",
            path=pathlib.Path("."),
        ),
    ]

    assert result == "foo"
