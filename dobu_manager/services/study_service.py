from __future__ import annotations
import datetime
import pathlib
import random

from filelock import FileLock
from loguru import logger
from tinydb import JSONStorage, Query, TinyDB
from tinydb.middlewares import Middleware

from shared.models.study import CreateStudy, Study

class LockLayer(Middleware):
    def __init__(self, storage_cls):
        super().__init__(storage_cls)
        self.lock = None
        
    def __call__(self, *args, **kwargs):
        path = pathlib.Path(args[0]).absolute()
        self.lock = FileLock(path.with_suffix(".lock"))
        return super().__call__(*args, **kwargs)
    
    def write(self, data) -> None:
        with self.lock:
            self.storage.write(data)
        


class StudyService():
    _instance : StudyService |None = None
    
    @staticmethod
    def get() -> StudyService:
        if StudyService._instance is None:
            logger.error("Tried to access the study service before it was initialized")
            raise Exception("Study service is not yet initialized")
        
        return StudyService._instance
            
    
    def __init__(self, db_file: pathlib.Path, study_directory: pathlib.Path):
        if not db_file.exists():
            db_file.touch()
        self.db = TinyDB(db_file, indent=4,storage=LockLayer(JSONStorage))
        self.study_directory = study_directory
        if not self.study_directory.exists():
            logger.info(f"Creating Study Directory {self.study_directory}")
            self.study_directory.mkdir(parents=True, exist_ok=True)
            
        StudyService._instance = self
            
        
        
    def create_study(self, data: CreateStudy) -> Study:
        study = Study(
            name=data.name,
            direction=data.direction,
            created_at=datetime.datetime.now(),
            objective_file=data.objective_file,
            objective_function=data.objective_function,
        )
        
        self.db.insert(study.model_dump(mode="json"))
        return study
    
    def get_by_name(self, name: str) -> Study | None:
        query = Query()
        result = self.db.get(query.name == name)
        return None if result is None else Study.model_validate(result)
    
    def get_all(self) -> list[Study]:
        return [Study.model_validate(doc) for doc in self.db.all()]
    
    def activate(self, name) -> Study:
        query = Query()
        study = Study.model_validate(self.db.get(query.name == name))
        study.state = "running"
        self.db.update(study.model_dump(mode="json"), query.name == name)
        return study
    
    def pause(self, name) -> Study:
        query = Query()
        study = Study.model_validate(self.db.get(query.name == name))
        study.state = "paused"
        self.db.update(study.model_dump(mode="json"), query.name == name)
        return study
    
    def select_study(self) -> Study | None:
        all_studies = self.get_all()
        eligible = [study for study in all_studies if study.state == "running"]
        if len(eligible) == 0:
            return None
        return random.choice(eligible)