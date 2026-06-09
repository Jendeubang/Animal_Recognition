"""
动物识别系统 - 单元测试
CI/CD 流水线通过 pytest 执行本测试
"""

import os
import sys
import importlib.util

# ── 测试1：模块可导入 ──
def test_imports():
    """验证所有 Python 依赖模块都能正常导入"""
    modules = [
        "torch", "torchvision", "fastapi", "uvicorn",
        "PIL", "numpy", "sklearn", "requests",
    ]
    for mod_name in modules:
        spec = importlib.util.find_spec(mod_name)
        assert spec is not None, f"模块 {mod_name} 未安装"
    print(f"✅ 全部 {len(modules)} 个模块导入成功")


# ── 测试2：项目目录结构 ──
def test_project_structure():
    """验证必要的目录和文件存在"""
    required = [
        "python/train.py",
        "python/predict_api.py",
        "python/requirements.txt",
        "java-client/pom.xml",
    ]
    for path in required:
        assert os.path.exists(path), f"缺少文件: {path}"
    
    # 模型文件可选（CI 中不需要完整模型）
    print(f"✅ 项目结构完整")


# ── 测试3：Python 脚本可解析 ──
def test_python_syntax():
    """验证所有 Python 文件语法正确"""
    import py_compile
    py_files = [
        "python/train.py",
        "python/predict_api.py",
    ]
    for f in py_files:
        py_compile.compile(f, doraise=True)
    print(f"✅ Python 语法检查通过")


# ── 测试4：requirements.txt 可解析 ──
def test_requirements():
    """验证 requirements.txt 格式正确"""
    with open("python/requirements.txt", "r") as f:
        lines = f.readlines()
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if line and not line.startswith("#"):
            assert "=" in line or ">=" in line or "~=" in line, \
                f"第 {i} 行格式异常: {line}"
    print(f"✅ requirements.txt 格式正确 ({len(lines)} 行)")


if __name__ == "__main__":
    test_imports()
    test_project_structure()
    test_python_syntax()
    test_requirements()
    print("\n🎉 所有测试通过！")
