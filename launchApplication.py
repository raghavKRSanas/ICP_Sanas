import ctypes

#Run this command in cmd with admin access and restart to remove UAC
#cmd = 'reg.exe ADD HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA /t REG_DWORD /d 0 /f'


def launchAPP(app_path):
    app_path = r"C:\Program Files\Sanas.ai\Sanas Accent Translator\Sanas.AccentConverter.exe"
    ctypes.windll.shell32.ShellExecuteW(None, "runas", app_path, None, None, 1)



