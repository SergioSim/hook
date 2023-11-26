"""Loading the OULAD dataset into memory."""

import logging
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pandas as pd

from swarmoodle.conf import get_settings

logger = logging.getLogger(__name__)


@dataclass
class OULAD:
    """The OULAD dataset tables."""

    # pylint: disable=too-many-instance-attributes

    assessments: pd.DataFrame
    courses: pd.DataFrame
    domains: pd.DataFrame
    student_assessment: pd.DataFrame
    student_info: pd.DataFrame
    student_registration: pd.DataFrame
    student_vle: pd.DataFrame
    vle: pd.DataFrame


@lru_cache(maxsize=1)
def get_oulad(path: Path = None) -> OULAD:
    """Return the OULAD dataset tables in a dataclass."""
    path = path if path else get_settings().oulad_default_path
    return OULAD(
        assessments=pd.read_csv(f"{path}/assessments.csv"),
        courses=pd.read_csv(f"{path}/courses.csv"),
        domains=pd.DataFrame(
            {
                "code_module": ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG"],
                "domain": [
                    "Social Sciences",
                    "Social Sciences",
                    "STEM",
                    "STEM",
                    "STEM",
                    "STEM",
                    "Social Sciences",
                ],
            },
        ),
        student_assessment=pd.read_csv(f"{path}/studentAssessment.csv"),
        student_info=pd.read_csv(f"{path}/studentInfo.csv"),
        student_registration=pd.read_csv(f"{path}/studentRegistration.csv"),
        student_vle=pd.read_csv(f"{path}/studentVle.csv"),
        vle=pd.read_csv(f"{path}/vle.csv"),
    )


def filter_by_module_presentation(
    data: pd.DataFrame, code_module: str, code_presentation: str, drop: bool = True
) -> pd.DataFrame:
    """Filter the `data` DataFrame by `code_module` and `code_presentation`.

    Args:
        data (DataFrame): The OULAD DataFrame with `code_module` and
            `code_presentation` columns.
        code_module (str): The `code_module` column value to filter.
        code_presentation (str): The `code_presentation` column value to filter.
        drop (bool): Whether to drop the `code_module` and `code_presentation`
            columns after filtering. By default is set to `True`.

    Return:
        result (DataFrame): The filtered OULAD DataFrame.
    """
    result = data.loc[
        (data.code_module == code_module)
        & (data.code_presentation == code_presentation)
    ]
    if drop:
        return result.drop(["code_module", "code_presentation"], axis=1)

    return result


def map_oulad_to_moodle(vle: pd.DataFrame, moodle_course: list[dict]) -> dict:
    """Map OULAD activities with moodle course items."""
    moodle_oulad_map = {
        "resource": ["resource"],
        "book": ["oucontent"],
        "url": ["url"],
        "page": ["page", "subpage", "dualpane"],
        "glossary": ["glossary"],
        "forum": ["forumng"],
        "workshop": ["oucollaborate"],
        "data": ["dataplus"],
        "quiz": ["quiz"],
        "lesson": ["ouelluminate"],
        "scorm": ["sharedsubpage", "externalquiz", "htmlactivity"],
        "feedback": ["questionnaire"],
        "survey": ["questionnaire"],
        "choice": ["questionnaire"],
        "wiki": ["ouwiki"],
        "h5pactivity": ["repeatactivity"],
        "folder": ["folder"],
        "homepage": ["homepage"],
    }
    site_by_activity = vle.groupby("activity_type").groups
    last_used_index = {activity: 0 for activity in site_by_activity}
    moodle_id_by_oulad_site = {}
    for i, activity_type in enumerate(map(lambda x: x["modname"], moodle_course)):
        for oulad_activity_type in moodle_oulad_map.get(activity_type, []):
            indices = site_by_activity.get(oulad_activity_type, [])
            last_index = last_used_index.get(oulad_activity_type, math.inf)
            if len(indices) > last_index:
                last_used_index[oulad_activity_type] += 1
                moodle_id_by_oulad_site[indices[last_index]] = i
                break

    total_moodle = len(moodle_course)
    total_oulad = vle.shape[0]
    mapped = len(moodle_id_by_oulad_site)
    logger.info(
        "Mapped %d (%.2f%%) out of %d Moodle modules from %d (%.2f%%) OULAD activities",
        mapped,
        100 * mapped / total_moodle,
        total_moodle,
        total_oulad,
        100 * mapped / total_oulad,
    )
    return moodle_id_by_oulad_site
