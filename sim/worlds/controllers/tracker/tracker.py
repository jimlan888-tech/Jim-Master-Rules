import os
import time
import importlib
import main as _main


def _stamp():
    base = os.path.dirname(__file__)
    s = 0
    try:
        for f in os.listdir(base):
            if f.endswith(".py"):
                p = os.path.join(base, f)
                s ^= int(os.path.getmtime(p))
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        cfg_pid = os.path.join(root, "config", "pid.yaml")
        cfg_ctl = os.path.join(root, "config", "control.yaml")
        if os.path.exists(cfg_pid):
            s ^= int(os.path.getmtime(cfg_pid))
        if os.path.exists(cfg_ctl):
            s ^= int(os.path.getmtime(cfg_ctl))
    except Exception:
        pass
    return s


def _root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


def _logs():
    d = os.path.join(_root(), "logs")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass
    return d


def _write_pid(kp, ki, kd, deadzone=3.0):
    import yaml
    cfg = {
        "yaw": {"kp": float(kp), "ki": float(ki), "kd": float(kd)},
        "pitch": {"kp": float(kp), "ki": float(ki), "kd": float(kd)},
        "deadzone": float(deadzone),
    }
    try:
        with open(os.path.join(_root(), "config", "pid.yaml"), "w", encoding="utf-8") as f:
            yaml.safe_dump(cfg, f, allow_unicode=True)
    except Exception:
        pass


def _read_metrics():
    import csv
    p = os.path.join(_logs(), "tracker_metrics.csv")
    if not os.path.exists(p):
        return []
    rows = []
    try:
        with open(p, "r", encoding="utf-8") as f:
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
    except Exception:
        return []
    return rows


def _eval(rows, ts_ms=20):
    if not rows:
        return None
    errs = [x[1] for x in rows]
    avgs = [x[2] for x in rows]
    avg_err = sum(errs) / max(1, len(errs))
    max_lag = max(avgs) if avgs else 0.0
    frames_10s = int(10000 / ts_ms)
    tail = avgs[-frames_10s:] if len(avgs) >= frames_10s else avgs
    stable_ok = (sum(tail) / max(1, len(tail))) < 2.0 if tail else False
    return avg_err, max_lag, stable_ok


def _tune():
    import csv
    import yaml
    import importlib
    sets = [
        1.0,
        2.0,
        5.0,
        8.0,
        10.0,
    ]
    report = os.path.join(_logs(), "tuning_report.csv")
    best = None
    try:
        base_cfg = {"yaw": {"ki": 0.01, "kd": 0.04}, "pitch": {"ki": 0.01, "kd": 0.04}, "deadzone": 3.0}
        try:
            with open(os.path.join(_root(), "config", "pid.yaml"), "r", encoding="utf-8") as f:
                cur = yaml.safe_load(f)
                base_cfg["yaw"]["ki"] = float(cur["yaw"]["ki"])
                base_cfg["yaw"]["kd"] = float(cur["yaw"]["kd"])
                base_cfg["pitch"]["ki"] = float(cur["pitch"]["ki"])
                base_cfg["pitch"]["kd"] = float(cur["pitch"]["kd"])
                base_cfg["deadzone"] = float(cur.get("deadzone", 3.0))
        except Exception:
            pass
        with open(report, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["kp", "ki", "kd", "avg_err", "max_lag", "success"])
            for kp in sets:
                _write_pid(kp, base_cfg["yaw"]["ki"], base_cfg["yaw"]["kd"], base_cfg["deadzone"])
                _main = importlib.reload(_main)
                _main.run(None, max_seconds=60)
                rows = _read_metrics()
                metrics = _eval(rows)
                if metrics is None:
                    w.writerow([kp, base_cfg["yaw"]["ki"], base_cfg["yaw"]["kd"], "NA", "NA", False])
                    continue
                avg_err, max_lag, ok = metrics
                rmse = (sum([r[1] * r[1] for r in rows]) / max(1, len(rows))) ** 0.5
                w.writerow([kp, base_cfg["yaw"]["ki"], base_cfg["yaw"]["kd"], f"{rmse:.3f}", f"{max_lag:.3f}", ok])
                if best is None or rmse < best[3] or (abs(rmse - best[3]) < 1e-6 and max_lag < best[4]):
                    best = (kp, base_cfg["yaw"]["ki"], base_cfg["yaw"]["kd"], rmse, max_lag, ok)
    except Exception:
        pass
    if best:
        print(f"测试结束，最优参数为 P={best[0]}, I={best[1]}, D={best[2]}，平均对齐误差为 {best[3]:.3f} px")
        print(f"lag<5px 要求：{'YES' if best[4] < 5.0 else 'NO'}")
    else:
        print("No valid results collected.")


if __name__ == "__main__":
    last = _stamp()
    try:
        _tune()
    except Exception:
        pass
    while True:
        def _should_reload():
            return _stamp() != last
        _main.run(_should_reload)
        _main = importlib.reload(_main)
        last = _stamp()
