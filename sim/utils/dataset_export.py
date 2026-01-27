import os
import json
from datetime import datetime


def export(output_dir, frames, labels):
    day = datetime.now().strftime("%Y%m%d")
    base = os.path.join(output_dir, day)
    os.makedirs(os.path.join(base, "frames"), exist_ok=True)
    os.makedirs(os.path.join(base, "labels"), exist_ok=True)
    meta = {"count": len(frames)}
    with open(os.path.join(base, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)
    for i, frame in enumerate(frames):
        with open(os.path.join(base, "frames", f"{i:06d}.png"), "wb") as fp:
            fp.write(frame)
        with open(os.path.join(base, "labels", f"{i:06d}.json"), "w", encoding="utf-8") as fp:
            json.dump(labels[i], fp, ensure_ascii=False)
    return base
