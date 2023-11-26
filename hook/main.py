"""Hook API main entrypoint."""

import os
import re
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, Request


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Add moodle clients to the FastAPI app at startup."""
    moodle_url = os.environ.get("HOOK_MOODLE_URL")
    token = os.environ.get("HOOK_MOODLE_WEBSERVICE_TOKEN")
    fastapi_app.moodle = httpx.AsyncClient(
        base_url=f"{moodle_url}/webservice/rest/server.php",
        params={"wstoken": token, "moodlewsrestformat": "json"},
    )
    fastapi_app.moodle_file = httpx.AsyncClient(
        base_url=f"{moodle_url}/webservice/pluginfile.php", params={"token": token}
    )

    yield

    await fastapi_app.moodle.aclose()
    await fastapi_app.moodle_file.aclose()


app = FastAPI(lifespan=lifespan)


def patch_moodle_url(url: str) -> str:
    """Replace the hostname in `url` with the `HOOK_MOODLE_URL` value."""
    if not url:
        return None

    moodle_url = urlparse(os.environ.get("HOOK_MOODLE_URL"))
    moodle_netloc = moodle_url.netloc
    moodle_scheme = moodle_url.scheme
    return urlparse(url)._replace(netloc=moodle_netloc, scheme=moodle_scheme).geturl()


@app.get("/")
async def root(request: Request, raw: bool = False):
    """Get Moodle site info."""
    data = {"wsfunction": "core_webservice_get_site_info"}
    result = (await request.app.moodle.post("/", data=data)).json()
    if raw:
        return result

    return {
        "sitename": result.get("sitename"),
        "siteurl": patch_moodle_url(result.get("siteurl")),
    }


@app.get("/courses")
async def courses(request: Request, raw: bool = False):
    """Get the list of visible Moodle courses."""
    data = {"wsfunction": "core_course_get_courses"}
    result = (await request.app.moodle.post("/", data=data)).json()
    if raw:
        return result

    return [
        {
            "id": course.get("id"),
            "fullname": course.get("fullname"),
            "url": patch_moodle_url(f"/course/view.php?id={course.get('id')}"),
            "summary": course.get("summary"),
        }
        for course in result
        if course.get("visible") and course.get("format") != "site"
    ]


@app.get("/courses/{course_id}")
async def course(
    request: Request, course_id: int, raw: bool = False, html: bool = True
):
    """Get the list of visible Moodle course modules by `course_id`."""
    data = {
        "wsfunction": "core_course_get_contents",
        "courseid": course_id,
    }
    result = (await request.app.moodle.post("/", data=data)).json()
    if raw:
        return result

    get_file = request.app.moodle_file.post
    return [
        {
            "id": module.get("id"),
            "instance": module.get("instance"),
            "name": module.get("name"),
            "modname": module.get("modname"),
            "url": patch_moodle_url(module.get("url")),
            "contents": [
                {
                    "type": content.get("type"),
                    "mimetype": content.get("mimetype", "text/html"),
                    "fileurl": patch_moodle_url(content["fileurl"])
                    if content.get("type") == "file"
                    else content["fileurl"],
                    "content": (
                        await get_file(patch_moodle_url(content["fileurl"]))
                    ).text
                    if content.get("type") == "file"
                    and content.get("mimetype", "text/html").startswith("text")
                    else None,
                }
                for content in module.get("contents", [])
                if content.get("type") != "content" and content.get("fileurl")
            ]
            if module.get("modname") != "quiz" and html
            else (await quiz(request, int(module.get("instance"))))
            if html
            else None,
        }
        for section in result
        for module in section.get("modules", [])
        if (
            section.get("visible")
            and module.get("visible")
            and module.get("modname") != "label"
        )
    ]


@app.get("/quiz/{quiz_id}")
async def quiz(request: Request, quiz_id: int, raw: bool = False):
    """Get Moodle quiz contents by `quiz_id`."""
    data = {
        "wsfunction": "mod_quiz_get_user_attempts",
        "quizid": quiz_id,
        "status": "all",
        "includepreviews": 1,
    }
    attempts = (await request.app.moodle.post("/", data=data)).json()
    # Try to retrieve existing attempt.
    attempt = next(
        (x["id"] for x in attempts.get("attempts", []) if x["state"] == "inprogress"),
        None,
    )

    # Create new attempt if no previous attempt exists.
    if not attempt:
        data = {
            "wsfunction": "mod_quiz_start_attempt",
            "quizid": quiz_id,
        }
        attempt = (await request.app.moodle.post("/", data=data)).json()["attempt"][
            "id"
        ]

    # Submit attempt.
    data = {
        "wsfunction": "mod_quiz_process_attempt",
        "attemptid": attempt,
        "finishattempt": 1,
    }
    (await request.app.moodle.post("/", data=data)).json()

    # Get attempt result.
    data = {
        "wsfunction": "mod_quiz_get_attempt_review",
        "attemptid": attempt,
    }
    result = (await request.app.moodle.post("/", data=data)).json()
    if raw:
        return result
    pattern = r"<!\[CDATA\[(.*?)\]\]>"
    return [
        {
            "slot": question.get("slot"),
            "type": question.get("type"),
            "page": question.get("page"),
            "html": re.sub(pattern, "", question.get("html"), flags=re.DOTALL),
        }
        for question in result.get("questions", [])
    ]
