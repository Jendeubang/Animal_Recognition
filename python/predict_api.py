"""
动物识别 FastAPI 推理服务
启动: uvicorn predict_api:app --host 0.0.0.0 --port 8000
Java 端通过 HTTP POST http://localhost:8000/predict 调用
"""

import os
import json
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ── 配置 ──────────────────────────────────────────
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "animal_model.pth")
CLASSES_PATH = os.path.join(MODEL_DIR, "classes.txt")
FULL_MODEL_PATH = os.path.join(MODEL_DIR, "animal_model_full.pth")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
IMG_SIZE = 128

# ── 置信度阈值 ────────────────────────────────────
# 低于此阈值视为"无法识别"
# 原有10类置信度99%+，新增6类约70-90%，设为60%可兼顾
CONFIDENCE_THRESHOLD = 0.60  # 60%

# ── 名称映射 ──────────────────────────────────────
# 意大利语 → 中文
LABEL_MAP_CN = {
    "cane": "狗", "cavallo": "马", "elefante": "大象",
    "farfalla": "蝴蝶", "gallina": "鸡", "gatto": "猫",
    "mucca": "牛", "pecora": "羊", "ragno": "蜘蛛",
    "scoiattolo": "松鼠",
    "uccello": "鸟", "anatra": "鸭子", "coniglio": "兔子",
    "tigre": "老虎", "leone": "狮子", "scimmia": "猴子",
}

# 意大利语 → 英文
LABEL_MAP_EN = {
    "cane": "dog", "cavallo": "horse", "elefante": "elephant",
    "farfalla": "butterfly", "gallina": "chicken", "gatto": "cat",
    "mucca": "cow", "pecora": "sheep", "ragno": "spider",
    "scoiattolo": "squirrel",
    "uccello": "bird", "anatra": "duck", "coniglio": "rabbit",
    "tigre": "tiger", "leone": "lion", "scimmia": "monkey",
}

# ── 加载模型 ──────────────────────────────────────
def load_model():
    """加载训练好的模型和类别名称"""
    # 读取类别
    if os.path.exists(CLASSES_PATH):
        with open(CLASSES_PATH, "r", encoding="utf-8") as f:
            classes = [line.strip() for line in f.readlines()]
    else:
        classes = list(LABEL_MAP_CN.keys())

    print(f"类别列表: {classes}")
    print(f"  中文映射: {[LABEL_MAP_CN.get(c, c) for c in classes]}")

    # 构建模型架构（必须与 train.py 完全一致）
    model = models.resnet18(weights=None)
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(num_features, len(classes)),
    )
    print(f"  模型 fc 层: {model.fc}")

    # 加载权重
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        print(f"模型已加载: {MODEL_PATH}")
    elif os.path.exists(FULL_MODEL_PATH):
        checkpoint = torch.load(FULL_MODEL_PATH, map_location=DEVICE)
        model.load_state_dict(checkpoint['model_state_dict'])
        classes = checkpoint.get('class_names', classes)
        print(f"模型已加载: {FULL_MODEL_PATH}")
    else:
        raise RuntimeError(
            f"未找到模型文件！请先运行 train.py 训练模型。\n"
            f"期望路径: {MODEL_PATH} 或 {FULL_MODEL_PATH}"
        )

    model = model.to(DEVICE)
    model.eval()
    return model, classes

model, classes = load_model()

# ── 图片预处理 ────────────────────────────────────
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

# ── FastAPI 应用 ─────────────────────────────────
app = FastAPI(
    title="🐾 动物识别 API",
    description="上传动物图片，返回识别结果（英文标签 + 中文名称 + 置信度）",
    version="1.0.0",
)

# 允许 Java 跨域调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """健康检查 + 服务信息"""
    return {
        "service": "动物识别 API",
        "status": "running",
        "device": DEVICE,
        "classes": classes,
        "classes_cn": [LABEL_MAP_CN.get(c, c) for c in classes],
        "classes_en": [LABEL_MAP_EN.get(c, c) for c in classes],
        "usage": "POST /predict (multipart/form-data, field: file)",
    }


@app.get("/health")
def health():
    """健康检查"""
    return {"status": "ok", "device": DEVICE}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    上传图片进行动物识别

    请求: multipart/form-data, file 字段为图片
    返回: {
        "success": true,
        "label": "dog",
        "label_cn": "狗",
        "confidence": 0.9723,
        "probabilities": { ... }
    }
    """
    # 校验文件类型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件 (jpg/png)")

    try:
        # 读取上传的图片
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"图片解析失败: {str(e)}")

    # 预处理
    input_tensor = transform(image).unsqueeze(0).to(DEVICE)

    # 推理
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

    # 取 Top-1 结果
    top1_idx = probabilities.argmax().item()
    top1_conf = probabilities[top1_idx].item()
    top1_label = classes[top1_idx]

    # ── 置信度过低 → 无法识别 ──
    if top1_conf < CONFIDENCE_THRESHOLD:
        return JSONResponse(content={
            "success": True,
            "recognized": False,
            "label": "unknown",
            "label_en": "unknown",
            "label_cn": "无法识别",
            "confidence": round(top1_conf, 4),
            "message": f"无法识别（最高置信度仅{top1_conf*100:.1f}%）",
            "device": DEVICE,
        })

    # 取 Top-3 结果
    top3_indices = probabilities.argsort(descending=True)[:3]
    top3_results = []
    for idx in top3_indices:
        idx = idx.item()
        label = classes[idx]
        conf = probabilities[idx].item()
        top3_results.append({
            "label": label,
            "label_en": LABEL_MAP_EN.get(label, label),
            "label_cn": LABEL_MAP_CN.get(label, label),
            "confidence": round(conf, 4),
        })

    result = {
        "success": True,
        "recognized": True,
        "label": top1_label,
        "label_en": LABEL_MAP_EN.get(top1_label, top1_label),
        "label_cn": LABEL_MAP_CN.get(top1_label, top1_label),
        "confidence": round(top1_conf, 4),
        "top3": top3_results,
        "device": DEVICE,
    }

    return JSONResponse(content=result)


@app.post("/predict_batch")
async def predict_batch(files: list[UploadFile] = File(...)):
    """
    批量识别（一次上传多张图片）

    请求: multipart/form-data, files 字段为多张图片
    """
    results = []
    for f in files:
        try:
            contents = await f.read()
            image = Image.open(io.BytesIO(contents)).convert("RGB")
            input_tensor = transform(image).unsqueeze(0).to(DEVICE)
            with torch.no_grad():
                outputs = model(input_tensor)
                probs = torch.nn.functional.softmax(outputs[0], dim=0)
            top1_idx = probs.argmax().item()
            results.append({
                "filename": f.filename,
                "label": classes[top1_idx],
                "label_en": LABEL_MAP_EN.get(classes[top1_idx], classes[top1_idx]),
                "label_cn": LABEL_MAP_CN.get(classes[top1_idx], classes[top1_idx]),
                "confidence": round(probs[top1_idx].item(), 4),
            })
        except Exception as e:
            results.append({
                "filename": f.filename,
                "error": str(e),
            })

    return JSONResponse(content={"success": True, "results": results})


# ── 启动入口 ────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print(f"🚀 启动动物识别服务 (设备: {DEVICE})")
    print(f"   API 文档: http://localhost:8000/docs")
    print(f"   预测接口: POST http://localhost:8000/predict")
    uvicorn.run(app, host="0.0.0.0", port=8000)
