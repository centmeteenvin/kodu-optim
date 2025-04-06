import ast
import json
import tomllib
from pathlib import Path
from typing import Literal

from packaging.requirements import Requirement
from pydantic import BaseModel, ValidationError


class KoduConfig(BaseModel):
    objective_function: str
    objective_file: str


type DependencyState = (
    Literal["pyproject.toml not found"]
    | Literal["optuna not found"]
    | Literal["invalid version"]
    | Literal["ok"]
)

type FunctionState = (
    Literal["Not present"]
    | Literal["Function Not found"]
    | Literal["Invalid Argument count"]
    | Literal["Invalid return"]
    | Literal["ok"]
)
type CodebaseState = (
    Literal["ok"] | Literal["invalid config"] | FunctionState | DependencyState
)


def check_codebase(path: Path) -> tuple[CodebaseState, KoduConfig | None]:
    config = check_config_file(path)
    if config is None:
        return "invalid config", None

    function_path = path / config.objective_file
    function_result = check_function(function_path, config.objective_function)
    if function_result != "ok":
        return function_result, config

    dependency_result = check_dependencies(path)
    if dependency_result != "ok":
        return dependency_result, config

    return "ok", config


def check_config_file(path: Path) -> KoduConfig | None:
    config_file = path / "kodu-optim.json"
    if not config_file.exists():
        return False

    with open(config_file, "r") as f:
        try:
            config = KoduConfig.model_validate(json.loads(f.read()))
            return config
        except ValidationError:
            return None


def check_function(function_path: Path, function_name) -> FunctionState:
    if not function_path.exists():
        return "Not present"

    with open(function_path, "r") as f:
        code = f.read()
        tree = ast.parse(code)
        functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        objective_functions = [
            function for function in functions if function.name == function_name
        ]
        if len(objective_functions) != 1:
            return "Function Not found"
        proposed_function = objective_functions[0]
        if len(proposed_function.args.args) != 1:
            return "Invalid Argument count"

        class ReturnVisitor(ast.NodeVisitor):
            def __init__(self):
                self.found_non_none = False

            def visit_Return(self, node):
                # Check if return value is not None
                if node.value is not None and not (
                    isinstance(node.value, ast.Constant) and node.value.value is None
                ):
                    self.found_non_none = True

        visitor = ReturnVisitor()
        visitor.visit(proposed_function)

        if not visitor.found_non_none:
            return "Invalid return"
        return "ok"


def check_dependencies(path: Path) -> DependencyState:
    project_definition_path = path / "pyproject.toml"
    if not project_definition_path.exists():
        return "pyproject.toml not found"

    with open(project_definition_path, "rb") as f:
        data = tomllib.load(f)

    dependencies: list[str] = data.get("project", {}).get("dependencies", [])
    for dep in dependencies:
        try:
            req = Requirement(dep)
            if req.name == "kodu-optim" or "kodu_optim":
                optuna_specifier = req.specifier
                break
        except Exception:
            continue
    else:
        return "kodu-optim not found"

    return "ok" if optuna_specifier.contains("0.1.0") else "invalid version"
