"""Đo tempo (BPM) và vị trí beat của file nhạc bằng ffmpeg + numpy (không cần librosa)."""
import subprocess

import numpy as np

SR, HOP, WIN = 22050, 256, 1024


def onset_envelope(path: str):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    frames = np.lib.stride_tricks.sliding_window_view(x, WIN)[::HOP]
    spec = np.abs(np.fft.rfft(frames * np.hanning(WIN), axis=1))
    flux = np.maximum(np.diff(np.log1p(spec), axis=0), 0).sum(1)
    return (flux - flux.mean()) / (flux.std() + 1e-9), SR / HOP


def detect(path: str, lo: float = 80, hi: float = 160):
    """Trả về (bpm, phase_giây): beat thứ n nằm ở phase + n * 60 / bpm."""
    env, fps = onset_envelope(path)
    t = np.arange(len(env)) / fps
    best = (-np.inf, 0.0, 0.0)
    # Quét thô rồi tinh: điểm = tổng năng lượng onset tại các beat dự đoán, thử mọi pha
    for step, center in ((0.5, None), (0.02, "refine")):
        grid = np.arange(lo, hi, step) if center is None else np.arange(best[1] - 1, best[1] + 1, step)
        for bpm in grid:
            period = 60.0 / bpm
            phases = np.arange(0, period, 1 / fps)
            idx = ((t[-1] - phases[:, None]) // period).astype(int).max()
            beats = phases[:, None] + np.arange(idx)[None, :] * period
            score = env[np.clip((beats * fps).round().astype(int), 0, len(env) - 1)].mean(1)
            k = int(score.argmax())
            if score[k] > best[0]:
                best = (score[k], float(bpm), float(phases[k]))
    return best[1], best[2]


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        bpm, phase = detect(p)
        print(f"{p}: {bpm:.2f} BPM, beat đầu tiên ở {phase:.3f}s")
