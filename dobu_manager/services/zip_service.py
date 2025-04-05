import shutil
import zipfile
from pathlib import Path

from loguru import logger


def extract_zip(zip_path: Path) -> Path:
    target_dir = zip_path.parent
    with zipfile.ZipFile(zip_path, "r") as zip:
        size = sum([zip_info.file_size for zip_info in zip.filelist])
        logger.info(f"Extracting code-base [{(size / 10e6):.2f} MB] to {target_dir}")
        zip.extractall(target_dir)
        shutil.rmtree(target_dir / "__MACOSX")
        dir_of_interest = list([dir for dir in target_dir.iterdir() if dir.is_dir()])[0]

        for item in dir_of_interest.iterdir():
            shutil.move(item, target_dir)
        shutil.rmtree(dir_of_interest)

    return target_dir
