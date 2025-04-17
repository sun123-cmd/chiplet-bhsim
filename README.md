# Chiplet Architecture Simulator

This repository provides a user-friendly behavioral simulator for evaluating chiplet-based architectures. The simulator estimates performance (e.g., inference time, Linux task latency), power consumption, and overheads (e.g., die-to-die communication, coherence) for various configurations of CPU and NPU dies. It is designed for coarse-grained analysis, ideal for early-stage design space exploration.

## Features

- **Configurable Architecture**: Specify CPU/NPU die counts, cores per die, interconnect bandwidth, and memory bandwidth.
- **Workload Support**: Model AI inference (FLOPS) and Linux tasks (DMIPS).
- **Overhead Modeling**: Includes die-to-die communication, coherence, synchronization, and memory contention overheads.
- **User-Friendly Interface**: Configure simulations via command-line arguments or a JSON configuration file.
- **Structured Output**: Results are presented in a tabular format for easy analysis.

## Prerequisites

- **Python 3.6+**: Ensure Python is installed (`python --version`).
- **pip**: For installing Python dependencies.
- **jq**: For parsing JSON configuration files (required for multi-configuration runs).
  - Install on Linux: `sudo apt install jq`
  - Install on macOS: `brew install jq`
  - Install on Windows: Download from jq releases
- **Dependencies**: Python package `tabulate` for formatted table output.

## Installation

1. **Clone the Repository** (if applicable):

   ```bash
   git clone <repository-url>
   cd chiplet-simulator
   ```

2. **Install Python Dependencies**:

   ```bash
   pip install tabulate
   ```

3. **Make the Shell Script Executable**:

   ```bash
   chmod +x run_simulation.sh
   ```

## Files

- `run_simulation.sh`: Shell script to configure and run simulations.
- `simulate.py`: Python script containing the simulator logic.
- `configs.json`: Example JSON file for defining multiple configurations.

## Usage

### 1. Running a Single Configuration

Use the `run_simulation.sh` script with command-line arguments to run a single simulation.

**Example**:

```bash
./run_simulation.sh \
    --cpu_dies 1 \
    --cpu_cores 6 \
    --npu_dies 1 \
    --npu_cores 16 \
    --interconnect_bw 200 \
    --memory_bw 400 \
    --cpu_flops 1e12 \
    --npu_flops 20e12 \
    --inference_freq 10 \
    --linux_dmips 20000 \
    --data_size 0.01
```

**Parameters**:

| Parameter | Description | Example Value |
| --- | --- | --- |
| `--cpu_dies` | Number of CPU dies | 1 |
| `--cpu_cores` | CPU cores per die | 6 |
| `--npu_dies` | Number of NPU dies | 1 |
| `--npu_cores` | NPU cores per die | 16 |
| `--interconnect_bw` | Interconnect bandwidth (GB/s) | 200 |
| `--memory_bw` | Memory bandwidth (GB/s) | 400 |
| `--cpu_flops` | CPU FLOPS per inference | 1e12 |
| `--npu_flops` | NPU FLOPS per inference | 20e12 |
| `--inference_freq` | Inference frequency (inferences/s) | 10 |
| `--linux_dmips` | Linux task DMIPS | 20000 |
| `--data_size` | Data size per inference (GB) | 0.01 |

**Output**: A table displaying the simulation results, including CPU/NPU times, overheads, total time, and power consumption.

### 2. Running Multiple Configurations

Use a JSON configuration file to define multiple configurations and run them in batch.

**Example** `configs.json`:

```json
[
    {
        "cpu_dies": 1,
        "cpu_cores_per_die": 4,
        "npu_dies": 1,
        "npu_cores_per_die": 8,
        "interconnect_bw": 100,
        "memory_bw": 200
    },
    {
        "cpu_dies": 1,
        "cpu_cores_per_die": 6,
        "npu_dies": 1,
        "npu_cores_per_die": 16,
        "interconnect_bw": 200,
        "memory_bw": 400
    },
    {
        "cpu_dies": 1,
        "cpu_cores_per_die": 8,
        "npu_dies": 2,
        "npu_cores_per_die": 16,
        "interconnect_bw": 400,
        "memory_bw": 400
    }
]
```

**Run**:

```bash
./run_simulation.sh \
    --config_file configs.json \
    --cpu_flops 1e12 \
    --npu_flops 20e12 \
    --inference_freq 10 \
    --linux_dmips 20000 \
    --data_size 0.01
```

**Output**: Separate tables for each configuration, showing performance and power metrics.

### 3. Example Output

```
+----------------+--------------------+----------------+--------------------+-----------------+-----------------+---------------------+-------------------+---------------+-----------------+------------------+-------------+
|   CPU Dies     |   CPU Cores/Die    |   NPU Dies     |   NPU Cores/Die    |   CPU Time (ms) |   NPU Time (ms) |   Interconnect (ms) |   Coherence (ms)  |   Sync (ms)   |   Memory (ms)   |   Total Time (ms)|   Power (W) |
+----------------+--------------------+----------------+--------------------+-----------------+-----------------+---------------------+-------------------+---------------+-----------------+------------------+-------------+
|              1 |                  6 |              1 |                 16 |            0.40 |            0.41 |                0.05 |              0.00 |          0.05 |            0.03 |             0.84 |       29.60 |
+----------------+--------------------+----------------+--------------------+-----------------+-----------------+---------------------+-------------------+---------------+-----------------+------------------+-------------+
```

## Configuration Tips

- **Workload Parameters**:
  - Derive `cpu_flops` and `npu_flops` from ONNX model analysis (e.g., using `onnx` library).
  - Estimate `linux_dmips` based on Linux task requirements (e.g., 20K DMIPS for real-time scheduling).
  - Calculate `data_size` from model output sizes (e.g., 10 MB for a 10B parameter model).
- **Architecture Parameters**:
  - Start with 1 CPU die and 1-2 NPU dies for edge devices.
  - Use 4-8 CPU cores and 8-32 NPU cores per die for balanced performance.
  - Set `interconnect_bw` to 100-400 GB/s (based on UCIe or HBM standards).
  - Set `memory_bw` to 200-400 GB/s (based on HBM3 or LPDDR5).
- **Constraints**:
  - Target inference time &lt; 10 ms and Linux task latency &lt; 1 ms.
  - Keep power consumption within budget (e.g., 10-50 W for edge devices).

## Troubleshooting

- **ModuleNotFoundError: No module named 'tabulate'**: Install `tabulate`:

  ```bash
  pip install tabulate
  ```
- **jq: command not found**: Install `jq` (see Prerequisites).
- **Permission Denied for** `run_simulation.sh`: Add execute permission:

  ```bash
  chmod +x run_simulation.sh
  ```
- **Invalid Parameters**: Ensure all required parameters are provided and are valid numbers (e.g., positive integers for die/core counts).

## Extending the Simulator

- **Save Results**: Modify `simulate.py` to save results to a CSV file:

  ```python
  import csv
  with open("results.csv", "a") as f:
      writer = csv.DictWriter(f, fieldnames=result.keys())
      if f.tell() == 0:
          writer.writeheader()
      writer.writerow(result)
  ```
- **Visualize Results**: Add `matplotlib` for plotting:

  ```python
  import matplotlib.pyplot as plt
  plt.plot([1, 2, 3], [total_time1, total_time2, total_time3], label="Total Time (ms)")
  plt.savefig("performance.png")
  ```
- **Add Parameters**: Extend `ChipletConfig` and `argparse` to include new parameters (e.g., CPU/NPU frequency, cache size).

## License

This project is licensed under the MIT License. See the `LICENSE` file for details (if provided).

## Contact

For issues or feature requests, please open an issue on the repository or contact the maintainer.``