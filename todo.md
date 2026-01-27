# SmartShot AI TODO

## 第一阶段：Webots 仿真开发
- [ ] 搭建 Webots 世界：球场、2 米支架、随机移动足球
- [ ] 编写控制器：初始化 Camera、Yaw/Pitch 电机与 PID 追踪
- [ ] 加入控制“死区”与平滑逻辑，降低启停抖动
- [ ] 自动发球与调参：随机高速弹出、统计追踪成功率与抖动指标
- [ ] 网格搜索 P/I/D 参数，输出最稳定组合
- [ ] 数据集导出：保存帧图与标签（球 bbox/遮挡标记）至 sim_data/YYYYMMDD
- [ ] 视觉预热：集成 YOLOv8-Nano（量化），评估仿真帧识别率
- [ ] 指标与日志：记录物理延迟（目标 < 5px）、丢球点、抖动曲线

## 第二阶段：硬件采购与组装
- [ ] 采购清单：Pi Zero 2W、DS3218 双轴云台、160° CSI、三脚架、移动电源、配重袋
- [ ] 2 米高度物理组装与配重平衡，线缆管理
- [ ] 环境初始化脚本：更新国内镜像源、安装 OpenCV/Ultralytics/GPIO 库、关闭代理
- [ ] 舵机校准：角度范围、PWM 映射、限速与死区验证
- [ ] 供电与安全：过载防护、自检日志、长时稳定性测试

## 第三阶段：代码迁移与实战测试
- [ ] 迁移 PID 与控制逻辑到 GPIO 代码；读取 config/pid.yaml
- [ ] 视频回放测试：对着转播画面跑自动化脚本，记录追踪指标
- [ ] 球场实测：记录丢球点并完成最后参数微调
- [ ] 鲁棒性策略：输入熔断（>100px）、DPI 补偿、低光下球员密集区优先

## 规则与合规
- [ ] 遵循 Sports-Tracker-Env：NPM 使用 `https://registry.npmmirror.com` 与 `--no-proxy`；GPIO/系统路径失败先提示 sudo
- [ ] 遵循 Sports-Tracker-Physics：增量追踪与平滑审核；`devicePixelRatio` 补偿；输入熔断
- [ ] 遵循 Sports-Tracker-Autopilot：Zero-Touch；用 Timer/信号替代人工阻塞；输出代码审计报告与延迟指标
- [ ] 配置管理：统一维护 config/pid.yaml、config/control.yaml

## 交付物
- [ ] 仿真控制器脚本（sim/controllers/tracker）
- [ ] PID 自动调参脚本与最优参数报告（sim/controllers/pid_tuner）
- [ ] 数据集与标签（sim/utils/dataset_export 与 sim_data）
- [ ] 树莓派环境脚本（raspi/setup/pi_setup.sh）
- [ ] GPIO 舵机驱动封装（raspi/gpio/servo_controller.py）
- [ ] 实测日志与最终参数（logs/ 与 config/pid.yaml）
