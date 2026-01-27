import random
from controller import Supervisor


def main():
    sup = Supervisor()
    ts = int(sup.getBasicTimeStep())
    width = 10.0
    height = 6.0
    while sup.step(ts) != -1:
        ball = sup.getFromDef("BALL")
        if ball is None:
            continue
        t = ball.getField("translation")
        p = t.getSFVec3f()
        if random.random() < 0.05:
            vx = random.uniform(-2.0, 2.0)
            vy = random.uniform(-1.5, 1.5)
            p[0] += vx * (ts / 1000.0)
            p[2] += vy * (ts / 1000.0)
        if p[0] < -width or p[0] > width:
            p[0] = max(-width, min(width, p[0]))
        if p[2] < -height or p[2] > height:
            p[2] = max(-height, min(height, p[2]))
        t.setSFVec3f(p)


if __name__ == "__main__":
    main()
