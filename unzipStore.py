import os
import zipfile
import shutil


def unzip_latest_folder(source_dir, destination_dir, new_wav_name):
    zip_files = [file for file in os.listdir(source_dir) if file.endswith('.zip')]
    if not zip_files:
        print("No zip files found in the source directory.")
        return
    zip_files.sort(key=lambda x: os.path.getmtime(os.path.join(source_dir, x)), reverse=True)
    latest_zip_file = os.path.join(source_dir, zip_files[0])
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    with zipfile.ZipFile(latest_zip_file, 'r') as zip_ref:
        zip_ref.extractall(destination_dir)
    print(f"Latest zip file '{latest_zip_file}' extracted to '{destination_dir}'.")
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
        print("No .mp3 files found in the destination directory.")


# source_directory = "C:\\Users\\RaghavKR\\Downloads\\recordings"
# destination_directory = "C:\\Users\\RaghavKR\\Downloads\\extracted_recordings"
# new_wav_name = 'new_name'
# unzip_latest_folder(source_directory, destination_directory, new_wav_name)



