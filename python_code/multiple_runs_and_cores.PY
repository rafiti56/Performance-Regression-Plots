import os 
#Import os interacts with the operating system, used for file operations
import re
#useful for pattern matching
import matplotlib.pyplot as plt 
#plotting library
import seaborn as sns
#stat analysis library
import pandas as pd
#data manipulation library

def get_sorted_files(folder_path, file_pattern):
    #define function get_sorted_file swhich takes folder_path and file_pattern as inputs
    files = os.listdir(folder_path)
    #retrieves a list of all files and directories in the specified folder path
    matched_files = [f for f in files if re.match(file_pattern, f)]
    #sorts through files in folder and retrieves a list of all files that match the specified file pattern
    sorted_files = sorted(matched_files, key=lambda x: (int(re.findall(r'\d+', x)[0]), int(re.findall(r'run(\d+)', x)[0])))
    #sorts the matched files, lambda is a pyython featuer that creates anonymous functions, it then extracts the numerical values in the filenames as a tuple(primary, secondary)
    return sorted_files

def process_files(folder_path):
    #specifies file pattern
    file_pattern = r'data_cores\d+_run\d+'  # Adjust the pattern as needed to match the specific files
    sorted_files = get_sorted_files(folder_path, file_pattern)
    #calls for get_sorted files function and assigns it to sorted_files
    results = {}
    
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
                "Total Fill Time": r'Albany: Total Fill Time: (\d+\.\d+)',
                "Precond": r'NOX Total Preconditioner Construction: (\d+\.\d+)',
                "Total Lin": r'NOX Total Linear Solve: (\d+\.\d+)',
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
            if core not in results:
                #Add core as a key in the dictionary if not there
                results[core] = {}
            if run not in results[core]:
                #Adds run as a nested dictionary under core key and creates and empty list to append the extracted timer values from the file (Piro, Albany, FIll, linsonve)
                results[core][run] = []
            results[core][run].append(extracted_timers)
    return results

def calculate_speedup_efficiency(df):
    single_core_times = df[df['Cores'] == 4].mean()
    df_speedup_efficiency = df.copy()
    
    timers = ['Albany Piro', 'Total Fill Time', 'Precond', 'Total Lin']
    for timer in timers:
        df_speedup_efficiency[f'{timer}_Speedup'] = single_core_times[timer] / df[timer]
        df_speedup_efficiency[f'{timer}_Efficiency'] = (df_speedup_efficiency[f'{timer}_Speedup'] / df['Cores']) * 100

    return df_speedup_efficiency

if __name__ == "__main__":
    folder_path = r'C:\Users\Rafael\OneDrive\Documents\GitHub\Performance-Regression-Plots\text_files'  # Update with path to folder containing run cases as text files
    data = process_files(folder_path)

    data_list = []
    for cores, runs in data.items():
        #loops through core numbers, run numbers in dataset returned from process_files function
        for run, metrics in runs.items():

            record = metrics[0]
            record['Cores'] = cores
            record['Run'] = run
            
            data_list.append(record)
            #creates a dictionary named record that contains the values for the timers on each iteration of the loop and adds keys 'Cores' and "run" to specifiy category
            #it then stores the data in a list where each index is the values for the timers and their correpsonding core count and run number
    df = pd.DataFrame(data_list)
    #creates a pandas DataFrame that looks like this
    # Albany Piro  Total Fill Time  Precond  Total Lin  Cores  Run
#0      35.4208          5.13436  18.1079    12.0622      4    1
#1      35.5050          5.13656  18.2115    12.0437      4    2
#2      35.6224          5.12401  18.2333    12.1431      4    3
#3      35.5578          5.15496  18.1484    12.1402      4    4
#4      35.7281          5.13867  18.2746    12.1920      4    5
#5      25.3387          2.70286  12.2567    10.2876      8    1
#6      25.3760          2.68414  12.2851    10.3191      8    2 

    sns.set(style="whitegrid")

    categories = ['Albany Piro', 'Total Fill Time', 'Precond', 'Total Lin']
    #creat categories list with column names in dataframe to iterate over each item in the list in order to plot each one using the matplotlib library
    for category in categories:
        plt.figure(figsize=(10, 5))
        sns.lineplot(x='Cores', y=category, hue='Run', data=df, marker="o")
        plt.title(f'{category} vs. Number of Cores')
        plt.xlabel('Number of Cores')
        plt.ylabel('Time')
        plt.legend(title='Run')
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        plt.show()

    grouped_by_cores = df.groupby('Cores').agg(
        {
            'Albany Piro': ['mean', 'std'],
            'Total Fill Time': ['mean', 'std'],
            'Precond': ['mean', 'std'],
            'Total Lin': ['mean', 'std']
        }
    )

    #groups the dataframe by cores by adding the values for each run and calculating the mean and std deviation for each timer on each core case

    

    # create a new list that is sorted by the Column names in grouped_by cores and adds a _ between the timer name and mean/std
    grouped_by_cores.columns = ['_'.join(col).strip() for col in grouped_by_cores.columns.values]
    

    timers = ['Albany Piro', 'Total Fill Time', 'Precond', 'Total Lin']
    colors = ['b', 'g', 'r', 'c']

    #loops through groyuped_by cores indexes which are [4,8,16,32,64]
    for core in grouped_by_cores.index:
        plt.figure(figsize=(12, 8))
        for i, timer in enumerate(timers):
            plt.subplot(2, 2, i+1)
            core_data = df[df['Cores'] == core]
            plt.scatter(core_data['Run'], core_data[timer], label=f'Core {core}', color=colors[i])
            #sns.scatterplot(x= range(1,len(timers)+1), y=timers, color = 'blue', label = 'Data Points')
            mean = grouped_by_cores.loc[core, f'{timer}_mean']
            std = grouped_by_cores.loc[core, f'{timer}_std']
            plt.axhline(mean, color='k', linestyle='--', label='Mean')
            plt.axhline(mean + 3 * std, color='r', linestyle='--', label='+3 Std Dev')
            plt.axhline(mean - 3 * std, color='r', linestyle='--', label='-3 Std Dev')
            plt.title(f'{timer} for Core {core}')
            plt.xlabel('Run')
            plt.ylabel(timer)
            plt.legend()
            plt.tight_layout()

    plt.show()

    # Calculate speedup and efficiency
    df_speedup_efficiency = calculate_speedup_efficiency(df)

    # Generate ideal values for plotting
    cores = sorted(df['Cores'].unique())
    ideal_speedup = [1] + cores[1:]  # Ideal speedup is linear with the number of cores
    ideal_efficiency = [100] + [100] * (len(cores) - 1)  # Ideal efficiency is always 100%
    single_core_time = df[df['Cores'] == 4].mean()  # Assuming 4 is the single-core time
    ideal_wall_time = [single_core_time[category] / core for core in cores] #

    for timer in timers:
        # Plot Wall-Clock Time
        plt.figure(figsize=(10, 5))
        sns.lineplot(x='Cores', y=timer, hue='Run', data=df, marker="o")
        plt.plot(cores, ideal_wall_time, 'k--', label='Ideal Wall-Clock Time')
        plt.title(f'Wall-Clock Time ({timer}) vs. Number of Cores')
        plt.xlabel('Number of Cores')
        plt.ylabel('Time')
        plt.legend(title='Run')
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        plt.show()
        
        # Plot Speedup
        plt.figure(figsize=(10, 5))
        sns.lineplot(x='Cores', y=f'{timer}_Speedup', hue='Run', data=df_speedup_efficiency, marker="o")
        plt.plot(cores, ideal_speedup, 'k--', label='Ideal Speedup')
        plt.title(f'Speedup ({timer}) vs. Number of Cores')
        plt.xlabel('Number of Cores')
        plt.ylabel('Speedup')
        plt.legend(title='Run')
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        plt.show()
        
        # Plot Efficiency
        plt.figure(figsize=(10, 5))
        sns.lineplot(x='Cores', y=f'{timer}_Efficiency', hue='Run', data=df_speedup_efficiency, marker="o")
        plt.plot(cores, ideal_efficiency, 'k--', label='Ideal Efficiency')
        plt.title(f'Efficiency ({timer}) vs. Number of Cores')
        plt.xlabel('Number of Cores')
        plt.ylabel('Efficiency (%)')
        plt.legend(title='Run')
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        plt.show()
