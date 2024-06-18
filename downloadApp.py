import os
import subprocess
import requests
from tqdm import tqdm
import logging

# URL of the file to download
url = 'https://cdn-dev.sanas.ai/releases/v2-desktop-app/SanasAccentTranslator-V2-2.24.0604.27-phl-dev.exe'
download_dir = r"C:\Users\RaghavKR\Downloads\appdownload"

def downloadApp(url, download_dir):
    file_name = url.split('/')[-1]
    file_path = os.path.join(download_dir, file_name)

    # Ensure the download directory exists
    os.makedirs(download_dir, exist_ok=True)
    response = requests.head(url)
    file_size = int(response.headers.get('content-length', 0))

    # Make a GET request to download the file
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as file, tqdm(
                desc=file_name,
                total=file_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                bar.update(len(chunk))
        logging.info(f"File '{file_name}' has been downloaded successfully.")
    else:
        logging.info(f"Failed to download the file. Status code: {response.status_code}")


def installApp(url, download_dir):
    # Installation
    file_name = url.split('/')[-1]
    file_path = os.path.join(download_dir, file_name)
    command = f'"{file_path}" /q'
    try:
        subprocess.run(command, check=True, shell=True)
        logging.info("Installation completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.info(f"Installation failed with error: {e}")

