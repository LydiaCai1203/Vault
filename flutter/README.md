# Vault Flutter App（骨架）

> 注意：当前沙箱环境未安装 Flutter SDK，因此我在这里提供的是**完整可运行的 Flutter 工程代码骨架**（你在本机安装 Flutter 后即可运行）。

## 运行

1) 安装 Flutter（本机）
2) 进入工程目录：
```bash
cd flutter_app
flutter pub get
flutter run
```

## 后端

后端是 FastAPI：
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

默认前端请求 `http://127.0.0.1:8000`。

## 已包含页面
- 底部导航：总览 / 交易 / 记一笔 / 复盘 / 我的
- 交易列表 + 交易详情
- 复盘列表 + 复盘详情（3M 雷达图 + 情绪&纪律热力图）
- 记一笔（自然语言录入骨架）
- 开仓前清单

## 下一步建议
- 把 baseUrl 改成你线上域名/局域网 IP
- 补齐：登录、Portfolio、真实 Recorder 解析、复盘生成任务（对接你的 Agent 模块）
