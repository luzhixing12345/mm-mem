import argparse
import os
import sys
from typing import Dict, List

from config_huge_page import *
from config_sysfs_settings import check_autonuma, setup_autonuma
from print_host_info import color_str, get_cpu_info, get_mem_info
from utils import read_env
import subprocess
from parse_output import parse_idle_latency_output, parse_bandwidth_output, parse_loaded_latency_output
from draw import *


def get_huge_page_mapping(size: int) -> int:
    if size == (2 << 10):
        return 1
    elif size == (512 << 10):
        return 2
    elif size == (1 << 20):
        return 3
    elif size == (16 << 20):
        return 4
    else:
        print(color_str(f"Unexpected huge page size of {size}kB", 31))
        return 0


def get_bin_path(test_name: str) -> str:
    return os.path.join(read_env()["ROOT"], "bin", test_name)


def run_idle_latency(huge_page_state: Dict[int, List[int]]):

    latency_results = []

    print(color_str("---- Running Idle Latency test ...", 32))
    sys.stdout.flush()
    # not using huge page
    cmd = [
        get_bin_path("cpu_idle_latency"),
        "--latency_matrix",
        "-t",
        str(args.target_duration),
    ]
    stdout = subprocess.check_output(" ".join(cmd), shell=True)
    basic_idle_latency = parse_idle_latency_output(stdout.decode("utf-8"))
    latency_results.append(basic_idle_latency)

    # using huge page
    print(color_str("---- Running Idle Latency test with huge pages ...", 32))
    huge_page_sizes = get_huge_page_sizes()
    for size in huge_page_sizes:
        print("using huge page size: ", human_read_pagesize(size))

        if setup_huge_pages(HugePageSize(size)) is False:
            print(color_str("Fail to setup huge pages", 31))
            continue

        cmd = [
            get_bin_path("cpu_idle_latency"),
            "--latency_matrix",
            "-t",
            str(args.target_duration),
            "-p",
            "2",
            "-H",
            str(get_huge_page_mapping(size)),
        ]
        stdout = subprocess.check_output(" ".join(cmd), shell=True)
        latency_results.append(parse_idle_latency_output(stdout.decode("utf-8")))
        reset_huge_pages(huge_page_state)

    return latency_results


def run_peak_bandwidth(num_numa_nodes: int):

    peak_bandwith_results = []

    print(color_str("---- Running Peak Bandwidth test ...", 32))
    sys.stdout.flush()
    cmd = [
        get_bin_path("cpu_peak_bandwidth"),
        "-t",
        str(args.target_duration),
    ]
    os.system(" ".join(cmd))
    if num_numa_nodes > 0:
        # 0 - all reads
        # 1 - 1:1 read/write
        # 2 - 2:1 read/write
        # 3 - 3:1 read/write
        bandwidth_types = {
            0: "all reads",
            1: "1:1 read/write",
            2: "2:1 read/write",
            3: "3:1 read/write",
        }

        for i, test_type in bandwidth_types.items():
            print(color_str(f"---- Running Peak Bandwidth test - {test_type} ...", 32))
            sys.stdout.flush()
            cmd = [
                get_bin_path("cpu_peak_bandwidth"),
                "--bandwidth_matrix",
                "-t",
                str(args.target_duration),
                "-m",
                str(i),
            ]
            stdout = subprocess.check_output(" ".join(cmd), shell=True)
            peak_bandwith_results.append(parse_bandwidth_output(stdout.decode("utf-8")))

    return peak_bandwith_results


def run_memcpy(num_numa_nodes: int):
    print(color_str("---- Running MemCpy test - Large ...", 32))
    sys.stdout.flush()
    cmd = [
        get_bin_path("cpu_memcpy"),
        "-t",
        str(args.target_duration),
    ]
    os.system(" ".join(cmd))
    print(color_str("---- Running MemCpy test - Medium ...", 32))
    sys.stdout.flush()
    cmd = [
        get_bin_path("cpu_memcpy"),
        "-t",
        str(args.target_duration),
        "-f",
        "16384",
    ]
    os.system(" ".join(cmd))


class AccessPattern(Enum):
    SEQUENTIAL = 0
    RANDOM_IN_CHUNK = 1
    RANDOM_IN_FULL_REGION = 2


def run_loaded_latency(huge_page_state: Dict[int, List[int]], access_pattern: AccessPattern):

    loaded_latency_results = []

    print(color_str("---- Running Loaded Latency test ...", 32))
    sys.stdout.flush()
    # not using huge page
    cmd = [
        get_bin_path("cpu_loaded_latency"),
        "-t",
        str(args.target_duration),
        "-p",
        str(access_pattern.value)
    ]

    stdout = subprocess.check_output(" ".join(cmd), shell=True)
    loaded_latency_results.append(parse_loaded_latency_output(stdout.decode("utf-8")))

    # using huge page
    print(color_str("---- Running Loaded Latency test with huge pages ...", 32))
    huge_page_sizes = get_huge_page_sizes()

    for size in huge_page_sizes:
        print("using huge page size: ", human_read_pagesize(size))

        if setup_huge_pages(HugePageSize(size)) is False:
            print(color_str("Fail to setup huge pages", 31))
            continue

        cmd = [
            get_bin_path("cpu_loaded_latency"),
            "-t",
            str(args.target_duration),
            "-p",
            str(access_pattern.value),
            "-H",
            str(get_huge_page_mapping(size)),
        ]

        stdout = subprocess.check_output(" ".join(cmd), shell=True)
        loaded_latency_results.append(parse_loaded_latency_output(stdout.decode("utf-8")))
        reset_huge_pages(huge_page_state)

    return loaded_latency_results


def init_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--target-duration", "-t", type=int, default=2, help="duration in seconds for each data point")
    parser.add_argument(
        "--test",
        action="append",
        default=None,
        choices=["idle_latency", "loaded_latency", "bandwidth"],
        help="selective run certain tests; default to run all",
    )
    return parser


def main(args):
    num_numa_nodes = get_cpu_info()
    get_mem_info(num_numa_nodes)
    huge_page_state = check_huge_pages(color_str("before", 33))
    autonuma_state = check_autonuma(color_str("before", 33))
    # change autonuma setting here and hugepage setting in each test
    if autonuma_state > 0:
        setup_autonuma(value=0)
    print(color_str("-------- Running MM-Mem --------", 35))
    sys.stdout.flush()
    if args.test is None or "idle_latency" in args.test:
        latency_results = run_idle_latency(huge_page_state)
        draw_idle_latency(latency_results)
    if args.test is None or "bandwidth" in args.test:
        peak_bandwidth_results = run_peak_bandwidth(num_numa_nodes)
        draw_bandwidth(peak_bandwidth_results)
        # run_memcpy(num_numa_nodes)
    if args.test is None or "loaded_latency" in args.test:
        latency_results = run_loaded_latency(huge_page_state)
        draw_loaded_latency(latency_results)
    if autonuma_state > 0:
        setup_autonuma(value=autonuma_state)


if __name__ == "__main__":
    parser = init_parser()
    args = parser.parse_args()
    main(args)
