from typing import Annotated

from fastapi import File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from dobu_manager.app import app
from dobu_manager.services.codebase_service import KoduConfig, check_codebase
from dobu_manager.services.study_service import (
    activate_study,
    does_study_exists,
    get_all_studies,
    get_study_by_name,
    get_study_codebase_zip,
    insert_study,
    is_codebase_present,
    pause_study,
    select_single_study,
    store_codebase_zip,
)
from dobu_manager.services.zip_service import extract_zip
from shared.models.study import CodeBaseStudy, CreateStudy


@app.post("/study/test")
async def test_study(
    study_name: Annotated[str, Form()], data: Annotated[UploadFile, File()]
) -> KoduConfig:
    if not study_name.isalnum():
        raise HTTPException(400, detail="study name must be alpha numeric")

    if does_study_exists(study_name):
        raise HTTPException(400, detail="Study already exists")

    zip_path = store_codebase_zip(study_name, data)
    study_dir = extract_zip(zip_path)
    code_base_state, config = check_codebase(study_dir)
    if code_base_state != "ok":
        raise HTTPException(400, detail=code_base_state)

    return config


@app.post("/study")
async def handle_create_study(data: CreateStudy) -> CodeBaseStudy:
    if does_study_exists(data.name):
        raise HTTPException(400, detail="study with that name already exists")

    if not is_codebase_present(data.name):
        raise HTTPException(
            404,
            detail="The study directory could not be found, have you already posted to '/study/test?'",
        )

    return insert_study(data)


@app.get("/study/request")
async def handle_request_study() -> CodeBaseStudy:
    selected = select_single_study()
    if selected is None:
        raise HTTPException(404, detail="No eligible studies available")
    return selected


@app.get("/study/{name}")
async def handle_get_study_by_name(name: str) -> CodeBaseStudy:
    result = get_study_by_name(name)
    if result is None:
        raise HTTPException(404, detail="Study with name does not exists")
    return result


@app.get("/study")
async def handle_get_all_studies() -> list[CodeBaseStudy]:
    return get_all_studies()


@app.put("/study/{name}/activate")
async def handle_activate_study(name: str) -> CodeBaseStudy:
    if not does_study_exists(name):
        raise HTTPException(404, detail="Study with name does not exists")
    return activate_study(name)


@app.put("/study/{name}/pause")
async def handle_pause_study(name: str) -> CodeBaseStudy:
    if not does_study_exists(name):
        raise HTTPException(404, detail="Study with name does not exists")
    return pause_study(name)


@app.get("/study/{name}/download")
async def download_study(name: str):
    if not does_study_exists(name):
        raise HTTPException(404, detail="Study with name does not exists")
    zip_file = get_study_codebase_zip(name)
    return FileResponse(
        zip_file, media_type="application/octet-stream", filename="data.zip"
    )
