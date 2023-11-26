"""Test OULAD utilities."""

import logging

import pandas as pd
from pytest import LogCaptureFixture

from swarmoodle.oulad import (
    OULAD,
    filter_by_module_presentation,
    get_oulad,
    map_oulad_to_moodle,
)


def test_oulad_get_oulad():
    """Test the `get_oulad` function."""
    oulad = get_oulad("./tests/OULAD")
    assert isinstance(oulad, OULAD)
    assert isinstance(oulad.assessments, pd.DataFrame)
    assert isinstance(oulad.courses, pd.DataFrame)
    assert isinstance(oulad.domains, pd.DataFrame)
    assert isinstance(oulad.student_assessment, pd.DataFrame)
    assert isinstance(oulad.student_info, pd.DataFrame)
    assert isinstance(oulad.student_registration, pd.DataFrame)
    assert isinstance(oulad.student_vle, pd.DataFrame)
    assert isinstance(oulad.vle, pd.DataFrame)
    assert get_oulad.cache_info().currsize == 1
    assert get_oulad.cache_info().maxsize == 1
    get_oulad("./tests/OULAD")
    assert get_oulad.cache_info().hits == 1


def test_oulad_filter_by_module_presentation():
    """Test the `filter_by_module_presentation` function."""
    oulad = get_oulad("./tests/OULAD")
    # With drop = False
    courses = filter_by_module_presentation(oulad.courses, "AAA", "2013J", drop=False)
    columns = ["code_module", "code_presentation", "module_presentation_length"]
    assert courses.columns.to_list() == columns
    assert courses.values.tolist() == [["AAA", "2013J", 268]]
    # With drop = True
    courses = filter_by_module_presentation(oulad.courses, "AAA", "2013J")
    assert courses.columns.to_list() == ["module_presentation_length"]
    assert courses.values.tolist() == [[268]]


def test_oulad_map_oulad_to_moodle(caplog: LogCaptureFixture):
    """Test the `map_oulad_to_moodle` function."""
    activity_types = [
        "oucontent",
        "externalquiz",
        "page",
        "sharedsubpage",
        "url",
        "oucontent",
    ]
    vle = pd.DataFrame(
        activity_types,
        columns=["activity_type"],
        index=["o0", "o1", "o2", "o3", "o4", "o5"],
    )
    moodle_course = [
        {"id": "m0", "modname": "homepage"},
        {"id": "m1", "modname": "scorm"},
        {"id": "m2", "modname": "page"},
        {"id": "m3", "modname": "book"},
        {"id": "m4", "modname": "scorm"},
        {"id": "m5", "modname": "scorm"},
        {"id": "m6", "modname": "book"},
    ]
    with caplog.at_level(logging.INFO):
        assert map_oulad_to_moodle(vle, moodle_course) == {
            "o0": 3,
            "o1": 4,
            "o2": 2,
            "o3": 1,
            "o5": 6,
        }

    assert (
        "swarmoodle.oulad",
        logging.INFO,
        "Mapped 5 (71.43%) out of 7 Moodle modules from 6 (83.33%) OULAD activities",
    ) in caplog.record_tuples
