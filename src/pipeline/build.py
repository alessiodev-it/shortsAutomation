from src.pipeline.utils.of_build.download import downloadVideo
from src.pipeline.utils.of_build.crop import apply_verticalCrop
from src.pipeline.utils.of_build.effects import apply_genericEffects
from src.pipeline.utils.of_build.thumbnail import generate_thumbnail
from pathlib import Path
import shutil

def clip(log, url: str, stagingDIR, outputDIR):
    log("Cleaning folders")
    _clearFolders([stagingDIR])

    log("Building clip...")

    input_filepath = downloadVideo(url, stagingDIR) # filename: downloaded
    log(f"Input file=\n{input_filepath}\n")

    if not input_filepath:
        log(f"Invalid input file")
        return None

    processed = input_filepath

    processed = apply_verticalCrop(processed, stagingDIR) # filename: cropped
    log(f"Processed file after crop=\n{processed}\n")

    output_filepath = apply_genericEffects(processed, stagingDIR) # filename: effects
    log(f"Processed file after effects=\n{output_filepath}\n")

    thumbnail_filepath = generate_thumbnail(output_filepath, outputDIR, log)
    log(f"Thumbnail created: {thumbnail_filepath}\n")

    log(f"Output file will be=\n{output_filepath}\n{thumbnail_filepath}\n")
    return output_filepath, thumbnail_filepath # filename: effects, thumbnail


def _clearFolders(folders: list):
    for folder in folders:
        for item in folder.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
