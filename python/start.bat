@echo off
chcp 65001 >nul
title 🐾 动物识别 AI 服务
echo ================================
echo   🐾 动物识别 AI 服务启动脚本
echo ================================

echo.
echo [1/3] 安装 Python 依赖...
pip install -r requirements.txt -q

if not exist "models\animal_model.pth" (
    echo.
    echo [2/3] 训练模型中...
    python train.py
) else (
    echo.
    echo [2/3] 模型已存在，跳过训练
)

echo.
echo [3/3] 启动 FastAPI 服务...
echo    API 文档: http://localhost:8000/docs
echo    预测接口: POST http://localhost:8000/predict
echo.
uvicorn predict_api:app --host 0.0.0.0 --port 8000 --reload
pause
