import os
import csv
import numpy as np
import pandas as pd
#from scipy.signal import savgol_filter
import scipy.signal as signal

# Function to process a single CSV file
# Set the scaling factor. This is emperically calculated and isn't linear across the force range, but 1-16-24 had 30x scaling as a good approximation.
def process_file(csv_file, output_dir, threshold=.2, window_length=11, polyorder=0, scaling_factor=30):
    data = pd.read_csv(csv_file).values
    time_series = data[:, 0]
    data_series = data[:, 1]

    # Parameters  for lowpass filtering
    fs = 1000  # Sampling frequency in Hz
    cutoff = 40  # Hz (cutoff frequency for filtering). 20hz started to affect the square wave, so 40-100hz is a good range.
    order = 4  # Filter order

    # Design low-pass Butterworth filter
    nyquist = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = signal.filtfilt(b, a, data_series)
    
    # Save the lowpass filtered data to a CSV
    #LP_Filtered_Force = pd.DataFrame({'Time': time_series[:], 'LP_Filt': filtered_data})
    #LP_Force_filename = os.path.join(output_dir, f'LP_Filt{os.path.basename(csv_file)}')
    #P_Filtered_Force.to_csv(LP_Force_filename, index=False)

      # Find peaks in the derivative

    threshold = 0.1
    min_duration = 100 ##this is in frames of input data, so if 1khz sampling rate this is 100ms minimum 
    scaling_factor = 40  # Scaling factor for the median value. e.g. it's to convert the volts to mN of force. ~40 is ok, but not quite linear.

    above_threshold = filtered_data > threshold

    # Find where the data transitions above the threshold
    starts = np.where(np.diff(above_threshold.astype(int)) == 1)[0] + 1
    ends = np.where(np.diff(above_threshold.astype(int)) == -1)[0] + 1

    if above_threshold[0]:
        starts = np.insert(starts, 0, 0)  # Case where we start above the threshold
    if above_threshold[-1]:
        ends = np.append(ends, len(filtered_data))  # Case where we end above the threshold

    results = []
    for start, end in zip(starts, ends):
        if (end - start) >= min_duration:
            median_value = np.median(filtered_data[start:end]) * scaling_factor  # Apply scaling factor
            results.append([median_value, time_series[start], time_series[end]])

    results_array = np.array(results)
    #print("Results array (median, start, end):")
    #print(results_array)
    # Save results to CSV

    # Specify the directory to save the file
    save_directory = output_dir  # Replace with your desired directory path

    # Full path for the CSV file
    new_name="peaks_"+filename
    csv_file_path = os.path.join(save_directory, new_name)
    
    # Save results to CSV
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Median mN', 'Start', 'End'])  # Write header row
        writer.writerows(results_array)  # Write the data rows

    print(f"Results saved to '{csv_file_path}'.")

###################################################

# Directory containing input CSV files
input_dir = 'Y:/DRGS project/#540 3-19-25/3-19-25 #540/Time Lapse/ThorSync/Raw/Force Only/'  # Replace with your input directory
output_dir = input_dir+'/output/'  # Replace with your output directory

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Iterate over all CSV files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.csv'):
        csv_file = os.path.join(input_dir, filename)
        process_file(csv_file, output_dir)

print("All files processed.")