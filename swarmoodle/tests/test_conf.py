"""Test swarmoodle configuration."""

import pytest
from pydantic import ValidationError

from swarmoodle.conf import Settings, get_settings


def test_conf_settings_settings():
    """Test the `settings` function."""
    # pylint: disable=too-many-function-args
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert get_settings.cache_info().currsize == 1
    assert get_settings.cache_info().maxsize == 1
    get_settings()
    assert get_settings.cache_info().hits == 1


def test_conf_settings_moodle_ws_url(monkeypatch):
    """Test the `Settings.moodle_ws_url` computed property."""

    monkeypatch.setenv("locust_host", "http://foo")
    settings = Settings()
    assert str(settings.moodle_ws_url) == "http://foo/webservice/rest/server.php"


def test_conf_settings_moodle_students(monkeypatch):
    """Test the `Settings.moodle_students` property."""
    # Given no environment variables, `moodle_students` should default to 1.
    monkeypatch.delenv("SWARMOODLE_MOODLE_STUDENTS", raising=False)
    monkeypatch.delenv("LOCUST_USERS", raising=False)
    settings = Settings()
    assert settings.moodle_students == 1

    # Given an invalid environment variable,
    # instantiating `Settings` should raise a `ValidationError`.`
    monkeypatch.setenv("LOCUST_USERS", "-14")
    with pytest.raises(ValidationError, match=r"Input should be greater than 0"):
        settings = Settings()

    # Given the alias environment variable, `moodle_students` should be set.
    monkeypatch.setenv("LOCUST_USERS", "4")
    settings = Settings()
    assert settings.moodle_students == 4

    # Given the SWARMOODLE environment variable, `moodle_students` should be updated.
    monkeypatch.setenv("SWARMOODLE_MOODLE_STUDENTS", "10")
    settings = Settings()
    assert settings.moodle_students == 10


def test_conf_request_milliseconds_duration(monkeypatch):
    """Test the `Settings.request_milliseconds_duration` property."""
    # Given no environment variables,
    # `request_milliseconds_duration` should default to 400.
    monkeypatch.delenv("SWARMOODLE_REQUEST_MILLISECONDS_DURATION", raising=False)
    settings = Settings()
    assert settings.request_milliseconds_duration == 400

    # Given an invalid environment variable,
    # instantiating `Settings` should raise a `ValidationError`.
    monkeypatch.setenv("SWARMOODLE_REQUEST_MILLISECONDS_DURATION", "-1")
    msg = r"Input should be greater than or equal to 0"
    with pytest.raises(ValidationError, match=msg):
        Settings()

    # Given a valid environment variable,
    # `request_milliseconds_duration` should be set.
    monkeypatch.setenv("SWARMOODLE_REQUEST_MILLISECONDS_DURATION", "0")
    settings = Settings()
    assert settings.request_milliseconds_duration == 0


def test_conf_check_oulad_course_module_presentation(monkeypatch):
    """Test the `check_oulad_course_module_presentation` model validator."""
    # Given an invalid combination of `oulad_code_module` and `oulad_code_presentation`,
    # instantiating `Settings` should raise a `ValidationError`.
    monkeypatch.setenv("swarmoodle_oulad_code_module", "AAA")
    monkeypatch.setenv("swarmoodle_oulad_code_presentation", "2014B")
    msg = (
        r"invalid oulad_code_module/oulad_code_presentation combination: "
        r"for code_module: AAA the code_presentation "
        r"should be one of: \['2013J', '2014J'\]"
    )
    with pytest.raises(ValidationError, match=msg):
        Settings()

    # Given a valid combination of `oulad_code_module` and `oulad_code_presentation`,
    # instantiating `Settings` should succeed.
    monkeypatch.setenv("swarmoodle_oulad_code_module", "CCC")
    monkeypatch.setenv("swarmoodle_oulad_code_presentation", "2014B")
    settings = Settings()
    assert settings.oulad_code_module == "CCC"
    assert settings.oulad_code_presentation == "2014B"
