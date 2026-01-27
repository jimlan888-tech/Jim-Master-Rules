import os
import math
import csv
import yaml
from controller import Supervisor
from controller import Camera
from controller import Motor
try:
    import numpy as np
    import cv2
except Exception:
    np = None
    cv2 = None


class PID:
    def __init__(self, kp, ki, kd, deadzone=0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.deadzone = deadzone
        self.i = 0.0
        self.prev = 0.0

    def update(self, error, dt):
        if abs(error) < self.deadzone:
            error = 0.0
        self.i += error * dt
        d = (error - self.prev) / dt if dt > 0 else 0.0
        self.prev = error
        return self.kp * error + self.ki * self.i + self.kd * d


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def load_config():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    cfg_dir = os.path.join(root, "config")
    with open(os.path.join(cfg_dir, "pid.yaml"), "r", encoding="utf-8") as f:
        pid_cfg = yaml.safe_load(f)
    with open(os.path.join(cfg_dir, "control.yaml"), "r", encoding="utf-8") as f:
        ctl_cfg = yaml.safe_load(f)
    return pid_cfg, ctl_cfg, os.path.join(root, "logs")


def run(should_reload=None, max_seconds=None):
    pid_cfg, ctl_cfg, logs_dir = load_config()
    robot = Supervisor()
    ts = 20
    cam = robot.getDevice("camera")
    yaw = robot.getDevice("yaw_motor")
    pitch = robot.getDevice("pitch_motor")
    cam.enable(ts)
    try:
        cam.recognitionEnable(ts)
    except Exception:
        pass
    yaw.setPosition(float("inf"))
    pitch.setPosition(float("inf"))
    yaw.setVelocity(0.0)
    pitch.setVelocity(0.0)
    ball = robot.getFromDef("BALL")
    cam_node = robot.getFromDef("CAM")
    ball_field = None
    ball_orig = None
    ball_x = 0.0
    ball_dir = 1.0
    ball_left = -1.0
    ball_right = 1.0
    if ball:
        try:
            ball_field = ball.getField("translation")
            ball_orig = ball_field.getSFVec3f()
            ball_x = float(ball_orig[0])
            ball_left = ball_x - 1.0
            ball_right = ball_x + 1.0
        except Exception:
            ball_field = None
    w = cam.getWidth()
    h = cam.getHeight()
    cxf = w * 0.5
    cyf = h * 0.5
    yaw_pid = PID(pid_cfg["yaw"]["kp"], pid_cfg["yaw"]["ki"], pid_cfg["yaw"]["kd"], pid_cfg.get("deadzone", 0.0))
    pitch_pid = PID(pid_cfg["pitch"]["kp"], pid_cfg["pitch"]["ki"], pid_cfg["pitch"]["kd"], pid_cfg.get("deadzone", 0.0))
    max_speed = float(ctl_cfg["servo"]["max_speed"])
    min_angle = float(ctl_cfg["servo"]["min_angle"])
    max_angle = float(ctl_cfg["servo"]["max_angle"])
    yaw_angle = 0.0
    pitch_angle = 0.0
    prev_ex = 0.0
    prev_ey = 0.0
    fuse = 100.0
    os.makedirs(logs_dir, exist_ok=True)
    out_file = os.path.join(logs_dir, "tracker_metrics.csv")
    dyn_file = os.path.join(logs_dir, "dynamic_test_1.csv")
    step_count = 0
    wf = open(out_file, "w", newline="", encoding="utf-8")
    wlog = csv.writer(wf)
    wlog.writerow(["step", "err", "yaw_delta", "pitch_delta", "success", "avg_err_50", "lag_ok"])
    df = open(dyn_file, "w", newline="", encoding="utf-8")
    dlog = csv.writer(df)
    dlog.writerow(["step", "err_px"])
    mon_file = os.path.join(logs_dir, "monitoring.txt")
    last_lag = -1
    recent = []
    t0 = robot.getTime()
    while robot.step(ts) != -1:
        if should_reload and should_reload():
            break
        if max_seconds is not None:
            if (robot.getTime() - t0) >= max_seconds:
                break
        dt = ts / 1000.0
        if ball_field is not None and ball_orig is not None:
            ball_x += 1.0 * dt * ball_dir
            if ball_x > ball_right:
                ball_x = ball_right
                ball_dir = -1.0
            elif ball_x < ball_left:
                ball_x = ball_left
                ball_dir = 1.0
            try:
                ball_field.setSFVec3f([ball_x, ball_orig[1], ball_orig[2]])
                ball.resetPhysics()
            except Exception:
                pass
        cx = cxf
        cy = cyf
        try:
            objs = cam.getRecognitionObjects()
            if objs and len(objs) > 0:
                best = max(objs, key=lambda o: o.size[0] * o.size[1] if hasattr(o, "size") else 0.0)
                cx = best.position_on_image[0]
                cy = best.position_on_image[1]
            else:
                img = cam.getImage()
                sx = 8
                sy = 8
                sumx = 0.0
                sumy = 0.0
                cnt = 0
                for y in range(0, h, sy):
                    for x in range(0, w, sx):
                        r = cam.imageGetRed(img, w, x, y)
                        g = cam.imageGetGreen(img, w, x, y)
                        b = cam.imageGetBlue(img, w, x, y)
                        if r + g + b > 600:
                            sumx += x
                            sumy += y
                            cnt += 1
                if cnt > 0:
                    cx = sumx / cnt
                    cy = sumy / cnt
        except Exception:
            pass
        img = cam.getImage()
        if cv2 is not None and np is not None and img is not None:
            arr = np.frombuffer(img, dtype=np.uint8).reshape((h, w, 4))
            bgr = arr[:, :, :3].copy()
            cx0 = int(cxf)
            cy0 = int(cyf)
            bx0 = int(cx)
            by0 = int(cy)
            try:
                if cam_node and ball:
                    bp = ball.getPosition()
                    cp = cam_node.getPosition()
                    R = cam_node.getOrientation()
                    dx = bp[0] - cp[0]
                    dy = bp[1] - cp[1]
                    dz = bp[2] - cp[2]
                    rx = R[0] * dx + R[3] * dy + R[6] * dz
                    ry = R[1] * dx + R[4] * dy + R[7] * dz
                    rz = R[2] * dx + R[5] * dy + R[8] * dz
                    fov = cam.getFov()
                    fx = w / (2.0 * math.tan(fov * 0.5))
                    vfov = 2.0 * math.atan(math.tan(fov * 0.5) * (h / max(1.0, w)))
                    fy = h / (2.0 * math.tan(vfov * 0.5))
                    if rz != 0.0:
                        bx0 = int(fx * (rx / rz) + cxf)
                        by0 = int(fy * (ry / rz) + cyf)
            except Exception:
                pass
            cv2.line(bgr, (cx0 - 10, cy0), (cx0 + 10, cy0), (0, 255, 0), 1)
            cv2.line(bgr, (cx0, cy0 - 10), (cx0, cy0 + 10), (0, 255, 0), 1)
            cv2.line(bgr, (bx0 - 10, by0), (bx0 + 10, by0), (0, 0, 255), 1)
            cv2.line(bgr, (bx0, by0 - 10), (bx0, by0 + 10), (0, 0, 255), 1)
            cv2.imshow("SmartShot Overlay", bgr)
            cv2.waitKey(1)
        ex = cx - cxf
        ey = cy - cyf
        if abs(ex - prev_ex) > fuse or abs(ey - prev_ey) > fuse:
            prev_ex = ex
            prev_ey = ey
            continue
        yaw_out = yaw_pid.update(ex, dt)
        pitch_out = pitch_pid.update(-ey, dt)
        new_yaw = clamp(yaw_angle + yaw_out * dt, math.radians(min_angle), math.radians(max_angle))
        new_pitch = clamp(pitch_angle + pitch_out * dt, math.radians(min_angle), math.radians(max_angle))
        yaw_delta = new_yaw - yaw_angle
        pitch_delta = new_pitch - pitch_angle
        yaw_angle = new_yaw
        pitch_angle = new_pitch
        yaw.setVelocity(clamp(abs(yaw_out), 0.0, max_speed))
        pitch.setVelocity(clamp(abs(pitch_out), 0.0, max_speed))
        yaw.setPosition(yaw_angle)
        pitch.setPosition(pitch_angle)
        prev_ex = ex
        prev_ey = ey
        err = math.hypot(ex, ey)
        try:
            dlog.writerow([step_count, err])
        except Exception:
            pass
        if err > 10.0:
            try:
                print("\033[31mDELAY ALERT: {:.2f}px\033[0m".format(err))
            except Exception:
                print("DELAY ALERT: {:.2f}px".format(err))
        success = 1 if err < 20.0 else 0
        recent.append(err)
        if len(recent) > 50:
            recent.pop(0)
        avg_err = sum(recent) / max(1, len(recent))
        lag_ok = 1 if avg_err < 5.0 else 0
        wlog.writerow([step_count, err, yaw_delta, pitch_delta, success, avg_err, lag_ok])
        if lag_ok != last_lag:
            with open(mon_file, "a", encoding="utf-8") as mf:
                mf.write(f"{step_count},{avg_err:.3f},{'OK' if lag_ok==1 else 'VIOLATION'}\n")
            last_lag = lag_ok
        step_count += 1
    try:
        wf.close()
    except Exception:
        pass
    try:
        df.close()
    except Exception:
        pass


if __name__ == "__main__":
    run()
