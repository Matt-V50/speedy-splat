#!/usr/bin/env fish
# ============================================================
# Speedy-Splat 环境配置脚本 (Fish Shell)
# 基于 3DGS 优化的快速渲染方案
# Paper: "Speedy-Splat: Fast 3D Gaussian Splatting with Sparse Pixels and Sparse Primitives" (CVPR 2025)
# GitHub: https://github.com/j-alex-hanson/speedy-splat
# ============================================================

# 环境名称
set ENV_NAME "speedysplat"

echo "=========================================="
echo "开始配置 Speedy-Splat 环境"
echo "=========================================="

# 创建conda环境
echo "创建 Python 3.10 环境..."
conda create -y -n $ENV_NAME python=3.10
conda activate $ENV_NAME

# ============================================================
# PyTorch + CUDA 12.1
# ============================================================
echo "安装 PyTorch 2.4.1 + CUDA 12.1..."
conda install pytorch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 pytorch-cuda=12.1 -c pytorch -c nvidia --yes

# 安装 CUDA toolkit
conda install cuda-toolkit -c nvidia/label/cuda-12.1.0 --yes

# 解决常见编译问题
echo "安装编译工具链..."
conda install mkl==2023.1.0 mkl-include -c conda-forge --yes
conda install cuda-cudart=12.1.55 -c nvidia/label/cuda-12.1.0 --yes

# ============================================================
# 3DGS 基础依赖
# ============================================================
echo "安装 3DGS 基础依赖..."
pip install plyfile==1.1 \
    tqdm \
    opencv-python \
    pillow==11.0.0 \
    scikit-image \
    imageio \
    lpips \
    joblib

# ============================================================
# Speedy-Splat 特定依赖
# ============================================================
echo "安装 Speedy-Splat 额外依赖..."
pip install tensorboard \
    matplotlib \
    scipy

pip install numpy==1.24.0
# ============================================================
# 编译 Speedy-Splat 的 CUDA 扩展
# 注意：Speedy-Splat 使用优化过的 diff-gaussian-rasterization
# 核心优化：SnugBox (精确 Gaussian-tile 边界计算) + AccuTile (精确相交计算)
# ============================================================
echo ""
echo "=========================================="
echo "编译 Speedy-Splat CUDA 扩展..."
echo "=========================================="

# 设置 CUDA 环境变量
set -x CUDA_HOME $CONDA_PREFIX

# 编译 submodules
pip install submodules/diff-gaussian-rasterization/ submodules/simple-knn/ --no-build-isolation


echo "CUDA 扩展编译完成！"

echo ""
echo "=========================================="
echo "Speedy-Splat 环境配置完成!"
echo "=========================================="
echo ""
echo "使用方法:"
echo "  conda activate $ENV_NAME"
echo "  cd speedy-splat"
echo ""
echo "训练 (使用 Speedy-Splat 加速):"
echo "  # 设置环境变量"
echo "  set -x SCENE_DATA_PATH <path_to_colmap_or_nerf_data>"
echo "  set -x SCENE_MODEL_PATH <path_to_output_model>"
echo ""
echo "  # 运行训练脚本"
echo "  bash train.sh"
echo ""
echo "  # 或直接使用 Python 脚本"
echo "  python train.py -s <path_to_data> -m <path_to_model>"
echo ""
echo "计算场景指标:"
echo "  # 设置环境变量"
echo "  set -x SCENE_DATA_PATH <path_to_data>"
echo "  set -x SCENE_MODEL_PATH <path_to_trained_model>"
echo "  set -x ONLY_RAW_KERNEL_TIMES false  # 或 true 只输出渲染时间"
echo ""
echo "  # 运行评估脚本"
echo "  bash compute_scene_metrics.sh"
echo ""
echo "  # 结果保存在："
echo "  # <model_path>/<train|test>/ours_<iteration>/metrics.csv"
echo ""
echo "渲染:"
echo "  python render.py -m <path_to_model>"
echo ""
echo "评估:"
echo "  python metrics.py -m <path_to_model>"
echo ""
echo "=========================================="
echo "Speedy-Splat 核心技术："
echo "=========================================="
echo ""
echo "1. SnugBox: 精确计算 Gaussian-tile 边界框交集"
echo "   - 显著减少 tile 分配过估计"
echo "   - 降低下游函数计算开销"
echo ""
echo "2. AccuTile: SnugBox 扩展，计算精确的 Gaussian-tile 交集"
echo "   - 进一步优化 tile 分配"
echo ""
echo "3. Soft Pruning: 密集化过程中剪枝 Gaussians"
echo "   - 在训练过程中动态减少冗余 primitives"
echo ""
echo "4. Hard Pruning: 密集化后剪枝 Gaussians"
echo "   - 进一步压缩模型大小"
echo ""
echo "=========================================="
echo "性能对比 (与原版 3D-GS 相比)："
echo "=========================================="
echo ""
echo "  渲染速度提升:    6.71×"
echo "  Gaussian 数量:   10.6× 更少"
echo "  训练时间减少:    显著"
echo "  图像质量:        保持竞争力"
echo ""
echo "相关工作："
echo "  - PUP-3DGS (CVPR 2025): 剪枝 90% primitives"
echo "  - SpeeDe3DGS: 加速 DeformableGS 到 276 FPS"
echo ""