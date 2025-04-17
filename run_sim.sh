#!/bin/bash

# 默认参数
CPU_DIES=1
CPU_CORES_PER_DIE=6
NPU_DIES=1
NPU_CORES_PER_DIE=16
INTERCONNECT_BW=200
MEMORY_BW=400
CPU_FLOPS=1e12
NPU_FLOPS=20e12
INFERENCE_FREQ=10
LINUX_DMIPS=20000
DATA_SIZE=0.01

# 配置文件路径（可选）
CONFIG_FILE=""

# 解析命令行参数
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --cpu_dies) CPU_DIES="$2"; shift ;;
        --cpu_cores) CPU_CORES_PER_DIE="$2"; shift ;;
        --npu_dies) NPU_DIES="$2"; shift ;;
        --npu_cores) NPU_CORES_PER_DIE="$2"; shift ;;
        --interconnect_bw) INTERCONNECT_BW="$2"; shift ;;
        --memory_bw) MEMORY_BW="$2"; shift ;;
        --cpu_flops) CPU_FLOPS="$2"; shift ;;
        --npu_flops) NPU_FLOPS="$2"; shift ;;
        --inference_freq) INFERENCE_FREQ="$2"; shift ;;
        --linux_dmips) LINUX_DMIPS="$2"; shift ;;
        --data_size) DATA_SIZE="$2"; shift ;;
        --config_file) CONFIG_FILE="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# 如果指定了配置文件，读取多组配置
if [[ -n "$CONFIG_FILE" ]]; then
    if [[ ! -f "$CONFIG_FILE" ]]; then
        echo "Config file $CONFIG_FILE not found!"
        exit 1
    fi
    # 假设配置文件为JSON格式，使用jq解析
    CONFIGS=$(cat "$CONFIG_FILE")
    echo "$CONFIGS" | jq -c '.[]' | while read -r config; do
        cpu_dies=$(echo "$config" | jq -r '.cpu_dies')
        cpu_cores=$(echo "$config" | jq -r '.cpu_cores_per_die')
        npu_dies=$(echo "$config" | jq -r '.npu_dies')
        npu_cores=$(echo "$config" | jq -r '.npu_cores_per_die')
        interconnect_bw=$(echo "$config" | jq -r '.interconnect_bw')
        memory_bw=$(echo "$config" | jq -r '.memory_bw')
        python simulate.py \
            --cpu_dies "$cpu_dies" \
            --cpu_cores "$cpu_cores" \
            --npu_dies "$npu_dies" \
            --npu_cores "$npu_cores" \
            --interconnect_bw "$interconnect_bw" \
            --memory_bw "$memory_bw" \
            --cpu_flops "$CPU_FLOPS" \
            --npu_flops "$NPU_FLOPS" \
            --inference_freq "$INFERENCE_FREQ" \
            --linux_dmips "$LINUX_DMIPS" \
            --data_size "$DATA_SIZE"
    done
else
    # 运行单组配置
    python3 simulate.py \
        --cpu_dies "$CPU_DIES" \
        --cpu_cores "$CPU_CORES_PER_DIE" \
        --npu_dies "$NPU_DIES" \
        --npu_cores "$NPU_CORES_PER_DIE" \
        --interconnect_bw "$INTERCONNECT_BW" \
        --memory_bw "$MEMORY_BW" \
        --cpu_flops "$CPU_FLOPS" \
        --npu_flops "$NPU_FLOPS" \
        --inference_freq "$INFERENCE_FREQ" \
        --linux_dmips "$LINUX_DMIPS" \
        --data_size "$DATA_SIZE"
fi