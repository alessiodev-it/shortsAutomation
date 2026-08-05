from pathlib import Path
from typing import Optional
import subprocess, re, shutil

def apply_verticalCrop(processed: Path, stagingDIR: Path) -> Optional[Path]:
    output_filename = "cropped.mp4"
    output_path = stagingDIR / output_filename
    result_path = centerCrop(processed, output_path, 1080, 1920)
    return result_path

def find_ffmpeg():
    # Try to find ffmpeg in PATH
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path

    # Try common locations
    common_paths = [
        '/usr/bin/ffmpeg',
        '/usr/local/bin/ffmpeg',
        '/opt/homebrew/bin/ffmpeg',
        'ffmpeg'  # fallback
    ]

    for path in common_paths:
        if Path(path).exists():
            return path

    return 'ffmpeg'  # return default and hope for the best

def get_video_dimensions(input_video: Path) -> tuple[int, int]:
    ffmpeg_cmd = find_ffmpeg()

    cmd = [
        ffmpeg_cmd,
        '-i', str(input_video),
        '-hide_banner'
    ]
    # ffmpeg writes stream info to stderr
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Look for pattern like "Stream #0:0: Video: ... 1280x720"
    pattern = r'Stream.*Video.*?(\d{3,5})x(\d{3,5})'
    match = re.search(pattern, result.stderr)

    if match:
        width = int(match.group(1))
        height = int(match.group(2))
        return width, height
    else:
        raise ValueError("Could not parse video dimensions from ffmpeg output")

def centerCrop(input_video: Path, output_video: Path, target_width: int = 1080, target_height: int = 1920) -> Optional[Path]:
    try:
        if not input_video.exists():
            print(f"ERROR: Input video does not exist: {input_video}")
            return None

        ffmpeg_cmd = find_ffmpeg()
        print(f"Using ffmpeg at: {ffmpeg_cmd}")

        # Get actual video dimensions
        try:
            width, height = get_video_dimensions(input_video)
            print(f"Video dimensions: {width}x{height}, target: {target_width}x{target_height}")
        except Exception as e:
            print(f"ERROR: Could not get video dimensions: {e}")
            print(f"Attempting crop anyway with fallback filter...")
            # Fallback: just try the scale+crop filter without dimension check
            scale_filter = f"scale={target_width}:{target_height}:force_original_aspect_ratio=increase"
            crop_filter = f"crop={target_width}:{target_height}"
            vf = f"{scale_filter},{crop_filter}"
            width, height = 0, 0  # Unknown

        # Build filter based on dimensions
        if width > 0 and height > 0:
            if width < target_width or height < target_height:
                print(f"WARNING: Video ({width}x{height}) is smaller than target ({target_width}x{target_height}). Using scale+crop.")
                scale_filter = f"scale={target_width}:{target_height}:force_original_aspect_ratio=increase"
                crop_filter = f"crop={target_width}:{target_height}"
                vf = f"{scale_filter},{crop_filter}"
            else:
                # Center crop
                crop_filter = f"crop={target_width}:{target_height}:(in_w-{target_width})/2:(in_h-{target_height})/2"
                vf = crop_filter

        output_video.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            ffmpeg_cmd,
            '-i', str(input_video),
            '-vf', vf,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-map', '0:v:0',
            '-map', '0:a?',
            '-y',
            str(output_video)
        ]

        print(f"Running crop/scale operation...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"ERROR: ffmpeg crop failed with return code {result.returncode}")
            print(f"STDERR: {result.stderr[-500:]}")  # Last 500 chars
            return None

        if not output_video.exists():
            print(f"ERROR: Output video was not created: {output_video}")
            return None

        print(f"Crop successful: {output_video}")
        return output_video

    except Exception as e:
        print(f"ERROR: Unexpected error in centerCrop: {e}")
        import traceback
        traceback.print_exc()
        return None
