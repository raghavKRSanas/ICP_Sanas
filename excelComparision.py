import logging
import pandas as pd
import reportGen as rg

# Setup logging configuration
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


def getData(filePath):
    df = pd.read_excel(filePath)
    # Convert the DataFrame to a dictionary
    data_dict = df.to_dict(orient='list')

    # Keys to delete
    keys_to_delete = ['Inserted', 'Deleted', 'Substituted', 'Reference Text', 'Hypothesis Text', 'Reference File']

    # Delete the keys from the dictionary
    for key in keys_to_delete:
        if key in data_dict:
            del data_dict[key]

    # Create a new dictionary with required data
    converted_dict = {data_dict['Hypothesis File'][i]: data_dict['WER'][i] for i in
                      range(len(data_dict['Hypothesis File']))}

    # Extract model and app version from the file names
    first_key = next(iter(converted_dict))
    model_version = 'Unknown'
    app_version = 'Unknown'
    if 'modelVersion' in first_key:
        model_version = extract_version(first_key, '_modelVersion_', '.all')
    if '_appVersion_' in first_key:
        app_version = extract_version(first_key, '_appVersion_', '_modelVersion_')

    # Update keys in the dictionary
    updated_dict = {}
    for key, value in converted_dict.items():
        if '_appVersion' in key:
            new_key = key.split('_appVersion')[0] if '_appVersion' in key else key
        elif '.txt' in key:
            new_key = key.split('.txt')[0] if '.txt' in key else key
        else:
            new_key = key
        updated_dict[new_key] = value
    print(updated_dict)
    return updated_dict, model_version, app_version


def extract_version(filename, start_marker, end_marker):
    start_idx = filename.find(start_marker) + len(start_marker)
    end_idx = filename.find(end_marker, start_idx)
    return filename[start_idx:end_idx]


def main(file_path_mod1, file_path_mod2):
    # file_path_mod1 = 'C:\\Users\\RaghavKR\\Desktop\\Testing_Female\\410\\Report_Source__Female__SynFile__extracted_recording_log_Report20240619_141258.xlsx'
    # file_path_mod2 = 'C:\\Users\\RaghavKR\\Desktop\\option5,6,7\\option5,6,7\\option6\\Report_Source__Female_SynFile__extracted_recordingsFemale_option6_log_Report20240625_160603.xlsx'

    data_1, model_1, appVersion_1 = getData(file_path_mod1)
    data_2, model_2, appVersion_2 = getData(file_path_mod2)

    recording_names = data_1.keys()
    result = {}
    betterModel = {model_1: 0, model_2: 0}
    for name in recording_names:
        base_name = name.split('_appVersion')[0] if '_appVersion' in name else name

        if base_name in data_2 and base_name in data_1:
            wer_1 = float(data_1[base_name])
            wer_2 = float(data_2[base_name])
            if wer_1 > wer_2:
                diff = wer_1 - wer_2
                comment = f"WER is more in model: {model_1} app version {appVersion_1} by {diff:.2f} when compared to model: {model_2} appversion: {appVersion_2}"
                betterModel[model_2] += 1
                if round(diff, 2) == 0.0 or round(diff, 2) == 0.00:
                    comment = f"WER is same in model: {model_1} app version {appVersion_1} as model: {model_2} appversion: {appVersion_2}"
            elif wer_1 < wer_2:
                diff = wer_2 - wer_1
                comment = f"WER is more in model: {model_2} app version {appVersion_2} by {diff:.2f} when compared to model: {model_1} appversion: {appVersion_1}"
                betterModel[model_1] += 1
                if round(diff, 2) == 0.0 or round(diff, 2) == 0.00:
                    comment = f"WER is same in model: {model_1} app version {appVersion_1} as model: {model_2} appversion: {appVersion_2}"
            else:
                comment = "WER is the same in both models"

            result[base_name] = comment
        else:
            logging.error(f"Recording {base_name} is not found in both datasets")
    print(result)
    bestModel = max(betterModel, key=betterModel.get)
    rg.main(data_1, data_2, result, model_1, model_2, bestModel)


# if __name__ == "__main__":
#     main()

