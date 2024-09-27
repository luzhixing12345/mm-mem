import re

class LatencyIdle:
    def __init__(self):
        self.threads = None
        self.region_size_kb = None
        self.chunk_size_kb = None
        self.stride_size_b = None
        self.access_pattern = None
        self.use_hugepage = None
        self.target_duration = None
        self.idle_latency = {}

    def parse(self, text: str):
        '''
        threads:           1
        region size in KB: 524288
        chunk size in KB:  128
        stride size in B:  128
        access pattern:    1 - random in chunk
        use hugepage:      0 - No huge page
        target duration:   2
        Idle Latency (ns) - RandomInChunk       Node-0    Node-1    Node-2    Node-3
        Node-0                                  78.59     120.3     379.9     299.4
        Node-1                                  119.8     80.99     177.6     190.9
        '''
        # 使用正则表达式提取信息
        self.threads = int(re.search(r'threads:\s+(\d+)', text).group(1))
        self.region_size_kb = int(re.search(r'region size in KB:\s+(\d+)', text).group(1))
        self.chunk_size_kb = int(re.search(r'chunk size in KB:\s+(\d+)', text).group(1))
        self.stride_size_b = int(re.search(r'stride size in B:\s+(\d+)', text).group(1))
        self.access_pattern = re.search(r'access pattern:\s+(.+)', text).group(1).strip()
        self.use_hugepage = int(re.search(r'use hugepage:\s+(\d+)', text).group(1))
        self.target_duration = int(re.search(r'target duration:\s+(\d+)', text).group(1))

        # 提取 Idle Latency 数据
        lines = text.splitlines()
        latency_start = False
        for line in lines:
            if 'Idle Latency (ns)' in line:
                latency_start = True
                continue
            if latency_start:
                parts = line.split()
                if parts:
                    node_name = parts[0]
                    latencies = list(map(float, parts[1:]))
                    self.idle_latency[node_name] = latencies

    def __repr__(self) -> str:
        info_str = ""
        # print("Threads:", self.threads)
        # print("Region Size (KB):", self.region_size_kb)
        # print("Chunk Size (KB):", self.chunk_size_kb)
        # print("Stride Size (B):", self.stride_size_b)
        # print("Access Pattern:", self.access_pattern)
        # print("Use Hugepage:", self.use_hugepage)
        # print("Target Duration:", self.target_duration)
        # print("Idle Latency:", self.idle_latency)
        info_str += f"Threads: {self.threads}\n"
        info_str += f"Region Size (KB): {self.region_size_kb}\n"
        info_str += f"Chunk Size (KB): {self.chunk_size_kb}\n"
        info_str += f"Stride Size (B): {self.stride_size_b}\n"
        info_str += f"Access Pattern: {self.access_pattern}\n"
        info_str += f"Use Hugepage: {self.use_hugepage}\n"
        info_str += f"Target Duration: {self.target_duration}\n"
        info_str += f"Idle Latency: {self.idle_latency}\n"
        return info_str

class BandWidth:
    def __init__(self):
        self.threads = None
        self.region_size_kb = None
        self.read_write_mix = None
        self.target_duration = None
        self.peak_bandwidth = {}

    def parse(self, text: str):
        # 使用正则表达式提取基本信息
        self.threads = int(re.search(r'threads:\s+(\d+)', text).group(1))
        self.region_size_kb = int(re.search(r'region size in KB:\s+(\d+)', text).group(1))
        self.read_write_mix = re.search(r'read/write mix:\s+(\d+)', text).group(1).strip()
        # 0 - all reads
        # 1 - 1:1 read/write
        # 2 - 2:1 read/write
        # 3 - 3:1 read/write
        if self.read_write_mix == '0':
            self.read_write_mix = 'all reads'
        elif self.read_write_mix == '1':
            self.read_write_mix = '1:1 read/write'
        elif self.read_write_mix == '2':
            self.read_write_mix = '2:1 read/write'
        elif self.read_write_mix == '3':
            self.read_write_mix = '3:1 read/write'
        self.target_duration = int(re.search(r'target duration:\s+(\d+)', text).group(1))
        
        # 提取 Peak Bandwidth 数据
        lines = text.splitlines()
        bandwidth_start = False
        node_names = []
        
        for line in lines:
            if 'Peak Bandwidth (GB/s)' in line:
                bandwidth_start = True
                continue
            if bandwidth_start:
                parts = line.split()
                if 'Node' in line and len(parts) == 5:
                    node_name = parts[0]
                    node_bandwidths = list(map(float, parts[1:]))
                    self.peak_bandwidth[node_name] = node_bandwidths


def parse_idle_latency_output(stdout: str):
    # 创建对象并解析文本
    print(stdout)
    idle_latency = LatencyIdle()
    idle_latency.parse(stdout)
    return idle_latency

def parse_bandwidth_output(stdout: str):
    print(stdout)
    bandwidth = BandWidth()
    bandwidth.parse(stdout)
    return bandwidth

def parse_loaded_latency_output(stdout: str):
    ...