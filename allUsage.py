import psutil
import time

def bytes_to_mb(bytes):
    return bytes / (1024 * 1024)

def monitor_performance(duration, process_name="Sanas.AccentConverter.exe"):
    cpu_samples = []
    mem_samples = []
    net_samples = []
    disk_samples = []

    start_time = time.time()

    # Get the process ID for the given process name
    process = None
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            process = psutil.Process(proc.pid)
            break

    if not process:
        print(f"No process with name '{process_name}' found.")
        return

    while time.time() - start_time < duration:
        cpu_samples.append(process.cpu_percent())
        mem_info = process.memory_info()
        mem_samples.append(bytes_to_mb(mem_info.rss))  # Convert to MB
        net_usage = psutil.net_io_counters()
        net_samples.append(net_usage.bytes_sent + net_usage.bytes_recv)
        disk_usage = psutil.disk_usage('/')
        disk_samples.append(bytes_to_mb(disk_usage.used))  # Convert to MB

        print(f"Iteration {len(cpu_samples)}:")
        print(f"    CPU Usage: {cpu_samples[-1]}%")
        print(f"    Memory Usage: {mem_samples[-1]} MB")
        print(f"    Network Usage: {net_usage.bytes_sent + net_usage.bytes_recv} bytes")
        print(f"    Disk Usage: {disk_samples[-1]} MB")

        time.sleep(5)  # Adjusted sleep time for sampling every 1 second

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
#     duration = 180  # 60 seconds for 1-minute monitoring, adjust as needed
#     monitor_performance(process_name, duration)
