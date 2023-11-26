"""Swarm Moodle with OULAD students."""

import logging
import time
from logging.config import dictConfig

import gevent
from bs4 import BeautifulSoup
from faker import Faker
from locust import FastHttpUser, events, stats, task
from locust.env import Environment
from locust.exception import StopUser
from locust.runners import (
    STATE_CLEANUP,
    STATE_STOPPED,
    STATE_STOPPING,
    LocalRunner,
    MasterRunner,
)
from redis import Redis

from swarmoodle.conf import get_settings
from swarmoodle.moodle import (
    create_moodle_users,
    delete_moodle_users,
    enroll_moodle_users,
    get_moodle_course,
    get_moodle_users_by_usernames,
)
from swarmoodle.oulad import (
    filter_by_module_presentation,
    get_oulad,
    map_oulad_to_moodle,
)

settings = get_settings()
dictConfig(settings.logging)

stats.STATS_NAME_WIDTH = 70
stats.STATS_TYPE_WIDTH = 5

logger = logging.getLogger(__name__)
fake = Faker(["en_US"])
redis = Redis.from_url(str(settings.redis_dsn))

oulad = get_oulad()
students = (
    filter_by_module_presentation(
        oulad.student_info, settings.oulad_code_module, settings.oulad_code_presentation
    )
    .iloc[0 : settings.moodle_students]
    .set_index("id_student")
)
student_vle = (
    filter_by_module_presentation(
        oulad.student_vle, settings.oulad_code_module, settings.oulad_code_presentation
    )
    .set_index("id_student")
    .join(students.loc[:, []], how="right")
)
vle = (
    filter_by_module_presentation(
        oulad.vle, settings.oulad_code_module, settings.oulad_code_presentation
    )
    .drop(columns=["week_from", "week_to"])
    .set_index("id_site")
    .pipe(lambda df: df[df.index.isin(student_vle.id_site)])
)

moodle_course = get_moodle_course(settings)
moodle_id_by_oulad_site = map_oulad_to_moodle(vle, moodle_course)
moodle_vle = (
    student_vle[student_vle.id_site.isin(moodle_id_by_oulad_site.keys())]
    .replace({"id_site": moodle_id_by_oulad_site})
    .astype({"id_site": int, "sum_click": int})
    .pivot_table(
        aggfunc="sum",
        columns="date",
        fill_value=0,
        index=["id_student", "id_site"],
        values="sum_click",
    )
)
moodle_vle_students = moodle_vle.index.get_level_values("id_student").unique()

day_duration = moodle_vle.sum().max() * settings.request_milliseconds_duration / 1000


def checker(environment: Environment):
    """Stop test execution after all users finished their tasks."""
    states = [STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP]
    while environment.runner.state not in states:
        time.sleep(1)
        if not environment.runner.user_count and environment.runner.stats.num_requests:
            logger.info("All users finished their tasks - quitting the runner")
            environment.runner.quit()
            return


@events.init.add_listener
def on_locust_init(environment, **_):
    """Spawn checker greenlet."""
    is_master = isinstance(environment.runner, MasterRunner)
    if is_master or isinstance(environment.runner, LocalRunner):
        gevent.spawn(checker, environment)


@events.test_start.add_listener
def on_test_start(environment, **_):  # pylint: disable=unused-argument
    """Create and enroll Moodle users to a course.

    Extract test plan from OULAD dataset.
    """
    logger.info("The simulation will simulate %d interactions", moodle_vle.sum().sum())
    if settings.simulate_fixed_day_duration:
        logger.info(
            "Day duration set to %.1f seconds; expected completion time: %.1f minutes",
            day_duration,
            day_duration * (len(moodle_vle.columns)) / 60,
        )
    if settings.moodle_students != students.shape[0]:
        logger.info(
            "The number of simulated users (%d) if not equal to the number "
            "of OULAD users (%d) - missing or additional users are ignored",
            settings.moodle_students,
            students.shape[0],
        )

    logger.info("Resetting redis user day and login counters")
    redis.set("login", 0)
    for i in moodle_vle.columns:
        redis.set(i, 0)

    moodle_users = get_moodle_users_by_usernames(settings, students.index.tolist())
    if moodle_users:
        delete_moodle_users(settings, moodle_users)

    moodle_users = create_moodle_users(settings, students)
    enroll_moodle_users(settings, moodle_users)


@events.test_stop.add_listener
def on_test_stop(environment, **_):  # pylint: disable=unused-argument
    """Delete Moodle users of a course."""
    if settings.moodle_delete_users_after_run:
        moodle_users = get_moodle_users_by_usernames(settings, students.index.tolist())
        delete_moodle_users(settings, moodle_users)


class OuladMoodleStudent(FastHttpUser):
    """An OULAD student navigating on Moodle."""

    host = "http://localhost:8080"
    network_timeout = settings.request_timeout
    connection_timeout = settings.request_timeout
    max_retries = 3

    def __init__(self, *args, **kwargs):
        """Initialize OuladMoodleStudent."""
        super().__init__(*args, **kwargs)
        self.id = None
        self.username = None
        self.vle = None
        self.error = None
        self.client.client.retry_delay = 1

    def login(self):
        """Login user."""
        logger.info("Loggin in User %4d", self.id)
        login_page = self.client.get("/login/index.php")
        login_page.raise_for_status()
        soup = BeautifulSoup(login_page.text, "html.parser")
        token = soup.find("input", attrs={"name": "logintoken"})["value"]
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "anchor": "",
            "username": self.username,
            "password": settings.moodle_student_password,
            "logintoken": token,
        }
        response = self.client.post("/login/index.php", data=data, headers=headers)
        response.raise_for_status()
        logger.info("User %4d logged in with status %d", self.id, response.status_code)

    def logout(self):
        """Logout user."""
        home_page = self.client.get("/my/")
        home_page.raise_for_status()
        soup = BeautifulSoup(home_page.text, "html.parser")
        logout_url = soup.find("div", id="carousel-item-main").find_all("a")[-1]["href"]
        response = self.client.get(logout_url)
        response.raise_for_status()
        logger.info("User %4d logged out with status %d", self.id, response.status_code)

    @task
    def navigate(self):
        """User navigates the moodle course.

        Navigation plan:
        1. User logs in and waits for other users to log in.
        2. User navigates mapped learning items for the current day.
        3. User waits for other users to finish their navigation day.
           NB: If `simulate_fixed_day_duration` is set to `True`, each navigation day
           has a fixed duration. If the user does not complete his navigation day in
           time, he stops navigation.
        4. User navigates for the next day etc. until the end of the course.
        5. User logs out.
        """
        if self.error:
            while self.environment.runner.user_count < settings.moodle_students:
                # Wait for locust to spawn remaining students before quitting to attain
                # peak number of concurrent locust users.
                time.sleep(1)

            logger.info(self.error, self.id)
            raise StopUser()

        # 1. User logs in and waits for other users to log in.
        self.login()
        redis.incr("login")
        while int(redis.get("login")) != moodle_vle_students.shape[0]:
            time.sleep(1)

        for day, values in self.vle.items():
            start_time = time.time()
            # 2. User navigates mapped learning items for the current day.
            for moodle_id, sum_click in values[values > 0].items():
                moodle_url = moodle_course[moodle_id]["url"]
                pool = gevent.pool.Pool()
                _ = [pool.spawn(self.client.get, moodle_url) for _ in range(sum_click)]
                pool.join()
                logger.info(
                    "User %4d on day %3d clicked %3d times on %s",
                    self.id,
                    day,
                    sum_click,
                    moodle_url,
                )
                if settings.simulate_fixed_day_duration:
                    end_time = time.time()
                    elapsed = end_time - start_time
                    if elapsed > day_duration:
                        logger.warning(
                            "User %4d out of sync by %.2f seconds! Skipping day",
                            self.id,
                            elapsed - day_duration,
                        )
                        break

            redis.incr(day)
            if settings.simulate_fixed_day_duration:
                end_time = time.time()
                elapsed = end_time - start_time
                time.sleep(day_duration - elapsed)

            # 3. User waits for other users to finish their navigation day.
            while int(redis.get(day)) != moodle_vle_students.shape[0]:
                time.sleep(1)

            # 4. User navigates for the next day etc. until the end of the course.

        # 5. User logs out.
        self.logout()
        logger.info("User %4d finished", self.id)
        raise StopUser()

    def on_start(self):
        """Setup Moodle user navigation plan."""
        self.id = self.greenlet.getcurrent().minimal_ident
        if self.id >= students.shape[0]:
            self.error = "User %4d has no OULAD mapping. Skipping"
            return
        self.username = int(students.index[self.id])
        if self.username not in moodle_vle_students:
            self.error = "User %4d didn't interact with course. Skipping"
            return
        self.vle = moodle_vle.loc[self.username]
