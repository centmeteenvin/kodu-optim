import functools
from dataclasses import dataclass
from pathlib import Path

from filelock import FileLock
from loguru import logger
from tinydb import JSONStorage, Query, TinyDB
from tinydb.middlewares import Middleware

from dobu_manager.config import OrchestratorConfig
from shared.models.study import CodeBaseStudy


class LockLayer(Middleware):
    def __init__(self, storage_cls):
        super().__init__(storage_cls)
        self.lock = None

    def __call__(self, *args, **kwargs):
        path = Path(args[0]).absolute()
        self.lock = FileLock(path.with_suffix(".lock"))
        return super().__call__(*args, **kwargs)

    def write(self, data) -> None:
        with self.lock:
            self.storage.write(data)


@dataclass
class StudyRepositoryConfig:
    db: TinyDB

    @staticmethod
    def create(config: OrchestratorConfig):
        db_file = config.data_dir / "db.json"
        if not db_file.exists():
            logger.info(f"Creating Study database file: {db_file.as_posix()}")
            db_file.touch(exist_ok=False)
        db = TinyDB(db_file, indent=4, storage=LockLayer(JSONStorage))
        return StudyRepositoryConfig(db=db)


@functools.cache
def _get_db() -> TinyDB:
    return StudyRepositoryConfig.create(OrchestratorConfig.get()).db


def create_study(study: CodeBaseStudy) -> CodeBaseStudy:
    _get_db().insert(study.model_dump(mode="json"))


def update_study(
    study: CodeBaseStudy,
) -> CodeBaseStudy:
    query = Query()
    _get_db().update(study.model_dump(mode="json"), query.name == study.name)


def delete_study(
    study_name: str,
) -> None:
    query = Query()

    _get_db().remove(query.name == study_name)


def find_study_by_name(study_name: str) -> CodeBaseStudy | None:
    query = Query()

    raw = _get_db().get(query.name == study_name)
    if raw is None:
        return raw

    return CodeBaseStudy.model_validate(raw)


def find_all_studies() -> list[CodeBaseStudy]:
    return [CodeBaseStudy.model_validate(doc) for doc in _get_db().all()]
