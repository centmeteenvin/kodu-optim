from __future__ import annotations

import datetime
import random
import shutil
from functools import cache
from pathlib import Path

import optuna
from fastapi import UploadFile

from dobu_manager.config import OrchestratorConfig
from dobu_manager.repositories.study_repository import (
    create_study,
    find_all_studies,
    find_study_by_name,
    update_study,
)
from shared.models.study import CodeBaseStudy, CreateStudy


@cache
def _get_studies_dir() -> Path:
    return OrchestratorConfig.get().data_dir / "studies"


def insert_study(data: CreateStudy) -> CodeBaseStudy:
    study = CodeBaseStudy(
        name=data.name,
        direction=data.direction,
        created_at=datetime.datetime.now(),
        objective_file=data.objective_file,
        objective_function=data.objective_function,
    )
    optuna.create_study(
        storage=OrchestratorConfig.get().db_url,
        direction=study.direction,
        study_name=study.name,
    )

    create_study(study)
    return study


def get_study_by_name(name: str) -> CodeBaseStudy | None:
    return find_study_by_name(name)


def get_all_studies() -> list[CodeBaseStudy]:
    return find_all_studies()


def does_study_exists(name: str) -> bool:
    return find_study_by_name(name) is not None


def is_codebase_present(name: str) -> bool:
    study_dir = _get_studies_dir() / name
    return study_dir.exists() and len(list(study_dir.iterdir())) > 0


def select_single_study() -> CodeBaseStudy | None:
    all_studies = find_all_studies()
    eligible = [study for study in all_studies if study.state == "running"]
    if len(eligible) == 0:
        return None
    return random.choice(eligible)


def activate_study(name: str) -> CodeBaseStudy:
    study = find_study_by_name(name)
    study.state = "running"
    update_study(study)
    return study


def pause_study(name: str) -> CodeBaseStudy:
    study = find_study_by_name(name)
    study.state = "paused"
    update_study(study)
    return study


def get_study_codebase_zip(name: str) -> Path:
    return _get_studies_dir() / name / "data.zip"


def store_codebase_zip(
    name: str,
    data: UploadFile,
) -> Path:
    study_dir = _get_studies_dir() / name

    # Clear directory if exists
    if study_dir.exists():
        shutil.rmtree(study_dir)
    study_dir.mkdir(parents=True)

    # Save the uploaded zip file to the study directory as data.zip
    zip_path = study_dir / "data.zip"
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(data.file, buffer)

    return zip_path
