#!/bin/bash
# 启动 Java Spring Boot 客户端
# 先确保 Python AI 服务已启动 (python/start.sh)

echo "================================"
echo "  🐾 动物识别 Java 客户端启动"
echo "================================"

echo ""
echo "确保 Python AI 服务已在 localhost:8000 运行"
echo ""

# Maven 编译并启动
mvn spring-boot:run
