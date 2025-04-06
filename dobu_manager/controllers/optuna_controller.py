import optuna
import optuna.distributions
from fastapi import HTTPException
from optuna.storages import BaseStorage
from optuna.trial import TrialState

from dobu_manager.app import app
from dobu_manager.config import OrchestratorConfig
from shared.models.optuna import (
    OptunaGetAllTrials,
    OptunaRequestStudyFromName,
    OptunaSetParam,
    OptunaSetState,
    OptunaSetValue,
    OptunaSetValueResponse,
    OptunaStudyDirection,
    OptunaStudyIdFromName,
    OptunaStudyNameFromId,
    OptunaStudySummary,
    OptunaTrial,
    OptunaTrialCreation,
)
from shared.models.study import StudyDirection


def storage() -> BaseStorage:
    config = OrchestratorConfig.get()
    storage = optuna.storages.RDBStorage(config.db_url)
    return storage


@app.put("/optuna/study")
def get_study_id_from_name(data: OptunaRequestStudyFromName) -> OptunaStudyIdFromName:
    id = storage().get_study_id_from_name(data.study_name)
    return OptunaStudyIdFromName(id=id)


@app.get("/optuna/study/{study_id}")
def get_study_name_from_id(study_id: int) -> OptunaStudyNameFromId:
    name = storage().get_study_name_from_id(study_id)
    return OptunaStudyNameFromId(name=name)


@app.get("/optuna/study/{study_id}/trials")
def get_all_trails_from_study(study_id: int) -> OptunaGetAllTrials:
    trials = storage().get_all_trials(study_id)
    return OptunaGetAllTrials(
        trials=[
            OptunaTrial.from_frozen(
                trial_id=storage().get_trial_id_from_study_id_trial_number(
                    study_id=study_id, trial_number=trial.number
                ),
                trial=trial,
            )
            for trial in trials
        ]
    )


direction_mapper: dict[optuna.study.StudyDirection, StudyDirection] = {
    optuna.study.StudyDirection.MAXIMIZE: "maximize",
    optuna.study.StudyDirection.MINIMIZE: "minimize",
}


@app.get("/optuna/study/{study_id}/direction")
def get_study_direction(study_id: int) -> OptunaStudyDirection:
    directions = storage().get_study_directions(study_id)
    return OptunaStudyDirection(
        directions=[direction_mapper[direction] for direction in directions]
    )


@app.post("/optuna/study/{study_id}")
def create_new_trial(study_id: int) -> OptunaTrialCreation:
    trial_id = storage().create_new_trial(study_id, None)
    return OptunaTrialCreation(trial_id=trial_id)


@app.get("/optuna/trial/{trial_id}")
def get_trial(trial_id: int) -> OptunaTrial:
    trial = storage().get_trial(trial_id)
    return OptunaTrial.from_frozen(trial_id=trial_id, trial=trial)


@app.post("/optuna/trial/{trial_id}")
def set_trial_values(trial_id: int, data: OptunaSetValue) -> OptunaSetValueResponse:
    try:
        result = storage().set_trial_state_values(
            trial_id, state=data.state, values=data.value
        )
        return OptunaSetValueResponse(did_update=result)
    except RuntimeError:
        raise HTTPException(400, "trial already completed")


@app.post("/optuna/trial/{trial_id}/state")
def set_trial_state(trial_id: int, data: OptunaSetState):
    try:
        enum_state = TrialState[data.state.upper()]
        storage().set_trial_state_values(trial_id, enum_state)
        return {"ok": True}
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid trial state.")


@app.post("/optuna/trial/{trial_id}/trial-param")
def set_trial_param(trial_id: int, data: OptunaSetParam):
    dist = optuna.distributions.json_to_distribution(data.distribution)
    storage().set_trial_param(trial_id, data.name, data.value, dist)
    return {"ok": True}


@app.get("/optuna/study-summaries")
def handle_get_all_study_summaries() -> list[OptunaStudySummary]:
    optuna.study.get_all_study_summaries(storage())
    return [
        OptunaStudySummary.from_native(summary)
        for summary in storage().get_all_studies()
    ]
