from __future__ import annotations

import datetime
from typing import Any, Sequence

import optuna
from pydantic import BaseModel

from shared.models.study import StudyDirection


class OptunaStudyIdFromName(BaseModel):
    id: int


class OptunaStudyNameFromId(BaseModel):
    name: str


class OptunaStudyDirection(BaseModel):
    directions: list[StudyDirection]


class OptunaTrialCreation(BaseModel):
    trial_id: int


class OptunaGetAllTrials(BaseModel):
    trials: list[OptunaTrial]


class OptunaTrial(BaseModel):
    trial_id: int
    number: int
    state: optuna.trial.TrialState
    datetime_start: datetime.datetime
    datetime_complete: datetime.datetime | None
    distributions: dict[str, str]
    intermediate_values: dict[int, float]
    params: dict[str, Any]
    system_attributes: dict[str, Any]
    user_attributes: dict[str, Any]
    value: float | None
    values: Sequence[float] | None

    @staticmethod
    def from_frozen(trial_id: int, trial: optuna.trial.FrozenTrial) -> OptunaTrial:
        return OptunaTrial(
            trial_id=trial_id,
            number=trial.number,
            state=trial.state,
            datetime_start=trial.datetime_start,
            datetime_complete=trial.datetime_complete,
            distributions={
                key: optuna.distributions.distribution_to_json(value)
                for key, value in trial.distributions.items()
            },
            intermediate_values=trial.intermediate_values,
            params=trial.params,
            system_attributes=trial.system_attrs,
            user_attributes=trial.user_attrs,
            value=trial.value,
            values=trial.values
            if len(trial.values if trial.values is not None else []) > 1
            else None,
        )

    def to_native(self) -> optuna.trial.FrozenTrial:
        return optuna.trial.FrozenTrial(
            trial_id=self.trial_id,
            datetime_start=self.datetime_start,
            datetime_complete=self.datetime_complete,
            intermediate_values=self.intermediate_values,
            distributions={
                key: optuna.distributions.json_to_distribution(value)
                for key, value in self.distributions.items()
            },
            number=self.number,
            params=self.params,
            state=self.state,
            system_attrs=self.system_attributes,
            user_attrs=self.user_attributes,
            value=self.value,
            values=self.values,
        )


class OptunaStudySummary(BaseModel):
    study_id: int
    study_name: str
    direction: optuna.study.StudyDirection | None
    best_trial: OptunaTrial | None
    user_attrs: dict[str, Any]
    system_attrs: dict[str, Any]
    n_trials: int
    datetime_start: datetime.datetime | None

    @staticmethod
    def from_native(summary: optuna.study.StudySummary) -> OptunaStudySummary:
        return OptunaStudySummary(
            study_id=summary._study_id,
            study_name=summary.study_name,
            best_trial=OptunaTrial.from_frozen(summary.best_trial)
            if summary.best_trial is not None
            else None,
            direction=summary.direction,
            datetime_start=summary.datetime_start,
            n_trials=summary.n_trials,
            system_attrs=summary.system_attrs,
            user_attrs=summary.user_attrs,
        )


class OptunaRequestStudyFromName(BaseModel):
    study_name: str


class OptunaSetValue(BaseModel):
    state: optuna.trial.TrialState
    value: float | Sequence[float] | None


class OptunaSetValueResponse(BaseModel):
    did_update: bool


class OptunaSetState(BaseModel):
    state: str


class OptunaSetParam(BaseModel):
    name: str
    value: float
    distribution: str
