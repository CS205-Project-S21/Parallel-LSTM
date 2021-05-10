The following is the specs of AWS EC2 and EMR instance we use to do the parallel computing

Multi-Core test:
AWS: Ubuntu 18.04, m4.4xlarge(16vcpus + 64GiB memory)
Library Installed: Pyspark == 3.1.1, python == 3.9.1,
Java version: openjdk version "1.8.0_292"
OpenJDK Runtime Environment (build 1.8.0_292-8u292-b100ubuntu1~18.04-b10)
OpenJDK 64-Bit Server VM (build 25.292-b10, mixed mode)

CPU_Info:
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                16
On-line CPU(s) list:   0-15
Thread(s) per core:    2
Core(s) per socket:    8
Socket(s):             1
NUMA node(s):          1
Vendor ID:             GenuineIntel
CPU family:            6
Model:                 79
Model name:            Intel(R) Xeon(R) CPU E5-2686 v4 @ 2.30GHz
Stepping:              1
CPU MHz:               2299.981
BogoMIPS:              4600.16
Hypervisor vendor:     Xen
Virtualization type:   full     
L1d cache:             32K
L1i cache:             32K
L2 cache:              256K
L3 cache:              46060K
NUMA node0 CPU(s):     0-15

Multi-instance test:

AWS: emr-6.3.0: Spark 3.1.1 on Hadoop 3.2.1 with 1-8 core instances (m4.xlarge)python == 3.9.1

CPU_Info:
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                4
On-line CPU(s) list:   0-3
Thread(s) per core:    2
Core(s) per socket:    2
Socket(s):             1
NUMA node(s):          1
Vendor ID:             GenuineIntel
CPU family:            6
Model:                 79
Model name:            Intel(R) Xeon(R) CPU E5-2686 v4 @ 2.30GHz
Stepping:              1
CPU MHz:               2300.006
BogoMIPS:              4600.04
Hypervisor vendor:     Xen
Virtualization type:   full     
L1d cache:             32K
L1i cache:             32K
L2 cache:              256K
L3 cache:              46080K
NUMA node0 CPU(s):     0-3

Latency: rtt min/avg/max/mdev = 0.311/0.339/0.363/0.021 ms 
Bandwidth: 
	Interval             Transfer        Bandwidth
       0.0-10.0sec          1.22GBytes      1.05Gbits/sec

