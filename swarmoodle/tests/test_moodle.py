"""Test Moodle utilities."""

from urllib.parse import urlencode

import pandas as pd
from faker import Faker
from pytest import MonkeyPatch
from pytest_httpx import HTTPXMock

from swarmoodle.conf import Settings
from swarmoodle.moodle import (
    MoodleUser,
    create_moodle_users,
    delete_moodle_users,
    enroll_moodle_users,
    get_moodle_course,
    get_moodle_users_by_usernames,
)

Faker.seed(0)


def test_moodle_get_moodle_course(httpx_mock: HTTPXMock, monkeypatch: MonkeyPatch):
    """Test the `get_moodle_course` function."""
    # NB: pydantic-settings with aliases are not overwritten (see issue #178).
    monkeypatch.setenv("SWARMOODLE_MOODLE_URL", "http://moodle/")
    response = [{"id": 1}, {"id": 2}]
    url = "http://hook/courses/10?html=0"
    httpx_mock.add_response(method="GET", url=url, json=response)
    settings = Settings(hook_url="http://hook/", moodle_course_id=10)
    assert get_moodle_course(settings) == [
        {
            "id": 0,
            "instance": 0,
            "name": "Home page",
            "modname": "homepage",
            "url": "http://moodle/",
            "contents": None,
        },
        {"id": 1},
        {"id": 2},
    ]


def test_moodle_create_moodle_users(httpx_mock: HTTPXMock, monkeypatch: MonkeyPatch):
    """Test the `create_moodle_users` function."""
    # NB: pydantic-settings with aliases are not overwritten (see issue #178).
    monkeypatch.setenv("SWARMOODLE_MOODLE_URL", "http://moodle/")
    monkeypatch.setenv("SWARMOODLE_MOODLE_STUDENTS", "2")
    response = [{"id": 1, "username": "11391"}, {"id": 2, "username": "28400"}]
    data = {
        "wstoken": "token",
        "moodlewsrestformat": "json",
        "wsfunction": "core_user_create_users",
        "users[0][createpassword]": "0",
        "users[0][username]": "11391",
        "users[0][password]": "Passwd1!",
        "users[0][firstname]": "Ryan",
        "users[0][lastname]": "Chang",
        "users[0][email]": "11391@gmail.com",
        "users[0][country]": "GB",
        "users[0][timezone]": "Europe/London",
        "users[0][institution]": "Open Univesity",
        "users[0][customfields][0][type]": "gender",
        "users[0][customfields][0][value]": "M",
        "users[0][customfields][1][type]": "region",
        "users[0][customfields][1][value]": "East Anglian Region",
        "users[0][customfields][2][type]": "highest_education",
        "users[0][customfields][2][value]": "HE Qualification",
        "users[0][customfields][3][type]": "imd_band",
        "users[0][customfields][3][value]": "90-100%",
        "users[0][customfields][4][type]": "age_band",
        "users[0][customfields][4][value]": "55<=",
        "users[0][customfields][5][type]": "num_of_prev_attempts",
        "users[0][customfields][5][value]": "0",
        "users[0][customfields][6][type]": "studied_credits",
        "users[0][customfields][6][value]": "240",
        "users[0][customfields][7][type]": "disability",
        "users[0][customfields][7][value]": "N",
        "users[0][customfields][8][type]": "final_result",
        "users[0][customfields][8][value]": "Pass",
        "users[1][createpassword]": "0",
        "users[1][username]": "28400",
        "users[1][password]": "Passwd1!",
        "users[1][firstname]": "Jennifer",
        "users[1][lastname]": "Green",
        "users[1][email]": "28400@gmail.com",
        "users[1][country]": "GB",
        "users[1][timezone]": "Europe/London",
        "users[1][institution]": "Open Univesity",
        "users[1][customfields][0][type]": "gender",
        "users[1][customfields][0][value]": "F",
        "users[1][customfields][1][type]": "region",
        "users[1][customfields][1][value]": "Scotland",
        "users[1][customfields][2][type]": "highest_education",
        "users[1][customfields][2][value]": "HE Qualification",
        "users[1][customfields][3][type]": "imd_band",
        "users[1][customfields][3][value]": "20-30%",
        "users[1][customfields][4][type]": "age_band",
        "users[1][customfields][4][value]": "35-55",
        "users[1][customfields][5][type]": "num_of_prev_attempts",
        "users[1][customfields][5][value]": "1",
        "users[1][customfields][6][type]": "studied_credits",
        "users[1][customfields][6][value]": "60",
        "users[1][customfields][7][type]": "disability",
        "users[1][customfields][7][value]": "Y",
        "users[1][customfields][8][type]": "final_result",
        "users[1][customfields][8][value]": "Fail",
    }
    data = urlencode(data, doseq=True).encode("utf8")
    url = "http://moodle/webservice/rest/server.php"
    httpx_mock.add_response(method="POST", url=url, match_content=data, json=response)
    settings = Settings(moodle_webservices_token="token")
    data = {
        "gender": ["M", "F"],
        "region": ["East Anglian Region", "Scotland"],
        "highest_education": ["HE Qualification", "HE Qualification"],
        "imd_band": ["90-100%", "20-30%"],
        "age_band": ["55<=", "35-55"],
        "num_of_prev_attempts": [0, 1],
        "studied_credits": [240, 60],
        "disability": ["N", "Y"],
        "final_result": ["Pass", "Fail"],
    }
    students = pd.DataFrame(data=data, index=[11391, 28400])
    assert create_moodle_users(settings, students) == [
        MoodleUser(id=1, username="11391"),
        MoodleUser(id=2, username="28400"),
    ]


def test_moodle_delete_moodle_users(httpx_mock: HTTPXMock, monkeypatch: MonkeyPatch):
    """Test the `delete_moodle_users` function."""
    monkeypatch.setenv("SWARMOODLE_MOODLE_URL", "http://moodle/")
    data = {
        "wstoken": "token",
        "moodlewsrestformat": "json",
        "wsfunction": "core_user_delete_users",
        "userids[0]": "1",
        "userids[1]": "2",
    }
    data = urlencode(data, doseq=True).encode("utf8")
    url = "http://moodle/webservice/rest/server.php"
    httpx_mock.add_response(method="POST", url=url, match_content=data)
    settings = Settings(moodle_webservices_token="token")
    ids = [MoodleUser(id=1), MoodleUser(id=2)]
    delete_moodle_users(settings, ids)


def test_moodle_get_moodle_users_by_usernames(
    httpx_mock: HTTPXMock, monkeypatch: MonkeyPatch
):
    """Test the `get_moodle_users_by_usernames` function."""
    monkeypatch.setenv("SWARMOODLE_MOODLE_URL", "http://moodle/")
    response = [{"id": 1, "username": "11391"}, {"id": 2, "username": "28400"}]
    data = {
        "wstoken": "token",
        "moodlewsrestformat": "json",
        "wsfunction": "core_user_get_users_by_field",
        "field": "username",
        "values[0]": "11391",
        "values[1]": "28400",
    }
    data = urlencode(data, doseq=True).encode("utf8")
    url = "http://moodle/webservice/rest/server.php"
    httpx_mock.add_response(method="POST", url=url, match_content=data, json=response)
    settings = Settings(moodle_webservices_token="token")
    usernames = ["11391", "28400"]
    assert get_moodle_users_by_usernames(settings, usernames) == [
        MoodleUser(id=1, username="11391"),
        MoodleUser(id=2, username="28400"),
    ]


def test_moodle_enroll_moodle_users(httpx_mock: HTTPXMock, monkeypatch: MonkeyPatch):
    """Test the `enroll_moodle_users` function."""
    monkeypatch.setenv("SWARMOODLE_MOODLE_URL", "http://moodle/")
    data = {
        "wstoken": "token",
        "moodlewsrestformat": "json",
        "wsfunction": "enrol_manual_enrol_users",
        "enrolments[0][roleid]": "8",
        "enrolments[0][userid]": "1",
        "enrolments[0][courseid]": "9",
        "enrolments[1][roleid]": "8",
        "enrolments[1][userid]": "2",
        "enrolments[1][courseid]": "9",
    }
    data = urlencode(data, doseq=True).encode("utf8")
    url = "http://moodle/webservice/rest/server.php"
    httpx_mock.add_response(method="POST", url=url, match_content=data)
    settings = Settings(
        moodle_webservices_token="token", moodle_student_role_id=8, moodle_course_id=9
    )
    users = [
        MoodleUser(id=1, username="11391"),
        MoodleUser(id=2, username="28400"),
    ]
    enroll_moodle_users(settings, users)
