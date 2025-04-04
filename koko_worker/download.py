from pathlib import Path
import shutil
from loguru import logger
import zipfile

from koko_worker.requests import request_file


class DownloadService:
    def __init__(self, data_dir: Path):
        self.studies_dir = data_dir.joinpath('studies')
        self.studies_dir.mkdir(parents=True, exist_ok=True)
        
    def is_study_cached(self, name: str) -> bool:
        return self.studies_dir.joinpath(name).exists()
    
    async def download_study(self, name: str) -> None:
        study_dir = self.studies_dir.joinpath(name)
        study_dir.mkdir(parents=True, exist_ok=False)
        file = study_dir.joinpath('data.zip')
        with open(file, 'wb') as f:
            await request_file(f"study/{name}/download", "GET",None, f)
            logger.info("Finished downloading")
            
        with zipfile.ZipFile(file, 'r') as zip:
            logger.info("Inflating zip")
            zip.extractall(study_dir)
            shutil.rmtree(study_dir.joinpath("__MACOSX"))
            code_base_dir = [dir for dir in study_dir.iterdir() if dir.is_dir()][0]
            for item in code_base_dir.iterdir():
                shutil.move(item, study_dir)
            shutil.rmtree(code_base_dir)
            logger.info("Finished inflating")