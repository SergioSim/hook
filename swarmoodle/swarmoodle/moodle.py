"""Loading and handling of Moodle data."""

import logging

import httpx
import pandas as pd
from faker import Faker
from pydantic import BaseModel

from swarmoodle.conf import Settings

logger = logging.getLogger(__name__)


class MoodleUser(BaseModel, extra="allow"):
    """A Moodle user."""

    id: int


def get_moodle_course(settings: Settings) -> list[dict]:
    """Return a Moodle course by `course_id`."""
    url = f"{settings.hook_url}courses/{settings.moodle_course_id}?html=0"
    course = [
        {
            "id": 0,
            "instance": 0,
            "name": "Home page",
            "modname": "homepage",
            "url": str(settings.moodle_url),
            "contents": None,
        }
    ]
    response = httpx.get(url, timeout=settings.request_timeout)
    response.raise_for_status()
    return course + response.json()


def get_moodle_users_by_usernames(
    settings: Settings, usernames: list[str]
) -> list[MoodleUser]:
    """Return a list of Moodle users that have a matching username in `usernames`."""
    logger.info("Getting Moodle users with usernames: %s", usernames)
    data = {
        "wstoken": settings.moodle_webservices_token,
        "moodlewsrestformat": "json",
        "wsfunction": "core_user_get_users_by_field",
        "field": "username",
    }
    for i, username in enumerate(usernames):
        data[f"values[{i}]"] = username

    response = httpx.post(
        str(settings.moodle_ws_url), data=data, timeout=settings.request_timeout
    )
    response.raise_for_status()
    result = [MoodleUser(**user) for user in response.json()]
    logger.info("Found %d Moodle users with matching usernames", len(result))
    return result


def create_moodle_users(settings: Settings, students: pd.DataFrame):
    """Create moodle users from OULAD `students` records."""
    logger.info("Creating %d Moodle users", students.shape[0])
    fake = Faker(["en_US"])
    data = {
        "wstoken": settings.moodle_webservices_token,
        "moodlewsrestformat": "json",
        "wsfunction": "core_user_create_users",
    }
    for i, row in enumerate(students.itertuples()):
        first_name = fake.first_name_male
        last_name = fake.last_name_male
        if row.gender == "F":
            first_name = fake.first_name_female
            last_name = fake.last_name_female

        data[f"users[{i}][createpassword]"] = 0
        data[f"users[{i}][username]"] = row.Index
        data[f"users[{i}][password]"] = settings.moodle_student_password
        data[f"users[{i}][firstname]"] = first_name()
        data[f"users[{i}][lastname]"] = last_name()
        data[f"users[{i}][email]"] = f"{row.Index}@gmail.com"
        data[f"users[{i}][country]"] = "GB"
        data[f"users[{i}][timezone]"] = "Europe/London"
        data[f"users[{i}][institution]"] = "Open Univesity"
        data[f"users[{i}][customfields][0][type]"] = "gender"
        data[f"users[{i}][customfields][0][value]"] = row.gender
        data[f"users[{i}][customfields][1][type]"] = "region"
        data[f"users[{i}][customfields][1][value]"] = row.region
        data[f"users[{i}][customfields][2][type]"] = "highest_education"
        data[f"users[{i}][customfields][2][value]"] = row.highest_education
        data[f"users[{i}][customfields][3][type]"] = "imd_band"
        data[f"users[{i}][customfields][3][value]"] = row.imd_band
        data[f"users[{i}][customfields][4][type]"] = "age_band"
        data[f"users[{i}][customfields][4][value]"] = row.age_band
        data[f"users[{i}][customfields][5][type]"] = "num_of_prev_attempts"
        data[f"users[{i}][customfields][5][value]"] = row.num_of_prev_attempts
        data[f"users[{i}][customfields][6][type]"] = "studied_credits"
        data[f"users[{i}][customfields][6][value]"] = row.studied_credits
        data[f"users[{i}][customfields][7][type]"] = "disability"
        data[f"users[{i}][customfields][7][value]"] = row.disability
        data[f"users[{i}][customfields][8][type]"] = "final_result"
        data[f"users[{i}][customfields][8][value]"] = row.final_result

    response = httpx.post(
        str(settings.moodle_ws_url), data=data, timeout=settings.request_timeout
    )
    response.raise_for_status()
    result = [MoodleUser(**user) for user in response.json()]
    logger.info("Created %d Moodle users", len(result))
    return result


def delete_moodle_users(settings: Settings, users: list[MoodleUser]) -> None:
    """Delete moodle users by their ids."""
    logger.info("Deleting %d Moodle users", len(users))
    data = {
        "wstoken": settings.moodle_webservices_token,
        "moodlewsrestformat": "json",
        "wsfunction": "core_user_delete_users",
    }
    for i, user in enumerate(users):
        data[f"userids[{i}]"] = user.id

    response = httpx.post(
        str(settings.moodle_ws_url), data=data, timeout=settings.request_timeout
    )
    response.raise_for_status()
    logger.info("Deleted %d users", len(users))


def enroll_moodle_users(settings: Settings, users: list[MoodleUser]) -> None:
    """Enroll moodle users by their ids."""
    logger.info("Enrolling %d Moodle users", len(users))
    data = {
        "wstoken": settings.moodle_webservices_token,
        "moodlewsrestformat": "json",
        "wsfunction": "enrol_manual_enrol_users",
    }
    for i, user in enumerate(users):
        data[f"enrolments[{i}][roleid]"] = settings.moodle_student_role_id
        data[f"enrolments[{i}][userid]"] = user.id
        data[f"enrolments[{i}][courseid]"] = settings.moodle_course_id

    response = httpx.post(
        str(settings.moodle_ws_url), data=data, timeout=settings.request_timeout
    )
    response.raise_for_status()
    logger.info("Enrolled %d Moodle users", len(users))
