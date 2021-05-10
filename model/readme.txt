The following is the specs of Harvard Cannon virtual machines where we trained our LSTM models in parallel.

log1: COG_2009_1, without GPU, 3s45ms
log2: COG_2009_1, with GPU, 1s12ms
log3: COG_2009_5, without GPU, 2s34ms
log4: COG_2009_5, with GPU, 1s10ms
log5: COG_2016_1, without GPU, 1s27ms
log6: COG_2016_1, with GPU, 0s12ms
log7: COG_2016_5, without GPU, 1s43ms
log8: COG_2016_5, with GPU, 0s13ms

seas_dgx1 partition, 16GB, 4 CPUs, 1 GPU

CPU_Info:
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                40
On-line CPU(s) list:   0-39
Thread(s) per core:    1
Core(s) per socket:    20
Socket(s):             2
NUMA node(s):          2
Vendor ID:             GenuineIntel
CPU family:            6
Model:                 79
Model name:            Intel(R) Xeon(R) CPU E5-2698 v4 @ 2.20GHz
Stepping:              1
CPU MHz:               1200.036
CPU max MHz:           3600.0000
CPU min MHz:           1200.0000
BogoMIPS:              4390.17
Virtualization:        VT-x
L1d cache:             32K
L1i cache:             32K
L2 cache:              256K
L3 cache:              51200K
NUMA node0 CPU(s):     0-19
NUMA node1 CPU(s):     20-39

GPU Info:
CUDA Driver Version:           11010
NVRM version:                  NVIDIA UNIX x86_64 Kernel Module  455.23.05  Fri Sep 18 19:37:12 UTC 2020

Device Number:                 0
Device Name:                   Tesla V100-SXM2-16GB
Device Revision Number:        7.0
Global Memory Size:            16945512448
Number of Multiprocessors:     80
Concurrent Copy and Execution: Yes
Total Constant Memory:         65536
Total Shared Memory per Block: 49152
Registers per Block:           65536
Warp Size:                     32
Maximum Threads per Block:     1024
Maximum Block Dimensions:      1024, 1024, 64
Maximum Grid Dimensions:       2147483647 x 65535 x 65535
Maximum Memory Pitch:          2147483647B
Texture Alignment:             512B
Clock Rate:                    1530 MHz
Execution Timeout:             No
Integrated Device:             No
Can Map Host Memory:           Yes
Compute Mode:                  default
Concurrent Kernels:            Yes
ECC Enabled:                   Yes
Memory Clock Rate:             877 MHz
Memory Bus Width:              4096 bits
L2 Cache Size:                 6291456 bytes
Max Threads Per SMP:           2048
Async Engines:                 6
Unified Addressing:            Yes
Managed Memory:                Yes
Concurrent Managed Memory:     Yes
Preemption Supported:          Yes
Cooperative Launch:            Yes
  Multi-Device:                Yes
Default Target:                cc70





