@echo off
chcp 65001 >nul
title 🐾 动物识别 Java 客户端

echo ================================
echo   🐾 动物识别 Java 客户端启动
echo ================================
echo.
echo 请确保 Python AI 服务已在 localhost:8000 运行
echo.
echo 启动 Spring Boot...
mvn spring-boot:run
pause
