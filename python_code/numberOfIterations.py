import os 
#Import os interacts with the operating system, used for file operations
import re
#useful for pattern matching
import matplotlib.pyplot as plt 
#plotting library
import seaborn as sns
#stat analysis library
import pandas as pd
#data manipulation 
import numpy as np
import seaborn.objects as so
import pandas.plotting as table
from scipy.stats import t as tdist,  median_abs_deviation as mad, ttest_1samp as t1

def get_sorted_files(folder_path, file_pattern):
    #define function get_sorted_file swhich takes folder_path and file_pattern as inputs
    files = os.listdir(folder_path)
    #retrieves a list of all files and directories in the specified folder path
    matched_files = [f for f in files if re.match(file_pattern, f)]
    #sorts through files in folder and retrieves a list of all files that match the specified file pattern
    sorted_files = sorted(matched_files, key=lambda x: (int(re.findall(r'\d+', x)[0]), int(re.findall(r'run(\d+)', x)[0])))
    #sorts the matched files, lambda is a pyython featuer that creates anonymous functions, it then extracts the numerical values in the filenames as a tuple(primary, secondary)
    return sorted_files

def process_file1(folder_path):
    #specifies file pattern
    #change to text_file pattern
    file_pattern = r'frontier_cores\d+_run\d+'  # Adjust the pattern as needed to match the specific files
    sorted_files = get_sorted_files(folder_path, file_pattern)
    #calls for get_sorted files function and assigns it to sorted_files
    results_front = {}
    
    for filename in sorted_files:
        #for each filename in sorted_files (loops through each item on the list)
        file_path = os.path.join(folder_path, filename)
        #joins folder path with file name to create the file path

        with open(file_path, 'r') as file:
            #opens file
            text = file.read()
            #saves text on file to text
            timers = {
                "Albany Piro": r'Piro::NOXSolver::evalModelImpl::solve: (\d+\.\d+)',
                "No of Linear Iterations": r'NOX Total Linear Solve: .* \[(\d+)\]',
                "No of NonLinear Iterations": r'Belos: Operation Prec\*x: .* \[(\d+)\]'
            }
            #specifies timers to extract (change if needed)
            extracted_timers = {timer_name: float(re.search(pattern, text).group(1)) if re.search(pattern, text) else None for timer_name, pattern in timers.items()}
            #create a dictionary with timers key as timer name and the timer value 
            filename_no_ext = filename.split(".")[0]
            #splits the filename .txt portion

            parts = filename_no_ext.split("_")
            #splits filename into 3 parts data - cores4 -run1
            core = int(parts[1].replace("cores", ""))
            #gets rid of "cores" and converts remaining number string to an integer
            run = int(parts[2].replace("run", ""))
            #gets rid of "runs" and converts remaining number string to an integer
            if core not in results_front:
                #Add core as a key in the dictionary if not there
                results_front[core] = {}
            if run not in results_front[core]:
                #Adds run as a nested dictionary under core key and creates and empty list to append the extracted timer values from the file (Piro, Albany, FIll, linsonve)
                results_front[core][run] = []
            results_front[core][run].append(extracted_timers)
    #print(results_front)
    return results_front

def process_data(data, label):
    for cores, runs in data.items():
        # Loop through core numbers, run numbers in dataset returned from process_files function
        for run, metrics in runs.items():
            record = metrics[0]
            record['Cores'] = cores
            record['Run'] = run
            record['Dataset'] = label  # Add a label to identify the dataset
            data_list.append(record)
            # Creates a dictionary named record that contains the values for the timers on each iteration of the loop and adds keys 'Cores' and "Run" to specify category
            # It then stores the


if __name__ == "__main__":
    folder_path = r'C:\Users\rcaller\Documents\GitHub\Performance-Regression-Plots\text_files\text_files_gpu_frontier'

    get_sorted_files(folder_path, r'frontier_cores\d+_run\d+')
    lost = process_file1(folder_path)
    #print(lost)


    data_list =[]

    process_data(lost, 'Frontier')
    df = pd.DataFrame(data_list)

    print(df)

    df['Linear/Nonlinear'] = np.floor(df['No of NonLinear Iterations'] / df['No of Linear Iterations'])
    
    #round down using np.floor to integer number for average number of iterations
    print((np.floor(np.mean(df['Linear/Nonlinear']))))
    print(df)

    avgIters = []
    for core in df['Cores'].unique():
        coreGroup = df[df['Cores'] == core]
        avgIterations = np.mean(coreGroup['Linear/Nonlinear'])
        avgIters.append({
            'Average Iterations': avgIterations,
            'Cores': core
        })
    #avgIters = df.groupby('Cores')['Linear/Nonlinear'].mean().tolist()
    print(avgIters)
    avgItersDf = pd.DataFrame(avgIters)
    print(avgItersDf)

    #use seaborn to make plot of Avg iterations for each node count
    # x-axis number of cores
    # y-axis avg iterations




