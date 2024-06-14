import os
import re
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

#read core cases and outputs individual lineplots for each metric (efficiency, speedup, wall time)

def get_sorted_files(folder_path, file_pattern):
    # List all files in the given folder
    files = os.listdir(folder_path)
    
    # Filter files based on the provided pattern
    matched_files = [f for f in files if re.match(file_pattern, f)]
    
    # Sort files based on numerical order extracted from filenames
    sorted_files = sorted(matched_files, key=lambda x: int(re.findall(r'\d+', x)[0]))
    
    return sorted_files

def process_files(folder_path):
    # Define the pattern of the filenames you are looking for
    file_pattern = r'data_cores\d+\.txt'  # Adjust the pattern as needed
    
    # Get the sorted list of files
    sorted_files = get_sorted_files(folder_path, file_pattern)

    results ={}
    order = 1
    extracted_Piro = []
    extracted_Fill = []
    extracted_Precond = []
    extracted_linsolve = []
    
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
            results[order] = extracted_timers
            extracted_Piro.append(extracted_timers.get('Albany Piro'))
            extracted_Fill.append(extracted_timers.get('Total Fill Time'))
            extracted_Precond.append(extracted_timers.get('Precond'))
            extracted_linsolve.append(extracted_timers.get('Total Lin'))
            
            order += 1
            #print(extracted_timers)       
    return {
        'Total Piro': extracted_Piro,
        'Total Fill': extracted_Fill,
        'Total Precond': extracted_Precond,
        'Total Linear': extracted_linsolve
    }


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
    folder_path = r'C:\Users\rcaller\Documents\GitHub\Performance-Regression-Plots\text_files_plot_gen'  # Update with the path to your folder
    All_totals = process_files(folder_path)
    
    cores = [4,8,16,32,64]
    ideal_efficiency = [100]*len(cores)
    print(All_totals)

    for key, actual_comp_time in All_totals.items():
        base_comp_time = actual_comp_time[0]
        ideal_times = []
        speedup = []
        ideal_speedup = []
        for i in range(len(cores)):
            ideal_times.append(base_comp_time/(2**i))
        efficiency_actual = [(ideal/actual) *100 for ideal,actual in zip(ideal_times,actual_comp_time) ]
        
        for j in range(len(cores)):
            speedup.append(base_comp_time/actual_comp_time[j])
            ideal_speedup.append(base_comp_time/ideal_times[j])
        plot_efficiency(cores, efficiency_actual, ideal_efficiency, plot_title=f'{key} Efficiency')
        plot_wall_time(cores, actual_comp_time, ideal_times, plot_title=f'{key} Time')
        plot_speedup(cores, speedup, ideal_speedup ,plot_title=f'{key} Speedup' )

#needs files to be in format data_cores{num}
#runs graphs for efficiency, wall_time and speedup for each timer