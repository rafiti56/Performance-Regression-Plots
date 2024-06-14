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


#read multiple run files and outputs grouped scatterplots by core and individual lineplots for each metric (efficiency, speedup, wall time)

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



def plot_wall_time(cores, actual_comp_time, ideal_times, plot_title):
    df = pd.DataFrame({
        'Cores': cores,
        'Clock_Time': actual_comp_time,
        'Ideal_Time': ideal_times
    })

    sns.set_style("whitegrid")
    sns.set_context("paper")

    #Plot clock time
    plt.figure(figsize=(12,6))
    sns.lineplot(x = 'Cores', y='Clock_Time', data=df, marker='o', label ='Actual-Time')
    sns.lineplot(x = 'Cores', y='Ideal_Time', data=df, marker='o', label ='Ideal-Time', linestyle='--')
    plt.xlabel("Core Count")
    plt.ylabel('Wall-Clock-Time')
    plt.xscale('log', base =2)
    plt.title(plot_title)
    plt.legend()
    plt.savefig(plot_title, dpi =300)

def plot_efficiency(cores,efficiency_actual, ideal_efficiency,plot_title):
    df = pd.DataFrame({
        'Cores': cores,
        'Actual_Efficiency': efficiency_actual,
        'Ideal_Efficiency': ideal_efficiency
    })

    sns.set_style("whitegrid")
    sns.set_context("paper")

    #Plot efficiency
    plt.figure(figsize=(12,6))
    sns.lineplot(x = 'Cores', y='Actual_Efficiency', data=df, marker='o', label ='Actual Efficiency')
    sns.lineplot(x = 'Cores', y='Ideal_Efficiency', data=df, marker='o', label ='Ideal Efficiency', linestyle='--')
    plt.xlabel("Core Count")
    plt.ylabel('Efficiency')
    plt.xscale('log', base =2)
    plt.title(plot_title)
    plt.legend()
    plt.savefig(plot_title, dpi =300)

def plot_speedup(cores, speedup, ideal_speedup ,plot_title):
    df = pd.DataFrame({
        'Cores': cores,
        'Speedup': speedup,
        'Ideal_speedup': ideal_speedup
    })

    sns.set_style("whitegrid")
    sns.set_context("paper")

    #Plot speedup
    plt.figure(figsize=(12,6))
    sns.lineplot(x = 'Cores', y='Speedup', data=df, marker='o', label ='Actual Speedup')
    sns.lineplot(x = 'Cores', y='Ideal_speedup', data=df, marker='o', label ='Ideal Speedup', linestyle='--')
    plt.xlabel("Core Count")
    plt.ylabel('Speedup')
    plt.xscale('log', base =2)
    plt.title(plot_title)
    plt.legend()
    plt.savefig(plot_title, dpi =300)



def create_sorted_dictionary(df, timers, cores):
        timer_values_by_core = {timer: [] for timer in timers}

            # Populate the lists with timer values for each core count
        for core in cores:
            core_group = df[df['Cores'] == core]
            for timer in timers:
                timer_mean_value = core_group[timer].mean()  # Use mean to get a single value for each core
                timer_values_by_core[timer].append(timer_mean_value)
                print(timer_values_by_core)
        return timer_values_by_core

def get_metrics(timer_values_by_core):
        
        for key, actual_comp_time in timer_values_by_core.items():
            base_comp_time = actual_comp_time[0]
            ideal_times = []
            speedup = []
            ideal_speedup = []
            
            
            for i in range(len(cores)):
                
                ideal_times.append(base_comp_time/(2**i))
                speedup.append(base_comp_time/actual_comp_time[i])
                ideal_speedup.append(base_comp_time/ideal_times[i])
            efficiency_actual = [(ideal/actual) *100 for ideal,actual in zip(ideal_times,actual_comp_time) ]
            
            plot_efficiency(cores, efficiency_actual, ideal_efficiency, plot_title=f'{key} Efficiency')
            plot_wall_time(cores, actual_comp_time, ideal_times, plot_title=f'{key} Time')
            plot_speedup(cores, speedup, ideal_speedup ,plot_title=f'{key} Speedup' )

if __name__ == "__main__":
    folder_path = r'C:\Users\rcaller\Documents\GitHub\Performance-Regression-Plots\text_files'  # Update with path to folder containing run cases as text files
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
     
    #############################################################################################################################

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
    #scatterplot
    #loops through groyuped_by cores indexes which are [4,8,16,32,64]
    for core in grouped_by_cores.index:
        plt.figure(figsize=(12, 8))
        for i, timer in enumerate(timers):
            plt.subplot(2, 2, i+1)
            core_data = df[df['Cores'] == core]
            plt.scatter(range(1,len(core_data['Run'])+1), core_data[timer], label=f'Core {core}', color=colors[i])
            #sns.scatterplot(x= range(1,len(timers)+1), y=timers, color = 'blue', label = 'Data Points')
            mean = grouped_by_cores.loc[core, f'{timer}_mean']
            std = grouped_by_cores.loc[core, f'{timer}_std']
            plt.axhline(mean, color='k', linestyle='--', label='Mean')
            plt.axhline(mean + 3 * std, color='r', linestyle='--', label='+3 Std Dev')
            plt.axhline(mean - 3 * std, color='r', linestyle='--', label='-3 Std Dev')
            plt.title(f'{timer} for Core {core}')
            plt.xlabel('Run')
            plt.xticks(range(1,len(core_data['Run'])+1))
            plt.ylabel(timer)
            plt.legend()
            plt.tight_layout()
        plt.savefig(f'{core} core mean scatterplot', dpi =300)
    ################################################################################################################################
    


    # Generate ideal values for plotting
    cores = sorted(df['Cores'].unique())
    run =sorted(df['Run'].unique())
    ideal_efficiency = [100]*len(cores)

    x = create_sorted_dictionary(df, timers, cores)

    #Generates individual timer plots 'Timer Name: + Eff/Speed/Time'
    get_metrics(x)

    #takes input files with run and core number and sorts them into dictionary and then dataframe
    #takes the mean for all runs under core cases and makes lineplot for the mean
    #creates visual scatter plots that include all data points for each run for each timer. 
    #each scatterplot figure contains 4 plots for the specified core count, one plot for each timer, shows lines for mean and std deviation for reference 

