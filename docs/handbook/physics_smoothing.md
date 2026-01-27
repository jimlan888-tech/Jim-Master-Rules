# 物理平滑算法与测试手册

## 算法要点
- PID 更新：位置误差经 P/I/D 组合，采用增量更新云台角度，避免直接“跳转”。
- 死区控制：误差绝对值小于 deadzone 则视为 0，压制微抖动。
- 熔断阈值：单帧位移>100px 则忽略该帧更新，过滤识别瞬变与噪声。
- 限速与限位：速度限幅到 max_speed，角度限制在 [min_angle, max_angle]。
- 识别回退：优先 Recognition 对象；为空时进行简易颜色质心回退。

## 实现位置
- 控制器主逻辑：[main.py](file:///d:/Jim/AI_Trading/SmartShot%20AI/sim/worlds/controllers/tracker/main.py)
- 世界设备声明：[soccer_field.wbt](file:///d:/Jim/AI_Trading/SmartShot%20AI/sim/worlds/worlds/soccer_field.wbt#L19-L45)
- 配置参数：[pid.yaml](file:///d:/Jim/AI_Trading/SmartShot%20AI/config/pid.yaml)

## 指标与日志
- 帧级指标：err、yaw_delta、pitch_delta、success
- 延迟监控：滚动 50 帧平均误差 < 5px 视为 OK
- 输出文件：logs/tracker_metrics.csv、logs/monitoring.txt

## 测试机制
- 自动调参：运行 [pid_tuner](file:///d:/Jim/AI_Trading/SmartShot%20AI/sim/controllers/pid_tuner/main.py)，生成 logs/pid_tuning.csv 并写回最优 PID。
- 仿真运行：在 Webots 中加载 [soccer_field.wbt](file:///d:/Jim/AI_Trading/SmartShot%20AI/sim/worlds/worlds/soccer_field.wbt)，确保控制器路径为 sim/worlds/controllers/tracker。

## 常见问题
- 控制器未加载：检查目录为 sim/worlds/controllers/tracker，并确认世界文件 controller "tracker"。
- 识别报错：确认 Camera 具有 name 与 Recognition 子节点。
- 路径错误：Windows 环境下注意项目根解析，以世界文件所在目录的上级为“项目根”。
