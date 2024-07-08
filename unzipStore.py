import os
import time
import zipfile
import shutil
import logging
import glob
import time


def unzip_latest_folder(source_dir, destination_dir, new_wav_name, allFiles):
    zip_files = glob.glob(os.path.join(source_dir, '*.zip'))
    time.sleep(5)
    latest_zip_file = max(zip_files, key=os.path.getmtime)
    if latest_zip_file in allFiles:
        logging.info("Retrying to find the zip folder after 5 seconds")
        time.sleep(5)
        latest_zip_file = max(zip_files, key=os.path.getmtime)
    print("latest file found {} ".format(latest_zip_file))
    zip_files.sort(key=lambda x: os.path.getmtime(os.path.join(source_dir, x)), reverse=True)
    latest_zip_file = os.path.join(source_dir, zip_files[0])
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    with zipfile.ZipFile(latest_zip_file, 'r') as zip_ref:
        zip_ref.extractall(destination_dir)
    logging.info("Latest zip file '{}' extracted to '{}'.".format(latest_zip_file, destination_dir))
    mp3_files = [f for f in os.listdir(destination_dir) if f.endswith('.mp3')]
    if mp3_files:
        latest_mp3_file = max(mp3_files, key=lambda x: os.path.getmtime(os.path.join(destination_dir, x)))
        new_file_path = os.path.join(destination_dir, new_wav_name + '.mp3')
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
            print(f"Existing file '{new_file_path}' removed.")
        os.rename(os.path.join(destination_dir, latest_mp3_file), new_file_path)
        print(f"Latest .mp3 file renamed to '{new_wav_name}.mp3' in the location {destination_dir}")
    else:
        logging.error("No .mp3 files found in the destination directory.")
    return latest_zip_file

def rename_and_move_latest_file(source_dir, destination_dir, new_wav_name, fileExt):
    os.makedirs(destination_dir, exist_ok=True)
    files = [os.path.join(source_dir, f) for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
    latest_file = max(files, key=os.path.getmtime)
    destination_path = os.path.join(destination_dir, new_wav_name + fileExt)
    shutil.copy(latest_file, destination_path)




# source_directory = "C:\\Users\\RaghavKR\\Downloads\\recordings"
# destination_directory = "C:\\Users\\RaghavKR\\Downloads\\extracted_recordings"
# new_wav_name = 'new_name'
# unzip_latest_folder(source_directory, destination_directory, new_wav_name)
