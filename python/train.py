"""
动物识别模型训练脚本（CPU 优化版）
基于 torchvision 预训练 ResNet18，迁移学习微调
输出: models/animal_model.pth + models/classes.txt
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, WeightedRandomSampler
import numpy as np
import time

# ── 配置 ──────────────────────────────────────────
DATA_ROOT = os.path.join(os.path.dirname(__file__), "..", "raw-img")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
BATCH_SIZE = 32
EPOCHS = 8               # 8轮
LEARNING_RATE = 0.001    # 初始学习率
IMG_SIZE = 128           # 128兼顾速度和准确率
UNFREEZE_LAYERS = 1      # 只解冻最后1个残差块
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
os.makedirs(MODEL_DIR, exist_ok=True)

print(f"使用设备: {DEVICE}")
print(f"图片尺寸: {IMG_SIZE}x{IMG_SIZE}")
print(f"Batch: {BATCH_SIZE}  Epochs: {EPOCHS}")
print()

# ── 数据预处理 + 增强（CPU 友好版） ────────────────
# 1. 先定义一个只做 Resize 的基础 transform，用于快速扫描所有图片
base_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

# 2. 训练集增强（简化版，去掉耗时的 RandomRotation 和 ColorJitter）
train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE + 16, IMG_SIZE + 16)),
    transforms.RandomCrop(IMG_SIZE),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

# ── 加载数据集 ────────────────────────────────────
# 先用空 transform 加载（只做路径扫描，不处理图片）
print("正在扫描数据集...")
start = time.time()
full_dataset = datasets.ImageFolder(root=DATA_ROOT)
class_names = full_dataset.classes
print(f"  找到 {len(full_dataset)} 张图片，{len(class_names)} 个类别")
print(f"  类别: {class_names}")
print(f"  耗时: {time.time() - start:.1f}s")
print()

# 划分 train / val (80% / 20%)
train_size = int(0.8 * len(full_dataset))
val_size = len(full_dataset) - train_size
train_indices, val_indices = torch.utils.data.random_split(
    range(len(full_dataset)), [train_size, val_size],
    generator=torch.Generator().manual_seed(42),
)

# 分别设置 transform
train_dataset = datasets.ImageFolder(root=DATA_ROOT, transform=train_transform)
val_dataset = datasets.ImageFolder(root=DATA_ROOT, transform=base_transform)

# 用 Subset 取对应索引
from torch.utils.data import Subset
train_subset = Subset(train_dataset, train_indices.indices)
val_subset = Subset(val_dataset, val_indices.indices)

print(f"训练集: {len(train_subset)} 张")
print(f"验证集: {len(val_subset)} 张")

# ── 类别权重（处理不均衡） ────────────────────────
train_labels = [full_dataset.targets[i] for i in train_indices.indices]
class_counts = np.bincount(train_labels)
class_weights = 1.0 / class_counts
sample_weights = [class_weights[t] for t in train_labels]
sampler = WeightedRandomSampler(sample_weights, len(sample_weights), replacement=True)

train_loader = DataLoader(train_subset, batch_size=BATCH_SIZE,
                          sampler=sampler, num_workers=0)
val_loader = DataLoader(val_subset, batch_size=BATCH_SIZE,
                        shuffle=False, num_workers=0)

# ── 模型：预训练 ResNet18 ─────────────────────────
print()
print("正在加载预训练模型...")
model = models.resnet18(weights="IMAGENET1K_V1")

# 冻结所有参数
for param in model.parameters():
    param.requires_grad = False

# 解冻最后 N 个残差块（让高层特征适应动物识别）
if UNFREEZE_LAYERS > 0:
    layers_to_unfreeze = {
        1: model.layer4,      # 解冻 layer4（最后1个块）
        2: [model.layer4, model.layer3],  # 解冻 layer3+4
    }
    blocks = layers_to_unfreeze.get(UNFREEZE_LAYERS, [model.layer4])
    if not isinstance(blocks, list):
        blocks = [blocks]
    for block in blocks:
        for param in block.parameters():
            param.requires_grad = True
    print(f"  已解冻最后 {UNFREEZE_LAYERS} 个残差块进行微调")

# 替换最后一层全连接 → 10 分类
num_features = model.fc.in_features
model.fc = nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(num_features, len(class_names)),
)
model = model.to(DEVICE)

# 收集可训练参数
trainable_params = [p for p in model.parameters() if p.requires_grad]
print(f"模型总参数: {sum(p.numel() for p in model.parameters()):,}")
print(f"可训练参数: {sum(p.numel() for p in trainable_params):,}")
print()

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(trainable_params, lr=LEARNING_RATE)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max',
                                                   factor=0.5, patience=2)

# ── 训练循环 ──────────────────────────────────────
print("开始训练...")
print("-" * 70)
best_acc = 0.0
total_train_time = 0

for epoch in range(1, EPOCHS + 1):
    epoch_start = time.time()

    # 训练
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for batch_idx, (images, labels) in enumerate(train_loader):
        images, labels = images.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

        # 每 50 个 batch 打印一次进度
        if (batch_idx + 1) % 50 == 0:
            print(f"  Epoch {epoch}/{EPOCHS} | Batch {batch_idx+1}/{len(train_loader)} | "
                  f"Loss: {running_loss/total:.4f} | Acc: {100.*correct/total:.1f}%")

    train_acc = 100. * correct / total
    train_loss = running_loss / total

    # 验证
    model.eval()
    val_correct = 0
    val_total = 0
    val_loss = 0.0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            loss = criterion(outputs, labels)
            val_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            val_total += labels.size(0)
            val_correct += predicted.eq(labels).sum().item()

    val_acc = 100. * val_correct / val_total
    val_loss_val = val_loss / val_total
    epoch_time = time.time() - epoch_start
    total_train_time += epoch_time

    # 学习率调度（验证准确率不再提升时自动降低学习率）
    scheduler.step(val_acc)

    # 保存最佳模型
    if val_acc > best_acc:
        best_acc = val_acc
        torch.save(model.state_dict(), os.path.join(MODEL_DIR, "animal_model.pth"))
        with open(os.path.join(MODEL_DIR, "classes.txt"), "w", encoding="utf-8") as f:
            for name in class_names:
                f.write(name + "\n")
        best_str = " [NEW BEST]"
    else:
        best_str = ""

    print(f"[Epoch {epoch:2d}/{EPOCHS}] "
          f"Train Loss: {train_loss:.4f}  Acc: {train_acc:.2f}% | "
          f"Val Loss: {val_loss_val:.4f}  Acc: {val_acc:.2f}% | "
          f"Time: {epoch_time:.0f}s{best_str}")

print("-" * 70)
print(f"\n🎉 训练完成！总耗时: {total_train_time:.0f}s")
print(f"最佳验证准确率: {best_acc:.2f}%")
print(f"模型已保存至: {os.path.join(MODEL_DIR, 'animal_model.pth')}")

# 保存完整模型
full_model_path = os.path.join(MODEL_DIR, "animal_model_full.pth")
torch.save({
    'model_state_dict': model.state_dict(),
    'class_names': class_names,
    'img_size': IMG_SIZE,
}, full_model_path)
print(f"完整模型已保存至: {full_model_path}")
