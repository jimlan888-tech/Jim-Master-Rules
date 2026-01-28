# GOOSE 运行规则（Windows / OpenRouter / Proxy）

## 核心必胜准则（5 条）
- 使用 OpenRouter 提供方：统一以 `provider=openrouter` 运行，并确保已设置 `OPENROUTER_API_KEY`（避免 401）。
- 限额控制以避免费用错误：默认将 `GOOSE_MAX_TOKENS=2000`（可按需临时提高，避免 402）。
- 代理稳定性：在 PowerShell 中设置并持久化 `HTTP_PROXY`、`HTTPS_PROXY`（如 `http://127.0.0.1:7897`），网络诊断用 `curl.exe -I https://openrouter.ai/api/v1/models`。
- 权限与配置写入：Roaming 配置不可写时，必须提醒以管理员权限覆盖（从 `%LOCALAPPDATA%\\Temp` 副本复制到 `%APPDATA%\\Block\\goose\\config\\config.yaml`）。
- 明确模型选择：模型需为 OpenRouter 支持的有效名称（如 `google/gemini-2.0-flash-001` 或 `moonshotai/kimi-k2`），避免“Model Not Found”误用。

## 推荐操作流程
- 会话前环境注入：
  - `$env:HTTP_PROXY='http://127.0.0.1:7897'; $env:HTTPS_PROXY='http://127.0.0.1:7897'`
  - `$env:OPENROUTER_API_KEY='<你的密钥>'`
  - `$env:GOOSE_MAX_TOKENS='2000'`
- 运行示例（OpenRouter + Gemini）：
  - `goose run --provider openrouter --model google/gemini-2.0-flash-001 -t "你好"`
- 若需修改配置文件：
  - 先生成临时文件 `%LOCALAPPDATA%\\Temp\\goose_config_openrouter.yaml`
  - 管理员终端中执行：
    - `Copy-Item -Path "$env:LOCALAPPDATA\\Temp\\goose_config_openrouter.yaml" -Destination "C:\\Users\\onroud\\AppData\\Roaming\\Block\\goose\\config\\config.yaml" -Force`

## GitHub 规则文本（可粘贴）
Title: Goose Runtime Rules (Windows/OpenRouter/Proxy)

Rules:
1) Provider: Always use openrouter with OPENROUTER_API_KEY set to a valid key
2) Token Budget: Default GOOSE_MAX_TOKENS=2000 to avoid 402 Payment Required
3) Proxy: Set HTTP_PROXY/HTTPS_PROXY (e.g. http://127.0.0.1:7897) before running
4) Permissions: If Roaming config write is denied, require Admin and copy from %LOCALAPPDATA%\\Temp
5) Models: Use valid OpenRouter model IDs (e.g. google/gemini-2.0-flash-001 or moonshotai/kimi-k2)

Checklist:
- [ ] OPENROUTER_API_KEY present and valid
- [ ] HTTP_PROXY/HTTPS_PROXY set and curl to /api/v1/models returns 200
- [ ] GOOSE_MAX_TOKENS=2000 unless explicitly increased
- [ ] Admin override for config writes when needed
- [ ] Model ID verified against OpenRouter catalog
