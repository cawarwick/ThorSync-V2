import h5py
import csv
import os
import numpy as np

def downsample(data, original_fs, target_fs):
    # Calculate the downsample factor
    downsample_factor = int(original_fs / target_fs)
    
    # Generate the original and target time vectors
    original_time = np.arange(0, len(data) / original_fs, 1 / original_fs)
    target_time = np.arange(0, len(data) / original_fs, 1 / target_fs)
    
    # Use numpy's interp function to downsample the data
    downsampled_data = np.interp(target_time, original_time, data.flatten())
    
    return downsampled_data

def save_selected_datasets_to_csv(file_path, target_fs=1000): ##change this to be your desired frame rate. The list of selected datasets will need to match Thorsync exactly.
    selected_datasets = [
        "AI/E_Stim",
        "AI/M_Force",
        "AI/M_Length",
        "AI/Pedal",
        "AI/Pelt_Temp",
        #"AI/PiezoMonitor",
        #"AI/PockelsMonitor",
        "DI/2pFrames",
        #"DI/CaptureActive",
        "DI/PandaFrames",
        "CI/FrameCounter"
    ]

    try:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file_name = f"{base_name}_selected_datasets.csv"

        with h5py.File(file_path, 'r') as h5_file:
            # Downsample all selected datasets and organize into a NumPy array
            downsampled_data = []
            time_values = None

            for dataset_name in selected_datasets:
                item = h5_file[dataset_name]
                data = item[:]
                original_fs = 1000.0  # Replace with the actual sampling frequency of your data
                downsampled_data.append(downsample(data, original_fs, target_fs))

                # Save time values only once (assuming all datasets have the same length)
                if time_values is None:
                    time_values = np.arange(0, len(downsampled_data[-1]) / target_fs, 1 / target_fs)

            # Transpose the array to have time in the first column and each dataset in subsequent columns
            downsampled_data = np.column_stack([time_values] + downsampled_data)

            # Filter rows based on the condition in the DI_2pFrames column
            mask = downsampled_data[:, selected_datasets.index("DI/2pFrames") + 1] >= 0.5
            downsampled_data = downsampled_data[mask]

            # Regenerate time values starting from 0 with the appropriate sampling rate
            downsampled_data[:, 0] = np.arange(0, len(downsampled_data) / target_fs, 1 / target_fs)

            # Write the NumPy array to a CSV file with the original file name
            header_row = ["Time"] + [dataset.replace('/', '_') for dataset in selected_datasets]
            
            output_file_name=(directory_path+base_name+".csv")
            np.savetxt(output_file_name, downsampled_data, delimiter=",", header=",".join(header_row), comments="")
            #np.savetxt(output_file_name, downsampled_data, delimiter=",", header=",".join(header_row), comments="")
            print(f"CSV file '{output_file_name}' created.")
                
    except Exception as e:
        print(f"Error: {e}")

def process_directory(directory_path):
    # Iterate through all .h5 files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".h5"):
            file_path = os.path.join(directory_path, filename)
            save_selected_datasets_to_csv(file_path)

if __name__ == "__main__":
    directory_path = "Y:/DRGS project/#540 3-19-25/3-19-25 #540/Time Lapse/ThorSync/Raw/"  # Replace with the path to your directory containing .h5 files
    process_directory(directory_path)
