# SmartShot AI

## 项目简介
- 足球比赛自动拍摄支架仿真与实战工程，包含云台 PID 追踪、自动调参与数据导出。

## 目录结构
- sim/worlds/worlds：Webots 世界文件与项目工程
- sim/worlds/controllers/tracker：Webots 控制器（tracker）
- sim/controllers/pid_tuner：PID 自动调参脚本
- config：统一 PID 与控制参数
- logs：运行时指标与监控输出
- docs：审计与手册文档

## 快速启动（Webots）
- 打开项目文件夹：选择 sim/worlds 作为项目根（需看到 worlds 与 controllers 同级）。
- 加载世界：打开 [soccer_field.wbt](file:///d:/Jim/AI_Trading/SmartShot%20AI/sim/worlds/worlds/soccer_field.wbt)。
- 控制器路径：确保目录 [tracker](file:///d:/Jim/AI_Trading/SmartShot%20AI/sim/worlds/controllers/tracker) 存在，世界文件 controller 为 "tracker"。
- 设备声明：Camera 已具有 name 与 Recognition 子节点。

## 调参与日志
- 自动调参：运行 [pid_tuner](file:///d:/Jim/AI_Trading/SmartShot%20AI/sim/controllers/pid_tuner/main.py) 生成 logs/pid_tuning.csv 并写回 [pid.yaml](file:///d:/Jim/AI_Trading/SmartShot%20AI/config/pid.yaml)。
- 运行指标：logs/tracker_metrics.csv 与 logs/monitoring.txt；延迟目标 < 5px。

## 故障排查
- 控制器被忽略：检查 controller "tracker" 与 controllers 目录位置是否为 sim/worlds/controllers。
- 识别调用报错：确认 Camera 节点包含 recognition 子节点且命名为 "camera"。
- Windows 路径：优先使用“打开项目文件夹”，将 sim/worlds 作为根，避免路径误判。

## 进一步阅读
- 审计报告：见 [docs/audit/2026-01-27.md](file:///d:/Jim/AI_Trading/SmartShot%20AI/docs/audit/2026-01-27.md)
- 平滑算法手册：见 [docs/handbook/physics_smoothing.md](file:///d:/Jim/AI_Trading/SmartShot%20AI/docs/handbook/physics_smoothing.md)
