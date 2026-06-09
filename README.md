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

## CI/CD 流水线

### 配置

流水线文件：`.github/workflows/ci.yml`（GitHub Actions）

```
触发方式: push / pull_request / 手动
```

### 流水线阶段

| 阶段 | Job | 说明 |
|:----|:----|:------|
| 📥 拉取代码 | python-ci | `actions/checkout@v4` |
| 🐍 设置 Python | python-ci | Python 3.10 + pip 缓存 |
| 📦 安装依赖 | python-ci | `pip install -r requirements.txt` |
| 🔍 语法检查 | python-ci | `py_compile` 验证语法 |
| 🧪 执行测试 | python-ci | `pytest` 4 项测试 |
| ☕ Java 编译 | java-ci | `mvn compile` |
| 📦 打包归档 | java-ci | 生成 jar 并上传为 Artifact |
| 📢 通知 | notify | 输出构建结果 |

### 质量门禁

- **测试失败 → 自动中止**：pytest 返回非0退出码时，后续阶段不执行
- **语法错误阻止**：`py_compile` 失败即中止流水线
- **构建产物归档**：每次成功构建的 jar 包可在 Actions 页面下载

### 本地运行测试

```bash
# Python 测试
pip install pytest
python -m pytest python/test_ci.py -v --tb=short

# Java 测试（需要本地 MySQL）
cd java-client && mvn test
```

### CI/CD 徽章

[![CI](https://github.com/Jendeubang/Animal_Recognition/actions/workflows/ci.yml/badge.svg)](https://github.com/Jendeubang/Animal_Recognition/actions/workflows/ci.yml)

---

## 技术栈

| 层 | 技术 |
|----|------|
| 深度学习 | PyTorch + torchvision (ResNet18) |
| 推理服务 | FastAPI + uvicorn |
| Java 后端 | Spring Boot 3.2 + Thymeleaf |
| 通信 | HTTP multipart/form-data → JSON |
