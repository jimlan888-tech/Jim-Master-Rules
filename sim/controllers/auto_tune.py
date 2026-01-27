import os
import time
import csv
import yaml


def project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def cfg_dir():
    return os.path.join(project_root(), "config")


def logs_dir():
    d = os.path.join(project_root(), "logs")
    os.makedirs(d, exist_ok=True)
    return d


def write_pid(kp, ki, kd, deadzone=3.0):
    cfg = {
        "yaw": {"kp": float(kp), "ki": float(ki), "kd": float(kd)},
        "pitch": {"kp": float(kp), "ki": float(ki), "kd": float(kd)},
        "deadzone": float(deadzone),
    }
    with open(os.path.join(cfg_dir(), "pid.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True)


def read_metrics():
    path = os.path.join(logs_dir(), "tracker_metrics.csv")
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.reader(f)
        header = next(r, None)
        for row in r:
            try:
                step = int(row[0])
                err = float(row[1])
                avg_err_50 = float(row[5])
                rows.append((step, err, avg_err_50))
            except Exception:
                continue
    return rows


def eval_run(rows, ts_ms=20):
    if not rows:
        return None
    errs = [x[1] for x in rows]
    avgs = [x[2] for x in rows]
    avg_err = sum(errs) / max(1, len(errs))
    max_lag = max(avgs) if avgs else 0.0
    # last 10 seconds window
    frames_10s = int(10000 / ts_ms)
    tail = avgs[-frames_10s:] if len(avgs) >= frames_10s else avgs
    stable_ok = (sum(tail) / max(1, len(tail))) < 2.0 if tail else False
    return avg_err, max_lag, stable_ok


def main():
    sets = [
        (0.4, 0.00, 0.02),
        (0.5, 0.01, 0.03),
        (0.6, 0.01, 0.04),
        (0.7, 0.02, 0.05),
        (0.8, 0.02, 0.06),
    ]
    report = os.path.join(logs_dir(), "tuning_report.csv")
    with open(report, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kp", "ki", "kd", "avg_err", "max_lag", "success"])
        best = None
        for kp, ki, kd in sets:
            write_pid(kp, ki, kd)
            time.sleep(32)  # allow hot reload and warmup
            start = time.time()
            # wait until about 30 seconds of data collected
            while time.time() - start < 30:
                time.sleep(2)
            rows = read_metrics()
            metrics = eval_run(rows)
            if metrics is None:
                w.writerow([kp, ki, kd, "NA", "NA", False])
                continue
            avg_err, max_lag, ok = metrics
            w.writerow([kp, ki, kd, f"{avg_err:.3f}", f"{max_lag:.3f}", ok])
            if best is None or avg_err < best[3] or (abs(avg_err - best[3]) < 1e-6 and max_lag < best[4]):
                best = (kp, ki, kd, avg_err, max_lag, ok)
    if best:
        print(f"BEST kp={best[0]}, ki={best[1]}, kd={best[2]}, avg_err={best[3]:.3f}, max_lag={best[4]:.3f}, success={best[5]}")
        print(f"lag<5px requirement: {'YES' if best[4] < 5.0 else 'NO'}")
    else:
        print("No valid results collected.")


if __name__ == "__main__":
    main()
