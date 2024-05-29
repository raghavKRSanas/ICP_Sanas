import psutil
import time

def bytes_to_mb(bytes):
    return bytes / (1024 * 1024)

def get_normalized_cpu_percent(process):
    cpu_percent = process.cpu_percent(interval=2.0)
    logical_cpus = psutil.cpu_count()
    physical_cpus = psutil.cpu_count(logical=False)
    normalized_cpu_percent = (cpu_percent / logical_cpus) * 4
    return normalized_cpu_percent

def get_process_cpu_utilization(process_name):

    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            process = psutil.Process(proc.info['pid'])
            cpu_usage = get_normalized_cpu_percent(process)
            return proc.info['pid'], cpu_usage
    return None, None

def appCpuUsage():
    process_name = "Sanas.AccentConverter.exe"
    pid, cpu_usage = get_process_cpu_utilization(process_name)
    if pid is None:
        print(f"No process found with name {process_name}")
    return pid, cpu_usage

def monitor_performance( duration, process_name = "Sanas.AccentConverter.exe", timeInterval=10):
    cpu_samples = []
    mem_samples = []
    net_samples = []
    #disk_samples = []

    start_time = time.time()

    while time.time() - start_time < duration:
        processes = [proc for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info']) if proc.info['name'] == process_name]
        if processes:
            process = processes[0]
            if process.is_running():
                cpu_samples.append(process.cpu_percent())
                mem_info = process.memory_info()
                mem_samples.append(bytes_to_mb(mem_info.rss))  # Convert to MB
                net_usage = psutil.net_io_counters()
                net_samples.append(net_usage.bytes_sent + net_usage.bytes_recv)
                # disk_io = psutil.disk_io_counters()
                # disk_samples.append(bytes_to_mb(disk_io.read_bytes + disk_io.write_bytes))  # Convert to MB
                print(f"Instance {len(cpu_samples)}:")
                print(f"    CPU Usage: {cpu_samples[-1]}%")
                print(f"    Memory Usage: {mem_samples[-1]} MB")
                print(f"    Network Usage: {net_usage.bytes_sent + net_usage.bytes_recv} bytes")
                # print(f"    Disk Usage: {disk_samples[-1]} MB")
            else:
                print(f"Process '{process_name}' is not running.")
        else:
            print(f"No process with name '{process_name}' found.")

        time.sleep(timeInterval)  # Adjusted sleep time for sampling every 1 second

    avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
    peak_cpu = max(cpu_samples) if cpu_samples else 0
    low_cpu = min(cpu_samples) if cpu_samples else 0

    avg_mem = sum(mem_samples) / len(mem_samples) if mem_samples else 0
    peak_mem = max(mem_samples) if mem_samples else 0
    low_mem = min(mem_samples) if mem_samples else 0

    avg_net_usage = sum(net_samples) / (1024 * len(net_samples)) if net_samples else 0
    peak_net_usage = max(net_samples) / 1024 if net_samples else 0
    low_net_usage = min(net_samples) / 1024 if net_samples else 0

    # avg_disk_usage = sum(disk_samples) / len(disk_samples) if disk_samples else 0
    # peak_disk_usage = max(disk_samples) if disk_samples else 0
    # low_disk_usage = min(disk_samples) if disk_samples else 0

    print("\nFinal Summary:")
    print("CPU Usage:")
    print(f"    Average: {avg_cpu}%")
    print(f"    Peak: {peak_cpu}%")
    print(f"    Low: {low_cpu}%")
    print()

    print("Memory Usage:")
    print(f"    Average: {avg_mem} MB")
    print(f"    Peak: {peak_mem} MB")
    print(f"    Low: {low_mem} MB")
    print()

    print("Network Usage:")
    print(f"    Average: {avg_net_usage} KB")
    print(f"    Peak: {peak_net_usage} KB")
    print(f"    Low: {low_net_usage} KB")
    print()

    # print("Disk Usage:")
    # print(f"    Average: {avg_disk_usage} MB")
    # print(f"    Peak: {peak_disk_usage} MB")
    # print(f"    Low: {low_disk_usage} MB")
    # print()



# if __name__ == "__main__":
#     process_name = "Sanas.AccentConverter.exe"
#     duration = 60  # 60 seconds for 1-minute monitoring, adjust as needed
#     monitor_performance(process_name, duration)
