import os
import csv
import time
import random
import math
import yaml


def simulate(kp, ki, kd, deadzone, max_speed, min_angle, max_angle, steps, ts, width, height):
    cx = width * 0.5
    cy = height * 0.5
    bx = random.uniform(0, width)
    by = random.uniform(0, height)
    bvx = random.uniform(-200, 200)
    bvy = random.uniform(-150, 150)
    yaw_i = 0.0
    pitch_i = 0.0
    yaw_prev = 0.0
    pitch_prev = 0.0
    yaw_angle = 0.0
    pitch_angle = 0.0
    fuse = 100.0
    success = 0
    total_err = 0.0
    total_jitter = 0.0
    last_ex = 0.0
    last_ey = 0.0
    for _ in range(steps):
        if random.random() < 0.05:
            bvx = random.uniform(-400, 400)
            bvy = random.uniform(-300, 300)
        bx += bvx * (ts / 1000.0)
        by += bvy * (ts / 1000.0)
        if bx < 0 or bx > width:
            bvx *= -1
            bx = max(0, min(width, bx))
        if by < 0 or by > height:
            bvy *= -1
            by = max(0, min(height, by))
        if random.random() < 0.1:
            ox = cx
            oy = cy
        else:
            ox = bx
            oy = by
        ex = ox - cx
        ey = oy - cy
        if abs(ex - last_ex) > fuse or abs(ey - last_ey) > fuse:
            last_ex = ex
            last_ey = ey
            continue
        if abs(ex) < deadzone:
            ex = 0.0
        if abs(ey) < deadzone:
            ey = 0.0
        yaw_i += ex * (ts / 1000.0)
        pitch_i += (-ey) * (ts / 1000.0)
        yaw_d = (ex - yaw_prev) / (ts / 1000.0)
        pitch_d = ((-ey) - pitch_prev) / (ts / 1000.0)
        yaw_prev = ex
        pitch_prev = -ey
        yaw_out = kp * ex + ki * yaw_i + kd * yaw_d
        pitch_out = kp * (-ey) + ki * pitch_i + kd * pitch_d
        yaw_delta = max(-max_speed, min(max_speed, yaw_out)) * (ts / 1000.0)
        pitch_delta = max(-max_speed, min(max_speed, pitch_out)) * (ts / 1000.0)
        yaw_angle = max(math.radians(min_angle), min(math.radians(max_angle), yaw_angle + yaw_delta))
        pitch_angle = max(math.radians(min_angle), min(math.radians(max_angle), pitch_angle + pitch_delta))
        total_jitter += abs(yaw_delta) + abs(pitch_delta)
        err = math.hypot(ex, ey)
        total_err += err
        if err < 20.0:
            success += 1
        last_ex = ex
        last_ey = ey
    rate = success / max(1, steps)
    jitter = total_jitter / max(1, steps)
    delay = total_err / max(1, steps)
    score = rate - 0.01 * jitter - 0.001 * delay
    return rate, jitter, delay, score


def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "pid_tuning.csv")
    cfg_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "config")
    with open(os.path.join(cfg_dir, "pid.yaml"), "r", encoding="utf-8") as f:
        pid_cfg = yaml.safe_load(f)
    with open(os.path.join(cfg_dir, "control.yaml"), "r", encoding="utf-8") as f:
        ctl_cfg = yaml.safe_load(f)
    deadzone = float(pid_cfg.get("deadzone", 0.0))
    max_speed = float(ctl_cfg["servo"]["max_speed"])
    min_angle = float(ctl_cfg["servo"]["min_angle"])
    max_angle = float(ctl_cfg["servo"]["max_angle"])
    grid_p = [0.2, 0.4, 0.6, 0.8]
    grid_i = [0.0, 0.01, 0.02]
    grid_d = [0.0, 0.02, 0.04, 0.06]
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kp", "ki", "kd", "rate", "jitter", "delay", "score"])
        best = None
        for kp in grid_p:
            for ki in grid_i:
                for kd in grid_d:
                    rate, jitter, delay, score = simulate(kp, ki, kd, deadzone, max_speed, min_angle, max_angle, steps=1000, ts=20, width=640, height=480)
                    w.writerow([kp, ki, kd, rate, jitter, delay, score])
                    if best is None or score > best[6]:
                        best = [kp, ki, kd, rate, jitter, delay, score]
    if best:
        new_cfg = {
            "yaw": {"kp": float(best[0]), "ki": float(best[1]), "kd": float(best[2])},
            "pitch": {"kp": float(best[0]), "ki": float(best[1]), "kd": float(best[2])},
            "deadzone": deadzone,
        }
        with open(os.path.join(cfg_dir, "pid.yaml"), "w", encoding="utf-8") as f:
            yaml.safe_dump(new_cfg, f, allow_unicode=True)
    print(out_file)


if __name__ == "__main__":
    main()
