import os
from pydub import AudioSegment
from deepgram import Deepgram
import json
from datetime import datetime
import pandas as pd
import string
import inflect
import shutil
import logging
import asyncio
import excelComparision as ec
import subprocess


DEEPGRAM_API_KEY = 'e6a85dbec9ab2cb5540e9b0e33106743c64a46fa'

def convert_mp3_to_wav_ffmpeg(mp3_file, output_folder):
    try:
        # Define the output WAV file path
        wav_file = os.path.splitext(os.path.basename(mp3_file))[0] + ".wav"
        output_path = os.path.join(output_folder, wav_file)

        # Command to convert MP3 to WAV using ffmpeg
        command = ['ffmpeg', '-y', '-i', mp3_file, '-ac', '1', '-ar', '8000', output_path]


        # Run the ffmpeg command
        subprocess.run(command, check=True)

        logging.info("Conversion successful: {} -> {}".format(mp3_file, output_path))

        return output_path

    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting {mp3_file} to WAV: {e}")
        return None


def convert_mp3_files_in_folder(folder_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # Search for MP3 and WAV files in the specified folder only
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".mp3"):
            mp3_file = os.path.join(folder_path, file_name)
            converted_file = convert_mp3_to_wav_ffmpeg(mp3_file, output_folder)
            if converted_file:
                logging.info(f"Converted {mp3_file} to {converted_file}")
            else:
                logging.error(f"Failed to convert {mp3_file}")
        if file_name.endswith(".wav"):
            logging.info("Copying to folder {} since it is already in .wav file format".format(output_folder))
            wav_file = os.path.join(folder_path, file_name)
            destination = os.path.join(output_folder, file_name)
            if os.path.abspath(wav_file) != os.path.abspath(destination):
                shutil.copy(wav_file, destination)
            else:
                logging.info("There is already a file existing with same name for file : {} ".format(wav_file))


def convert_to_8000hz(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # Search for WAV files in the specified folder only
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(".wav"):
            wav_file = os.path.join(input_folder, file_name)
            output_file = os.path.join(output_folder, file_name)
            convert_and_resample(wav_file, output_file)
def convert_and_resample(input_file, output_file, target_rate=8000):
    # Load the audio file
    audio = AudioSegment.from_wav(input_file)
    # Convert stereo to mono
    if audio.channels > 1:
        audio = audio.set_channels(1)
    # Check the sampling rate
    current_rate = audio.frame_rate
    # If the sampling rate is greater than the target rate, resample
    if current_rate != target_rate:
        audio = audio.set_frame_rate(target_rate)
    # Export the audio to the output file
    audio.export(output_file, format="wav")
    logging.info("Exporting file {}".format(output_file))


def save_transcripts_to_text_files(root_folder):
    # Search for JSON files in the specified folder only
    for file_name in os.listdir(root_folder):
        if file_name.endswith(".json"):
            # Path to the JSON file
            json_file = os.path.join(root_folder, file_name)
            logging.info("Transcript from file:{}".format(json_file))
            # Read and save the transcript from the JSON file to a text file
            save_transcript(json_file)


async def transcribe_wav_files(folder_path):
    try:
        # Create a Deepgram client using the API key
        deepgram = Deepgram(DEEPGRAM_API_KEY)
        # Search for WAV files in the specified folder only
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".wav"):
                # Path to the WAV file
                audio_file = os.path.join(folder_path, file_name)
                with open(audio_file, "rb") as file:
                    buffer_data = file.read()
                source = {
                    'buffer': buffer_data,
                    'mimetype': 'audio/wav'
                }
                # Configure Deepgram options for audio analysis
                options = {
                    'model': 'nova-2',
                    'punctuate': True
                }
                # Send the audio to Deepgram for transcription
                response = await deepgram.transcription.prerecorded(source, options)
                # Save the transcription results to a JSON file in the same folder
                output_file = os.path.splitext(audio_file)[0] + ".json"
                with open(output_file, "w") as output:
                    json.dump(response, output, indent=4)
                logging.info("Transcription for {} saved to {}".format(audio_file, output_file))
    except Exception as e:
        logging.info("Exception: {}".format(e))


def save_transcript(transcription_file):
    with open(transcription_file, "r") as file:
        data = json.load(file)
        transcript = data['results']['channels'][0]['alternatives'][0]['transcript']
    # Construct the path for the text file
    text_file_path = os.path.splitext(transcription_file)[0] + ".txt"
    # Write transcript to the text file
    with open(text_file_path, "w") as text_file:
        text_file.write(transcript)
    logging.info("Transcript saved to: {}".format(text_file_path))

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
    logging.info("WER: {}".format(wer_score))
    logging.info("Inserted:{}".format(inserted))
    logging.info("Deleted:{}".format(deleted))
    logging.info("Substituted:{}".format(substituted))
    return wer_score, substituted, inserted, deleted

def save_data_to_excel(data, excel_file):
    # Create a DataFrame from the data
    df = pd.DataFrame(data)
    # Save the DataFrame to the new Excel file
    df.to_excel(excel_file, index=False)
    logging.info("Data saved to {}".format(excel_file))

def read_sentences(ref_path, hyp_path):
    # Read reference and hypothesis sentences from files
    with open(ref_path, 'r', encoding='iso-8859-1') as f:
        reference_sentence = f.read()
    with open(hyp_path, 'r', encoding='iso-8859-1') as f:
        hypothesis_sentence = f.read()
    return reference_sentence, hypothesis_sentence


def is_wav_8000hz(file_path):
    audio = AudioSegment.from_wav(file_path)
    return audio.frame_rate == 8000


def customize_audioTotext(rawFile, convertedFile):
    convert_mp3_files_in_folder(rawFile, convertedFile)
    for root, dirs, files in os.walk(convertedFile):
        for file in files:
            if file.endswith(".wav"):
                wav_file = os.path.join(root, file)
                if not is_wav_8000hz(wav_file):
                    convert_to_8000hz(convertedFile, convertedFile)
                    break
    asyncio.run(transcribe_wav_files(convertedFile))
    save_transcripts_to_text_files(convertedFile)


def generate_difference(convertedSourceFile, convertedSynFile):
    gender = ''
    hyp_folder = convertedSynFile
    hyp_files = [file for file in os.listdir(hyp_folder) if file.endswith('.txt')]
    ref_folder = convertedSourceFile
    if not convertedSourceFile:
        if 'female' in hyp_files[0].lower():
            ref_folder = "All source\\Female\\convertedSource"
            logging.info("Fetching Female converted files")
            gender = 'Female'
        elif 'male' in hyp_files[0].lower():
            ref_folder = "All source\\Male\\convertedSource"
            logging.info("Fetching Male converted files")
            gender = 'Male'
        else:
            logging.error("Converted source folder is not found and even default source folder is also missing")
    ref_files = [file for file in os.listdir(ref_folder) if file.endswith('.txt')]
    data = []
    for ref_file in ref_files:
        ref_file_name = ref_file.split('.txt')[0]
        check = ref_file_name
        for hyp_file in hyp_files:
            if ref_file_name in hyp_file:
                logging.info("comparing synth {} with source {}".format(hyp_file,ref_file))
                print("comparing synth {} with source {}".format(hyp_file,ref_file))
                ref_path = os.path.join(ref_folder, ref_file)
                hyp_path = os.path.join(hyp_folder, hyp_file)
                reference_sentence, hypothesis_sentence = read_sentences(ref_path, hyp_path)
                wer_score, substituted, inserted, deleted = compare_files(reference_sentence, hypothesis_sentence)
                data.append({'Reference File': ref_file, 'Hypothesis File': hyp_file, 'WER': wer_score,
                             'Inserted': ' '.join(inserted), 'Deleted': ' '.join(deleted),
                             'Substituted': ', '.join([' '.join(sub) for sub in substituted]),
                             'Reference Text': reference_sentence, 'Hypothesis Text': hypothesis_sentence})
                check = hyp_file
                break
        if check == ref_file_name:
            logging.error("Synth file {} does not match any source file".format(check))
            print("Synth file {} does not match any source file".format(check))
    return data, gender


def main(sourceFile, convertedSourceFile, synFile, convertedSynFile, ):
    if not convertedSynFile:
        convertedSynFile = synFile + '\\convertedSynFile'
    if sourceFile:
        if not convertedSourceFile:
            convertedSourceFile = sourceFile + '\\convertedSource'
        customize_audioTotext(sourceFile, convertedSourceFile)
    else:
        if not os.path.isdir("All source"):
            logging.error("Source directory is not mentioned and Default source directory is also missing")
    customize_audioTotext(synFile, convertedSynFile)
    excel_file = "Report_Source__" + str(sourceFile.split('\\')[-1] + '_SynFile__') + str(
        synFile.split('\\')[-1]) + datetime.now().strftime('_log_Report%Y%m%d_%H%M%S.xlsx')
    data, gender = generate_difference(convertedSourceFile, convertedSynFile)
    save_data_to_excel(data, excel_file)
    return excel_file, gender

if __name__ == "__main__":

    #Input Data
    sourceFile = ""
    convertedSourceFile = ''
    synFile = "C:\\Users\\RaghavKR\\Downloads\\AWS_Synth_RecordingsFemale_709\\extractedRecordingsFemale"
    convertedSynFile = ''
    compare_model = '410'

    # Logging File creation
    log_filename = "Report_Source__" + str(sourceFile.split('\\')[-1] + '_SynFile__') + str(synFile.split('\\')[-1])
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

    # Create logger
    logger = logging.getLogger(__name__)

    excel_file, gender = main(sourceFile, convertedSourceFile, synFile, convertedSynFile)
    model_path = "All model WER\\" + compare_model + "\\" + gender
    model_excel_file = [os.path.join(model_path, file) for file in os.listdir(model_path) if file.endswith('.xlsx')]
    ec.main(excel_file, str(model_excel_file[0]))
