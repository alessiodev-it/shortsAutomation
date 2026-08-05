from pathlib import Path
import numpy as np
import cv2

def generate_thumbnail(input_video, output_dir, log):
    log(f"Creating thumbnail for this video:\n{input_video}\n")

    if output_dir is None:
        output_dir = input_video.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    thumbnail_path = output_dir / f"thumbnail.png"

    cap = cv2.VideoCapture(str(input_video))

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    start_frame = int(total_frames * 0.15)
    end_frame = int(total_frames * 0.90)

    sample_interval = int(fps * 0.3)
    if sample_interval < 1:
        sample_interval = 1

    best_score = -1
    best_frame = None
    prev_gray = None
    frame_count = 0

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    for frame_idx in range(start_frame, end_frame, sample_interval):
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            motion = np.sum(np.abs(gray.astype(float) - prev_gray.astype(float)))
            motion = motion / (gray.shape[0] * gray.shape[1])
        else:
            motion = 0

        prev_gray = gray.copy()
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = gray.mean()
        contrast = gray.std()

        if brightness < 30 or brightness > 225:
            continue

        if contrast < 20:
            continue

        motion_score = motion * 0.45
        sharpness_score = laplacian_var * 0.35
        brightness_score = (brightness / 255.0) * contrast * 0.20

        total_score = motion_score + sharpness_score + brightness_score

        if total_score > best_score:
            best_score = total_score
            best_frame = frame.copy()
            best_frame_idx = frame_idx
            best_metrics = {
                'motion': motion,
                'sharpness': laplacian_var,
                'brightness': brightness,
                'contrast': contrast,
                'total_score': total_score
            }

    cap.release()

    if best_frame is None:
        raise ValueError("Nessun frame valido trovato per la thumbnail")

    cv2.imwrite(str(thumbnail_path), best_frame)
    return thumbnail_path
