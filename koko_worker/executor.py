import argparse
import importlib
import logging
import os
import sys
from pathlib import Path

import optuna

logger = logging.getLogger("[EXECUTOR]")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def main(objective_function: str, objective_file: str, study_name: str, storage: str):
    project_dir = Path(os.getcwd())
    logger.info(
        f"Looking for {objective_function} in {objective_file} at {project_dir.as_posix()}"
    )

    if project_dir not in sys.path:
        logger.info(f"Adding {project_dir.as_posix()} to sys.path")
        sys.path.insert(0, project_dir.as_posix())

    module = importlib.import_module(name="hello")
    logger.info(f"Successfully import module {module.__name__} from {objective_file}")
    logger.info(
        f"The imported module has the following attributes {[key for key in module.__dict__.keys() if key not in ['__name__', '__doc__', '__package__', '__loader__', '__spec__', '__file__', '__cached__', '__builtins__']]}"
    )

    objective = getattr(module, objective_function)

    logger.info("Successfully imported the object function")
    logger.info("Loading study from optuna")
    study = optuna.load_study(study_name=study_name, storage=storage)

    logger.info(f"Creating trial for study {study_name}")
    study.optimize(func=objective, n_trials=1, n_jobs=1, gc_after_trial=True)
    logger.info("Finished trial")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--objective-file", type=str, required=True)
    parser.add_argument("--objective-function", type=str, required=True)
    parser.add_argument("--storage", type=str, required=True)
    parser.add_argument("--study-name", type=str, required=True)

    args = parser.parse_args()
    logger.info("Starting Executor")
    main(
        objective_file=args.objective_file,
        objective_function=args.objective_function,
        storage=args.storage,
        study_name=args.study_name,
    )
