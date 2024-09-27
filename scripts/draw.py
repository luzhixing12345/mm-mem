
import paperplotlib as ppl
from parse_output import *

def hugepage_num2size(num):
    if num == 0:
        return "4KB"
    elif num == 1:
        return "2MB"
    elif num == 2:
        return "512GB"
    elif num == 3:
        return "1GB"
    else:
        return "16GB"

def draw_idle_latency(results: list[LatencyIdle]):
    
    graph = ppl.BarGraph()
    # 传入数据/组/列的文字信息
    cpu_node_num = len(results[0].idle_latency.keys())
    node_num = len(results[0].idle_latency['Node-0'])
    group_names = []
    for i in range(cpu_node_num):
        for j in range(node_num):
            group_names.append(f"{i}-{j}")
            
    column_names = []
    
    for result in results:
        column_names.append(hugepage_num2size(result.use_hugepage))
    
    datas = []
    for i in range(cpu_node_num):
        for j in range(node_num):
            data = []
            for result in results:
                data.append(result.idle_latency[f"Node-{i}"][j])
            datas.append(data)
    
    graph.plot_2d(datas, group_names, column_names)

    # 调整x/y轴文字
    graph.x_label = "Node A to Node B"
    graph.y_label = "idle latency(ns)"

    # 保存图片
    graph.save('idle_latency.png')

    
def draw_bandwidth(results: list[BandWidth]):
    
    graph = ppl.BarGraph()
    # 传入数据/组/列的文字信息
    cpu_node_num = len(results[0].peak_bandwidth.keys())
    node_num = len(results[0].peak_bandwidth['Node-0'])
    group_names = []
    for i in range(cpu_node_num):
        for j in range(node_num):
            group_names.append(f"{i}-{j}")
            
    column_names = []
    
    for result in results:
        column_names.append(result.read_write_mix)
    
    datas = []
    for i in range(cpu_node_num):
        for j in range(node_num):
            data = []
            for result in results:
                data.append(result.peak_bandwidth[f"Node-{i}"][j])
            datas.append(data)
    
    graph.plot_2d(datas, group_names, column_names)

    # 调整x/y轴文字
    graph.x_label = "Node A to Node B"
    graph.y_label = "peak bandwidth(GB/s)"

    # 保存图片
    graph.save('bandwidth.png')
    
def draw_loaded_latency(results: list[LatencyIdle]):
    
    graph = ppl.BarGraph()
    # 传入数据/组/列的文字信息
    cpu_node_num = len(results[0].keys())
    node_num = len(results[0].peak_bandwidth['Node-0'])
    group_names = []
    for i in range(cpu_node_num):
        for j in range(node_num):
            group_names.append(f"{i}-{j}")
            
    column_names = []
    
    for result in results:
        column_names.append(result.read_write_mix)
    
    datas = []
    for i in range(cpu_node_num):
        for j in range(node_num):
            data = []
            for result in results:
                data.append(result.peak_bandwidth[f"Node-{i}"][j])
            datas.append(data)
    
    graph.plot_2d(datas, group_names, column_names)

    # 调整x/y轴文字
    graph.x_label = "Node A to Node B"
    graph.y_label = "loaded latency(ns)"

    # 保存图片
    graph.save('loaded_latency.png')