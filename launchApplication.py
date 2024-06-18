import sys
import ctypes
import subprocess
import time

import psutil
import logging
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin(script):
    if not is_admin():
        # Re-run the script with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, script, None, 1)
        #sys.exit()


def check_if_app_running(app_name):
    for proc in psutil.process_iter(['name']):
        try:
            if app_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False




def cmdlauchApp(cmd_line=r'"C:\Program Files\Sanas.ai\Sanas Accent Translator\Sanas.AccentConverter.exe"'):
    subprocess.Popen(cmd_line, shell=True)
    logging.info("Application has launched")
    app_name = "Sanas"
    for i in range(3):
        if check_if_app_running(app_name):
            print(f"{app_name} is running.")
            break
        else:
            print(f"Checking again after 5sec")
            time.sleep(5)


#run_as_admin("applicationTesting.py")
