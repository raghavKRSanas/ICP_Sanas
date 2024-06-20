import os
from pydub import AudioSegment
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import json
from datetime import datetime
import pandas as pd
import string
import inflect
import shutil
import logging


def convert_mp3_to_wav(mp3_file, output_folder):
    # Load the MP3 file
    audio = AudioSegment.from_mp3(mp3_file)
    # Define the output WAV file path
    wav_file = os.path.splitext(mp3_file)[0] + ".wav"
    output_path = os.path.join(output_folder, os.path.basename(wav_file))
    # Export the audio to WAV format
    audio.export(output_path, format="wav")
    logging.info(f"Conversion successful: {mp3_file} -> {output_path}")


def convert_mp3_files_in_folder(folder_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".mp3"):
                mp3_file = os.path.join(root, file)
                convert_mp3_to_wav(mp3_file, output_folder)
            if file.endswith(".wav"):
                logging.info("Copying to folder {} since it is already in .wav file format".format(output_folder))
                wav_file = os.path.join(root, file)
                destination = os.path.join(output_folder, file)
                if os.path.abspath(wav_file) != os.path.abspath(destination):
                    shutil.copy(wav_file, destination)
                else:
                    logging.info("There is already a file existing with same name for file : {} ".format(wav_file))


def convert_to_8000hz(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # Recursively search for WAV files in the input folder and its subfolders
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(".wav"):
                wav_file = os.path.join(root, file)
                output_file = os.path.join(output_folder, file)
                convert_and_resample(wav_file, output_file)


def convert_and_resample(input_file, output_file, target_rate=8000):
    # Load the audio file
    audio = AudioSegment.from_wav(input_file)
    # Convert stereo to mono
    audio = audio.set_channels(1)
    # Check the sampling rate
    current_rate = audio.frame_rate
    # If the sampling rate is greater than the target rate, resample
    if current_rate != target_rate:
        audio = audio.set_frame_rate(target_rate)
    # Export the audio to the output file
    audio.export(output_file, format="wav")
    logging.info("Exporting file {}".format(output_file))


def transcribe_wav_files(folder_path):
    try:
        # Create a Deepgram client using the API key
        deepgram = DeepgramClient("e6a85dbec9ab2cb5540e9b0e33106743c64a46fa")
        # Iterate over all files and folders in the given folder path
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                if file_name.endswith(".wav"):
                    # Path to the WAV file
                    audio_file = os.path.join(root, file_name)
                    with open(audio_file, "rb") as file:
                        buffer_data = file.read()
                    payload: FileSource = {
                        "buffer": buffer_data,
                    }
                    # Configure Deepgram options for audio analysis
                    options = PrerecordedOptions(
                        model="nova-2",
                        smart_format=False,
                    )
                    # Call the transcribe_file method with the text payload and options
                    response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
                    # Save the transcription results to a JSON file in the same folder
                    output_file = os.path.splitext(audio_file)[0] + ".json"
                    with open(output_file, "w") as output:
                        json.dump(response.to_dict(), output, indent=4)
                    logging.info(f"Transcription for {audio_file} saved to {output_file}")
    except Exception as e:
        logging.info(f"Exception: {e}")


def save_transcripts_to_text_files(root_folder):
    # Traverse the directory structure recursively
    for root, dirs, files in os.walk(root_folder):
        for file_name in files:
            if file_name.endswith(".json"):
                # Path to the JSON file
                json_file = os.path.join(root, file_name)
                logging.info(f"Transcript from file: {json_file}")
                # Read and save the transcript from the JSON file to a text file
                save_transcript(json_file)


def save_transcript(transcription_file):
    with open(transcription_file, "r") as file:
        data = json.load(file)
        transcript = data['results']['channels'][0]['alternatives'][0]['transcript']
    # Construct the path for the text file
    text_file_path = os.path.splitext(transcription_file)[0] + ".txt"
    # Write transcript to the text file
    with open(text_file_path, "w") as text_file:
        text_file.write(transcript)
    logging.info(f"Transcript saved to: {text_file_path}")


def preprocess_sentence(sentence):
    # Convert the sentence to lowercase
    sentence = sentence.lower()
    # Remove punctuation
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
    # Convert numeric words to letters
    p = inflect.engine()
    words = sentence.split()
    for i, word in enumerate(words):
        if word.isdigit():
            words[i] = p.number_to_words(word)
    return ' '.join(words)


def wer(ref, hyp):
    # Preprocess reference and hypothesis sentences
    ref = preprocess_sentence(ref)
    hyp = preprocess_sentence(hyp)
    # Split the reference and hypothesis sentences into words
    ref_words = ref.split()
    hyp_words = hyp.split()
    # Initialize a matrix to store edit distances
    dp = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    # Fill the first row and column of the matrix
    for i in range(len(ref_words) + 1):
        dp[i][0] = i
    for j in range(len(hyp_words) + 1):
        dp[0][j] = j
    # Calculate edit distances
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1]) + 1
    # Calculate the Word Error Rate
    wer = dp[-1][-1] / len(ref_words)
    # Initialize lists to store inserted, deleted, and substituted words
    inserted = []
    deleted = []
    substituted = []
    # Traceback to find inserted, deleted, and substituted words
    i = len(ref_words)
    j = len(hyp_words)
    while i > 0 or j > 0:
        if i > 0 and j > 0 and ref_words[i - 1] == hyp_words[j - 1]:
            i -= 1
            j -= 1
        else:
            if i > 0 and (j == 0 or dp[i][j] == dp[i - 1][j] + 1):
                deleted.append(ref_words[i - 1])
                i -= 1
            elif j > 0 and (i == 0 or dp[i][j] == dp[i][j - 1] + 1):
                inserted.append(hyp_words[j - 1])
                j -= 1
            else:
                substituted.append((ref_words[i - 1], hyp_words[j - 1]))
                i -= 1
                j -= 1
    return wer, substituted, inserted, deleted


def compare_files(ref_text, hyp_text):
    # Calculate WER and get detailed information
    wer_score, substituted, inserted, deleted = wer(ref_text, hyp_text)
    # logging.info WER and detailed information
    logging.info("WER:", wer_score)
    logging.info("Inserted:", inserted)
    logging.info("Deleted:", deleted)
    logging.info("Substituted:", substituted)
    return wer_score, substituted, inserted, deleted


def save_data_to_excel(data, excel_file):
    # Create a DataFrame from the data
    df = pd.DataFrame(data)
    # Save the DataFrame to the new Excel file
    df.to_excel(excel_file, index=False)
    logging.info("Data saved to", excel_file)




def main():
    # sourceFile = "C:\\Users\\RaghavKR\\Desktop\\Testing1\\Male\\Male"
    # convertedSourceFile = 'C:\\Users\\RaghavKR\\Desktop\\Testing1\\convertedSource'
    # synFile = "C:\\Users\\RaghavKR\\Desktop\\Testing1\\extracted_recordings_Male\\extracted_recordings"
    # convertedSynFile = 'C:\\Users\\RaghavKR\\Desktop\\Testing1\\convertedSyn'

    sourceFile = "C:\\Users\\RaghavKR\\Desktop\\Testing_Female\\Female\\Femal_"
    convertedSourceFile = 'C:\\Users\\RaghavKR\\Desktop\\Testing_Female\\convertedSource'
    synFile = "C:\\Users\\RaghavKR\\Desktop\\Testing_Female\\extracted_recording"
    convertedSynFile = 'C:\\Users\\RaghavKR\\Desktop\\Testing_Female\\convertedSyn'

    log_filename = "Report_Source__" + str(sourceFile.split('\\')[-1] + '_SynFile__') + str(synFile.split('\\')[-1])
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler(log_filename), logging.StreamHandler()])
    logger = logging.getLogger(__name__)

    convert_mp3_files_in_folder(sourceFile, convertedSourceFile)
    convert_mp3_files_in_folder(synFile, convertedSynFile)
    convert_to_8000hz(convertedSourceFile, convertedSourceFile)
    convert_to_8000hz(convertedSynFile, convertedSynFile)
    transcribe_wav_files(convertedSynFile)
    save_transcripts_to_text_files(convertedSynFile)
    transcribe_wav_files(convertedSourceFile)
    save_transcripts_to_text_files(convertedSourceFile)
    ref_folder = convertedSourceFile
    hyp_folder = convertedSynFile
    excel_file = "Report_Source__" + str(sourceFile.split('\\')[-1] + '_SynFile__') + str(synFile.split('\\')[-1]) + datetime.now().strftime('_log_Report%Y%m%d_%H%M%S.xlsx')
    ref_files = [file for file in os.listdir(ref_folder) if file.endswith('.txt')]
    hyp_files = [file for file in os.listdir(hyp_folder) if file.endswith('.txt')]
    assert len(ref_files) == len(hyp_files), "Number of files in reference and hypothesis folders must be the same."
    data = []
    for ref_file, hyp_file in zip(ref_files, hyp_files):
        ref_path = os.path.join(ref_folder, ref_file)
        hyp_path = os.path.join(hyp_folder, hyp_file)
        # Read reference and hypothesis sentences from files
        with open(ref_path, 'r', encoding='iso-8859-1') as f:
            reference_sentence = f.read()
        with open(hyp_path, 'r', encoding='iso-8859-1') as f:
            hypothesis_sentence = f.read()
        wer_score, substituted, inserted, deleted = compare_files(reference_sentence, hypothesis_sentence)
        data.append({'Reference File': ref_file, 'Hypothesis File': hyp_file, 'WER': wer_score,
                     'Inserted': ' '.join(inserted), 'Deleted': ' '.join(deleted),
                     'Substituted': ', '.join([' '.join(sub) for sub in substituted]),
                     'Reference Text': reference_sentence, 'Hypothesis Text': hypothesis_sentence})
    # Save data to Excel
    save_data_to_excel(data, excel_file)


if __name__ == "__main__":
    main()
