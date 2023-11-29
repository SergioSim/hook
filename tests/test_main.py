"""Hook API main entrypoint test."""

import pytest
from httpx import AsyncClient

from hook.main import patch_moodle_url

COURSES_COUNT = 3


@pytest.mark.anyio
async def test_main_root(client: AsyncClient):
    """Test the main root route."""
    response = (await client.get("/")).json()
    assert response == {"sitename": "Hook", "siteurl": "http://moodle"}


@pytest.mark.anyio
async def test_main_root_with_raw(client: AsyncClient):
    """Test the main root route with `raw=1`."""
    response = (await client.get("/?raw=1")).json()
    assert response["username"] == "admin"


@pytest.mark.anyio
async def test_main_courses(client: AsyncClient):
    """Test the courses route."""
    response = (await client.get("/courses")).json()
    assert len(response) == COURSES_COUNT
    assert response[1] == {
        "id": 3,
        "fullname": "Digital Literacy ",
        "url": "http://moodle/course/view.php?id=3",
        "summary": (
            "<p>Introducing the concept of Digital Literacy. Optimised for mobile.</p>"
        ),
    }


@pytest.mark.anyio
async def test_main_courses_with_raw(client: AsyncClient):
    """Test the courses route with `raw=1`."""
    response = (await client.get("/courses?raw=1")).json()
    assert len(response) == COURSES_COUNT + 1
    assert response[0]["fullname"] == "Hook"


@pytest.mark.anyio
async def test_main_courses_with_course_id(client: AsyncClient):
    """Test the courses/{course_id} route."""
    response = (await client.get("/courses/3")).json()
    assert len(response) == 23
    assert response[0] == {
        "id": 23,
        "instance": 3,
        "name": "Announcements",
        "modname": "forum",
        "url": "http://moodle/mod/forum/view.php?id=23",
        "contents": [],
    }
    assert response[18] == {
        "id": 42,
        "instance": 2,
        "name": " Digital Literacies in Higher Ed",
        "modname": "url",
        "url": "http://moodle/mod/url/view.php?id=42",
        "contents": [
            {
                "type": "url",
                "mimetype": "text/html",
                "fileurl": (
                    "https://www.heacademy.ac.uk/enhancement/starter-tools/"
                    "digital-literacies"
                ),
                "content": None,
            }
        ],
    }


@pytest.mark.anyio
async def test_main_courses_with_course_id_with_raw(client: AsyncClient):
    """Test the courses/{course_id} route with `raw=1`."""
    response = (await client.get("/courses/3?raw=1")).json()
    assert len(response) == 5
    assert response[0]["visible"] == 1


@pytest.mark.anyio
async def test_main_quiz_with_quiz_id(client: AsyncClient):
    """Test the quiz/{quiz_id} route."""
    response = (await client.get("/quiz/2")).json()
    assert len(response) == 8
    assert 'The variable "x" can only contain a number.' in response[0]["html"]


@pytest.mark.anyio
async def test_main_quiz_with_quiz_id_with_raw(client: AsyncClient):
    """Test the quiz/{quiz_id} route with `raw=1`."""
    response = (await client.get("/quiz/1?raw=1")).json()
    assert response["attempt"]["layout"] == "1,2,3,4,5,6,0"


def test_main_patch_moodle_url(monkeypatch):
    """Test the `patch_moodle_url` function."""
    monkeypatch.setenv("HOOK_MOODLE_URL", "http://foo")
    assert patch_moodle_url("http://bar:8080/hello/world") == "http://foo/hello/world"
    assert patch_moodle_url(None, None) is None
