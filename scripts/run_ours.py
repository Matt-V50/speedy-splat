import os
import pty
import select
import subprocess


# ============================================================
# 配置参数
# ============================================================
def get_train_cmd(input, output, image_dir=None):

    # 路径配置
    image_root = f"/home/matt/cviss/Matt/Dataset/{input}"  # Blendswap/Render/pick/13078_toad
    output_base_dir = f"/home/matt/cviss/Matt/GS-Output"
    output_full_dir = f"{output_base_dir}/Speedy-Splat/{output}"  # pick/13078_toad

    # ============================================================
    # FastGS 训练命令
    # ============================================================
    cmd = (
        f"OMP_NUM_THREADS=4 "
        f"CUDA_VISIBLE_DEVICES=0 "
        f"python train.py "
        f"-s {image_root} "
        f"-m {output_full_dir} "
        f"{f'-i {image_dir} ' if image_dir is not None else ''}"
        f"-r 1 "
        f"--eval "
        f"--iterations 30000 "
        f"--test_iterations 7000 30000 "
        f"--save_iterations 7000 30000 "
    )
    # ============================================================
    # FastGS 评估命令
    # ============================================================
    eval_cmd = (
        f"python evaluate_metrics.py -s {image_root} -m {output_full_dir} --iterations 7000 30000"
    )
    
    return cmd, eval_cmd


def run_with_live_output(cmd):
    """运行命令并实时显示输出，正确处理 tqdm"""
    master_fd, slave_fd = pty.openpty()
    
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=slave_fd,
        stderr=slave_fd,
        close_fds=True
    )
    os.close(slave_fd)
    
    output_lines = []
    
    while True:
        ready, _, _ = select.select([master_fd], [], [], 0.1)
        if ready:
            try:
                data = os.read(master_fd, 1024).decode('utf-8', errors='replace')
                if data:
                    print(data, end='', flush=True)
                    output_lines.append(data)
            except OSError:
                break
        
        if process.poll() is not None:
            # 读取剩余输出
            while True:
                try:
                    data = os.read(master_fd, 1024).decode('utf-8', errors='replace')
                    if not data:
                        break
                    print(data, end='', flush=True)
                    output_lines.append(data)
                except OSError:
                    break
            break
    
    os.close(master_fd)
    return process.returncode, ''.join(output_lines)

cmd, eval_cmd = get_train_cmd(input="Rogers/Tower_0529", output="Rogers/Tower_0529_4", image_dir="images_4")

run_with_live_output(cmd)
run_with_live_output(eval_cmd)

cmd, eval_cmd = get_train_cmd(input="Rogers/Tower_0529", output="Rogers/Tower_0529_8", image_dir="images_8")

run_with_live_output(cmd)
run_with_live_output(eval_cmd)


###################### 
cmd, eval_cmd = get_train_cmd(input="Blendswap/Render/pick/13078_toad", output="Blendswap/pick/13078_toad", image_dir=None)

run_with_live_output(cmd)
run_with_live_output(eval_cmd)
