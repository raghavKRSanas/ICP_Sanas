import psutil


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


#appCpuUsage()







