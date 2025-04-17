import argparse
import numpy as np
from tabulate import tabulate

class ChipletConfig:
    def __init__(self, cpu_dies, cpu_cores_per_die, npu_dies, npu_cores_per_die, interconnect_bw, memory_bw):
        self.cpu_dies = cpu_dies
        self.cpu_cores_per_die = cpu_cores_per_die
        self.npu_dies = npu_dies
        self.npu_cores_per_die = npu_cores_per_die
        self.interconnect_bw = interconnect_bw  # GB/s
        self.interconnect_latency = 50e-9  # 50 ns
        self.interconnect_power_per_bit = 2e-12  # 2 pJ/bit
        self.memory_bw = memory_bw  # GB/s
        self.coherence_latency = 20e-9  # 20 ns per operation
        self.coherence_power_per_op = 0.05  # 0.05 W per operation
        self.sync_latency = 5e-6  # 5 µs per sync
        self.cpu_freq = 2.5  # GHz
        self.npu_freq = 1.5  # GHz
        self.cpu_dmips_per_core = 4000  # DMIPS/core
        self.npu_macs_per_core = 2048  # MACs/core
        self.cpu_power_per_core = 3.0  # W/core
        self.npu_power_per_core = 1.0  # W/core
        self.memory_power = 5.0  # W

class Workload:
    def __init__(self, cpu_flops, npu_flops, inference_freq, linux_dmips, data_size_per_inference):
        self.cpu_flops = cpu_flops
        self.npu_flops = npu_flops
        self.inference_freq = inference_freq
        self.linux_dmips = linux_dmips
        self.data_size_per_inference = data_size_per_inference  # GB

class BehavioralSimulator:
    def __init__(self, config, workload):
        self.config = config
        self.workload = workload

    def calculate_interconnect_overhead(self):
        data_size_gb = self.workload.data_size_per_inference
        transfer_time = (data_size_gb / self.config.interconnect_bw + self.config.interconnect_latency) * 1000  # ms
        data_bits = data_size_gb * 8e9
        interconnect_power = data_bits * self.config.interconnect_power_per_bit * self.workload.inference_freq  # W
        return transfer_time, interconnect_power

    def calculate_coherence_overhead(self):
        coherence_ops_per_inference = 10
        coherence_time = coherence_ops_per_inference * self.config.coherence_latency * 1000  # ms
        coherence_power = coherence_ops_per_inference * self.config.coherence_power_per_op * self.workload.inference_freq  # W
        return coherence_time, coherence_power

    def calculate_performance(self):
        # CPU性能
        total_cpu_cores = self.config.cpu_dies * self.config.cpu_cores_per_die
        cpu_flops_per_core = self.config.cpu_freq * 1e9
        cpu_time_linux = self.workload.linux_dmips / (total_cpu_cores * self.config.cpu_dmips_per_core) * 1000
        cpu_time_ai = self.workload.cpu_flops / (total_cpu_cores * cpu_flops_per_core) * 1000
        cpu_time = max(cpu_time_linux, cpu_time_ai)

        # NPU性能
        total_npu_cores = self.config.npu_dies * self.config.npu_cores_per_die
        npu_flops_per_core = self.config.npu_macs_per_core * self.config.npu_freq * 2
        npu_time = self.workload.npu_flops / (total_npu_cores * npu_flops_per_core) * 1000

        # 通信开销
        interconnect_time, interconnect_power = self.calculate_interconnect_overhead()

        # 一致性开销
        coherence_time, coherence_power = self.calculate_coherence_overhead()

        # 同步开销
        sync_time = self.config.sync_latency * self.workload.inference_freq * 1000

        # 内存竞争
        effective_memory_bw = self.config.memory_bw / (1 + 0.2 * (self.config.cpu_cores_per_die + self.config.npu_cores_per_die))
        memory_time = self.workload.data_size_per_inference / effective_memory_bw * 1000

        total_time = max(cpu_time, npu_time) + interconnect_time + coherence_time + sync_time + memory_time
        return cpu_time, npu_time, interconnect_time, coherence_time, sync_time, memory_time, total_time

    def calculate_power(self):
        total_cpu_cores = self.config.cpu_dies * self.config.cpu_cores_per_die
        total_npu_cores = self.config.npu_dies * self.config.npu_cores_per_die
        cpu_power = total_cpu_cores * self.config.cpu_power_per_core
        npu_power = total_npu_cores * self.config.npu_power_per_core
        interconnect_power = self.calculate_interconnect_overhead()[1]
        coherence_power = self.calculate_coherence_overhead()[1]
        total_power = cpu_power + npu_power + interconnect_power + coherence_power + self.config.memory_power
        return total_power

    def run(self):
        cpu_time, npu_time, interconnect_time, coherence_time, sync_time, memory_time, total_time = self.calculate_performance()
        total_power = self.calculate_power()
        return {
            "cpu_dies": self.config.cpu_dies,
            "cpu_cores_per_die": self.config.cpu_cores_per_die,
            "npu_dies": self.config.npu_dies,
            "npu_cores_per_die": self.config.npu_cores_per_die,
            "cpu_time_ms": cpu_time,
            "npu_time_ms": npu_time,
            "interconnect_time_ms": interconnect_time,
            "coherence_time_ms": coherence_time,
            "sync_time_ms": sync_time,
            "memory_time_ms": memory_time,
            "total_time_ms": total_time,
            "total_power_w": total_power
        }

def main():
    parser = argparse.ArgumentParser(description="Chiplet Architecture Simulator")
    parser.add_argument("--cpu_dies", type=int, required=True, help="Number of CPU dies")
    parser.add_argument("--cpu_cores", type=int, required=True, help="CPU cores per die")
    parser.add_argument("--npu_dies", type=int, required=True, help="Number of NPU dies")
    parser.add_argument("--npu_cores", type=int, required=True, help="NPU cores per die")
    parser.add_argument("--interconnect_bw", type=float, required=True, help="Interconnect bandwidth (GB/s)")
    parser.add_argument("--memory_bw", type=float, required=True, help="Memory bandwidth (GB/s)")
    parser.add_argument("--cpu_flops", type=float, required=True, help="CPU FLOPS per inference")
    parser.add_argument("--npu_flops", type=float, required=True, help="NPU FLOPS per inference")
    parser.add_argument("--inference_freq", type=float, required=True, help="Inference frequency (inferences/s)")
    parser.add_argument("--linux_dmips", type=float, required=True, help="Linux task DMIPS")
    parser.add_argument("--data_size", type=float, required=True, help="Data size per inference (GB)")

    args = parser.parse_args()

    config = ChipletConfig(
        cpu_dies=args.cpu_dies,
        cpu_cores_per_die=args.cpu_cores,
        npu_dies=args.npu_dies,
        npu_cores_per_die=args.npu_cores,
        interconnect_bw=args.interconnect_bw,
        memory_bw=args.memory_bw
    )
    workload = Workload(
        cpu_flops=args.cpu_flops,
        npu_flops=args.npu_flops,
        inference_freq=args.inference_freq,
        linux_dmips=args.linux_dmips,
        data_size_per_inference=args.data_size
    )

    simulator = BehavioralSimulator(config, workload)
    result = simulator.run()

    # 格式化输出
    headers = ["CPU Dies", "CPU Cores/Die", "NPU Dies", "NPU Cores/Die", "CPU Time (ms)", "NPU Time (ms)",
               "Interconnect (ms)", "Coherence (ms)", "Sync (ms)", "Memory (ms)", "Total Time (ms)", "Power (W)"]
    data = [[result["cpu_dies"], result["cpu_cores_per_die"], result["npu_dies"], result["npu_cores_per_die"],
             f"{result['cpu_time_ms']:.2f}", f"{result['npu_time_ms']:.2f}", f"{result['interconnect_time_ms']:.2f}",
             f"{result['coherence_time_ms']:.2f}", f"{result['sync_time_ms']:.2f}", f"{result['memory_time_ms']:.2f}",
             f"{result['total_time_ms']:.2f}", f"{result['total_power_w']:.2f}"]]
    print(tabulate(data, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    main()