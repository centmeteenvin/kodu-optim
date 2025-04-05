import datetime
from typing import Literal

from pydantic import BaseModel

type StudyDirection = Literal["minimize"] | Literal["maximize"]


class CreateStudy(BaseModel):
    name: str
    direction: StudyDirection = "minimize"
    objective_file: str
    objective_function: str


type StudyState = Literal["paused"] | Literal["running"]


class CodeBaseStudy(BaseModel):
    name: str
    direction: StudyDirection = "minimize"
    objective_file: str
    objective_function: str
    state: StudyState = "paused"
    created_at: datetime.datetime
