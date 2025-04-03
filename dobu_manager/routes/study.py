import importlib
import json
import os
import pathlib
import shutil
import sys
from typing import Annotated

from fastapi import File, Form, HTTPException, UploadFile
from loguru import logger
from pydantic import BaseModel
from dobu_manager.app import app
from dobu_manager.services.study_service import StudyService
import zipfile
from inspect import signature

from shared.models.study import CreateStudy, Study

class KoduConfig(BaseModel):
    objective_function: str
    objective_file: str

@app.post("/study/test")
async def test_study(
    study_name: Annotated[str, Form()], 
    data: Annotated[UploadFile, File()]
) -> KoduConfig:
    study_service = StudyService.get()
    if study_service.get_by_name(study_name) is not None:
        raise HTTPException(400, detail="Study already exists")
    
    study_dir = study_service.study_directory.joinpath(study_name)
    if study_dir.exists():
        shutil.rmtree(study_dir)
    study_dir.mkdir(parents=True)
    
        
    with zipfile.ZipFile(data.file, 'r') as zip:
        size = sum([zip_info.file_size for zip_info in zip.filelist])
        logger.info(f"Extracting code-base [{(size / 10e6):.2f} MB]to {study_dir}")
        filename = pathlib.Path(data.filename).with_suffix('').name
        zip.extractall(study_dir)
        shutil.rmtree(study_dir.joinpath("__MACOSX"))
        for item in study_dir.joinpath(filename).iterdir():
            shutil.move(item, study_dir)
        shutil.rmtree(study_dir.joinpath(filename))
        
    
    config_file = study_dir.joinpath('kodu-optim.json')
    if not config_file.exists():
        raise HTTPException(400, detail="Codebase does not contain the required kodu-optim.yaml")

    with open(config_file, 'r') as f:
        config = KoduConfig.model_validate(json.loads(f.read()))
    
    try:
        sys.path.insert(0, study_dir)
        module = importlib.import_module(f".{config.objective_file.replace(".py", '')}", package='.'.join(study_dir.relative_to(os.getcwd()).parts))

        if not hasattr(module, config.objective_function):
            raise HTTPException(400, detail="Objective Function not found")
        module_objective_function = getattr(module, config.objective_function)
        sig = signature(module_objective_function)
        arg_count = len(sig.parameters)
        logger.info(f"Objective function '{config.objective_function}' has {arg_count} arguments.")
        if arg_count > 1 :
            raise HTTPException(400, detail="Objective Function contains too many arguments")
        sys.path.pop(0)
    except ImportError as e:
        logger.error(f"The objective function could not be imported: {e.msg}")
        raise HTTPException(400, detail="Objective file is not importable")
    return config
    
@app.post("/study")
async def create_study(data: CreateStudy) -> Study:
    study_service = StudyService.get()
    
    if study_service.get_by_name(data.name) is not None:
        raise HTTPException(400, detail="study with that name already exists")
    
    study_dir = study_service.study_directory.joinpath(data.name)
    if not study_dir.exists() or len(os.listdir(study_dir)) < 0:
        raise HTTPException(404, detail="The study directory could not be found, have you already posted to '/study/test?'")
    
    return study_service.create_study(data)

@app.get("/study/request")
async def request_study() -> Study:
    study_service = StudyService.get()
    selected = study_service.select_study()
    if selected is None:
        raise HTTPException(404, detail="No eligible studies available")
    return selected

@app.get("/study/{name}")
async def get_by_name(name: str) -> Study:
    study_service = StudyService.get()
    result = study_service.get_by_name(name)
    if result is None:
        raise HTTPException(404, detail="Study with name does not exists")
    return result

@app.get("/study")
async def get_all() -> list[Study]:
    study_service = StudyService.get()
    return study_service.get_all()

@app.put("/study/{name}/activate")
async def activate_study(name: str) -> Study:
    study_service = StudyService.get()
    result = study_service.get_by_name(name)
    if result is None:
        raise HTTPException(404, detail="Study with name does not exists")
    return study_service.activate(name)

@app.put("/study/{name}/pause")
async def pause_study(name: str) -> Study:
    study_service = StudyService.get()
    result = study_service.get_by_name(name)
    if result is None:
        raise HTTPException(404, detail="Study with name does not exists")
    return study_service.pause(name)

