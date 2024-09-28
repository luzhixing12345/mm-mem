
import paperplotlib as ppl
import os
import re
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
    graph.save('results/idle_latency.png')

    
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
    graph.save('results/bandwidth.png')
    
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
    graph.save('results/loaded_latency.png')

def parse_output(filename: str, parse_func):
    
    with open(os.path.join('results', filename), 'r') as fp:
        text = fp.read()

    # split by [start]\n{...}[end]\n
    pattern = r"\[start\]\n(.*?)\n\[end\]\n"
    pure_results = re.findall(pattern, text, re.DOTALL)
    results = []
    for pure_result in pure_results:
        result = parse_func(pure_result)
        results.append(result)
    return results

def main():
    
    if not os.path.exists('results'):
        print("results not exist, please ./run.sh first")
        exit()
    
    idle_latency_results = parse_output("cpu_idle_latency.txt", parse_idle_latency_output)
    bandwidth_results = parse_output("cpu_peak_bandwidth.txt", parse_bandwidth_output)
    # loaded_latency_results = parse_output("cpu_loaded_latency.txt", parse_loaded_latency_output)
    
    draw_idle_latency(idle_latency_results)
    draw_bandwidth(bandwidth_results)
    # draw_loaded_latency(loaded_latency_results)
    
    
if __name__ == "__main__":
    main()