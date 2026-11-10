"""Đo các thông số chuyển động từ khung hình preview pv/NNNN.png (480x270)."""
import glob, sys
import numpy as np
from PIL import Image
FPS = 29.961
fs = sorted(glob.glob(sys.argv[1] + "/*.png"))

def load(i):
    return np.asarray(Image.open(fs[i]).convert("RGB")).astype(int)

def bbox(mask):
    ys, xs = np.nonzero(mask)
    if len(xs) < 30:
        return None
    return xs.min(), xs.max(), ys.min(), ys.max()

mode = sys.argv[2]
a, b = int(sys.argv[3]), int(sys.argv[4])
for i in range(a, b):
    im = load(i)
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    t = i / FPS
    if mode == "band":
        rows = np.nonzero(im.mean((1, 2)) > 12)[0]
        print(f"{i} {t:.3f} band {rows.min() if len(rows) else -1}-{rows.max() if len(rows) else -1} h={len(rows)/270:.3f}")
    elif mode == "text":
        m = (R > 190) & (G > 165) & (B < 150) & (R > G + 10) & (G > B + 60)
        bb = bbox(m)
        if bb:
            x0, x1, y0, y1 = bb
            print(f"{i} {t:.3f} text x{x0}-{x1} w={(x1-x0)/480:.3f} y{y0}-{y1} h={(y1-y0)/270:.3f} n={m.sum()}")
        else:
            print(f"{i} {t:.3f} text none")
    elif mode == "pip":
        bg = im[3:12, 3:12].reshape(-1, 3).mean(0)
        m = np.abs(im - bg).max(2) > 45
        m[:, :6] = m[:, -6:] = False
        bb = bbox(m)
        if bb:
            x0, x1, y0, y1 = bb
            print(f"{i} {t:.3f} pip w={(x1-x0)/480:.3f} h={(y1-y0)/270:.3f} cx={(x0+x1)/960:.3f} cy={(y0+y1)/540:.3f} bg={bg.astype(int)} in={im[135,240]}")
        else:
            print(f"{i} {t:.3f} pip none bg={bg.astype(int)}")
