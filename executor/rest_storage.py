import asyncio
from typing import Type, TypeVar, override

import optuna
from pydantic import BaseModel

from executor.requests import HTTPMethod, request
from shared.models.optuna import (
    OptunaGetAllTrials,
    OptunaRequestStudyFromName,
    OptunaSetParam,
    OptunaSetValue,
    OptunaSetValueResponse,
    OptunaStudyDirection,
    OptunaStudyIdFromName,
    OptunaStudyNameFromId,
    OptunaTrial,
    OptunaTrialCreation,
)

T = TypeVar("wr", bound=BaseModel)


class RestStorage(optuna.storages.BaseStorage):
    """
    An optuna storage implementation that is compatible with the
    Koko Orchestrator
    """

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        """The fully fledge domain url to the orchestrator"""

    def _sent_request(
        self,
        method: HTTPMethod,
        path: str,
        body: BaseModel | None,
        result_type: Type[T] | None,
    ) -> T | None:
        result: T | None = asyncio.run(
            request(
                url=f"{self.url}/optuna/{path}",
                method=method,
                data=body,
                result_type=result_type,
            )
        )
        return result

    @override
    def create_new_study(self, directions, study_name=None):
        raise NotImplementedError

    @override
    def delete_study(self, study_id):
        raise NotImplementedError

    @override
    def set_study_user_attr(self, study_id, key, value):
        raise NotImplementedError

    @override
    def set_study_system_attr(self, study_id, key, value):
        raise NotImplementedError

    @override
    def get_study_id_from_name(self, study_name):
        response = self._sent_request(
            "PUT",
            "study",
            OptunaRequestStudyFromName(study_name=study_name),
            OptunaStudyIdFromName,
        )
        return response.id

    @override
    def get_study_name_from_id(self, study_id) -> str:
        response = self._sent_request(
            "GET", f"study/{study_id}", None, OptunaStudyNameFromId
        )
        return response.name

    @override
    def get_study_directions(self, study_id) -> list[optuna.study.StudyDirection]:
        response = self._sent_request(
            "GET", f"study/{study_id}/direction", None, OptunaStudyDirection
        )
        return response.directions

    @override
    def get_study_user_attrs(self, study_id):
        raise NotImplementedError

    @override
    def get_study_system_attrs(self, study_id):
        raise NotImplementedError

    @override
    def get_all_studies(self):
        raise NotImplementedError

    @override
    def create_new_trial(self, study_id, template_trial=None):
        assert template_trial is None
        response = self._sent_request(
            "POST", f"study/{study_id}", None, OptunaTrialCreation
        )
        return response.trial_id

    @override
    def set_trial_param(self, trial_id, param_name, param_value_internal, distribution):
        self._sent_request(
            "POST",
            f"trial/{trial_id}/trial-param",
            OptunaSetParam(
                name=param_name,
                value=param_value_internal,
                distribution=optuna.distributions.distribution_to_json(distribution),
            ),
            None,
        )

    @override
    def set_trial_state_values(self, trial_id, state, values=None):
        try:
            result = self._sent_request(
                "POST",
                f"trial/{trial_id}",
                OptunaSetValue(state=state, value=values),
                OptunaSetValueResponse,
            )
            return result.did_update
        except:  # noqa: E722
            return False

    @override
    def set_trial_intermediate_value(self, trial_id, step, intermediate_value):
        raise NotImplementedError

    @override
    def set_trial_user_attr(self, trial_id, key, value):
        raise NotImplementedError

    @override
    def set_trial_system_attr(self, trial_id, key, value):
        raise NotImplementedError

    @override
    def get_trial(self, trial_id):
        response = self._sent_request("GET", f"trial/{trial_id}", None, OptunaTrial)
        return response.to_native()

    @override
    def get_all_trials(self, study_id, deepcopy=True, states=None):
        response = self._sent_request(
            "GET", f"study/{study_id}/trials", None, OptunaGetAllTrials
        )
        return [trial.to_native() for trial in response.trials]
