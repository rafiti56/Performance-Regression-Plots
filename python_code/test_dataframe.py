import os
import re
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def get_sorted_files(folder_path, file_pattern):
    # List all files in the given folder
    files = os.listdir(folder_path)
    
    # Filter files based on the provided pattern
    matched_files = [f for f in files if re.match(file_pattern, f)]
    
    # Sort files based on numerical order extracted from filenames
    sorted_files = sorted(matched_files, key=lambda x: (int(re.findall(r'\d+', x)[0]), int(re.findall(r'run(\d+)',x)[0])))
    
    return sorted_files

def process_files(folder_path):
    # Define the pattern of the filenames you are looking for
    file_pattern = r'data_cores\d+_run\d+'  # Adjust the pattern as needed to match the specific files
    
    # Get the sorted list of files
    sorted_files = get_sorted_files(folder_path, file_pattern)

    results = {}
    run1 =[]
    run2= []
    run3=  []
    run4 = []
    run5 = []
    
    run_lists = {
        1: run1,
        2: run2,
        3: run3,
        4: run4,
        5: run5
            }
    # Loop over the sorted files and process them
    for filename in sorted_files:
        file_path = os.path.join(folder_path, filename)
        print(f"Processing {file_path}")
        
        # Add your file processing code here
        with open(file_path, 'r') as file:
            text = file.read()
        
            # Define the timer names and regular expressions to extract their values
            timers = {
                "Albany Piro": r'Piro::NOXSolver::evalModelImpl::solve: (\d+\.\d+)',
                "Total Fill Time": r'Albany: Total Fill Time: (\d+\.\d+)',
                "Precond": r'NOX Total Preconditioner Construction: (\d+\.\d+)',
                "Total Lin": r'NOX Total Linear Solve: (\d+\.\d+)',
            }
            
            # Extract timer values for each timer
            extracted_timers = {}
            for timer_name, pattern in timers.items():
                match = re.search(pattern, text)
                if match:
                    timer_value = match.group(1)
                    extracted_timers[timer_name] = float(timer_value)
                else:
                    extracted_timers[timer_name] = None
            # Add the extracted timers to the results dictionary
            # Remove the file extension
            filename_no_ext = filename.split(".")[0]
    
            # Split the filename into parts
            parts = filename_no_ext.split("_")
    
            # Extract core and run numbers
            core = int(parts[1].replace("cores", ""))
            run = int(parts[2].replace("run", ""))

            if core not in results:
                results[core]= {}
                
            if run not in results[core]:
                results[core][run] = []
                
                
            results[core][run].append(extracted_timers)
            
            
    for key, l in results.items():
        for runs, lists in l.items():
            run_number = int(runs)
            run_lists[run_number].append(lists)    
                    #run_lists[run_number].append(extracted_timers)

    print(run1)
    print(run2)
    
    print(results)
    
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
    #plt.yscale('log', base =2)
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
    #plt.xscale('log', base =2)
    plt.title(plot_title)
    plt.legend()
    plt.savefig(plot_title, dpi =300)


if __name__ == "__main__":
    folder_path = r'C:\Users\Rafael\OneDrive\Documents\GitHub\Performance-Regression-Plots\text_files'  # Update with the path to your folder
    data = process_files(folder_path)
    

    # Convert the nested dictionary to a list of dictionaries for easier DataFrame creation
    data_list = []
    for cores, runs in data.items():
        for run, metrics in runs.items():
            record = metrics[0]
            record['Cores'] = cores
            record['Run'] = run
            data_list.append(record)

    # Create a DataFrame
    df = pd.DataFrame(data_list)

    # Plotting
    categories = ['Albany Piro', 'Total Fill Time', 'Precond', 'Total Lin']
    fig, axs = plt.subplots(len(categories), 1, figsize=(10, 15))
    fig.suptitle('Performance Metrics vs. Number of Cores')

    for i, category in enumerate(categories):
        for run in df['Run'].unique():
            run_data = df[df['Run'] == run]
            axs[i].plot(run_data['Cores'], run_data[category], label=f'Run {run}')
        axs[i].set_title(category)
        axs[i].set_xlabel('Number of Cores')
        axs[i].set_ylabel('Time')
        axs[i].legend()

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    print(df)
    plt.show()
    

    






