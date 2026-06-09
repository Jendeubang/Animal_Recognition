# 🐾 动物识别系统 — Python AI + Java 微服务方案

## 系统架构

```
┌─────────────────────────────────┐      ┌────────────────────────────────┐
│  Java Spring Boot (8080)        │      │  Python FastAPI (8000)         │
│                                 │      │                                │
│  ┌──────────┐    ┌──────────┐  │HTTP  │  ┌──────────┐   ┌──────────┐   │
│  │  HTML 页面 │───→│  Controller │──┼─────→│  predict │   │  PyTorch │   │
│  │ (浏览器)   │    │           │←─┼─────│  _api.py  │←──→│  Model   │   │
│  └──────────┘    └──────────┘  │JSON  │  └──────────┘   └──────────┘   │
│                                 │      │                                │
│  用户上传图片 → 转 Base64 回显  │      │  加载 trained/animal_model.pth │
│                                 │      │                                │
└─────────────────────────────────┘      └────────────────────────────────┘
```

---

## 快速启动 (两步)

### 第一步：启动 Python AI 服务

```bash
cd python

# 安装依赖
pip install -r requirements.txt

# 训练模型（约 15-30 分钟，取决于 CPU/GPU）
python train.py

# 启动 API 服务
uvicorn predict_api:app --host 0.0.0.0 --port 8000 --reload
```

验证: 访问 http://localhost:8000/health → `{"status":"ok"}`

### 第二步：启动 Java 客户端

```bash
cd java-client

# Maven 编译 + 启动
mvn spring-boot:run
```

浏览器打开 http://localhost:8080 → 上传图片 → 自动识别！

---

## API 接口

### Python AI 服务 (端口 8000)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/` | 服务信息 + 类别列表 |
| POST | `/predict` | 单张图片识别 (multipart, field: file) |
| POST | `/predict_batch` | 批量识别 (multipart, field: files) |

### Java 客户端 (端口 8080)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | HTML 上传页面 |
| POST | `/predict` | HTML 上传 + 返回页面 |
| POST | `/api/predict` | REST API (JSON 返回) |

---

## 配置自定义

编辑 `java-client/src/main/resources/application.yml`，修改 AI 服务地址：

```yaml
ai:
  service:
    url: http://192.168.1.100:8000   # 改为远程 Python 服务器地址
```

---

## 技术栈

| 层 | 技术 |
|----|------|
| 深度学习 | PyTorch + torchvision (ResNet18) |
| 推理服务 | FastAPI + uvicorn |
| Java 后端 | Spring Boot 3.2 + Thymeleaf |
| 通信 | HTTP multipart/form-data → JSON |
