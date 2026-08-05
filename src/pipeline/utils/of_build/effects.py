from pathlib import Path
import subprocess

def apply_genericEffects(input_file: Path, stagingDIR: Path, pitch_ratio=1.05, crf=18, preset="veryfast"):
    output_file = stagingDIR / "effects.mp4"

    if not Path(input_file).exists():
        return None

    vf = [
        "setpts=PTS-STARTPTS",
        "eq=brightness=0.02:saturation=1.1"
    ]
    vf_str = ",".join(vf)
    af = f"asetrate=44100*{pitch_ratio},aresample=44100,atempo=1/{pitch_ratio}"

    cmd = [
        "ffmpeg", "-y",
        "-fflags", "+genpts",
        "-avoid_negative_ts", "make_zero",
        "-i", str(input_file),
        "-vf", vf_str,
        "-af", af,
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-profile:v", "high",
        "-level", "4.1",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_file)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        if not output_file.exists():
            return None

        return output_file
    except Exception as e:
        return None
