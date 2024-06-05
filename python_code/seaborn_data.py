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
import numpy as np

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

def plot_wall_time(ax, cores, actual_comp_time, ideal_times, plot_title):
    df = pd.DataFrame({
        'Cores': cores,
        'Clock_Time': actual_comp_time,
        'Ideal_Time': ideal_times
    })

    sns.set_style("whitegrid")
    sns.set_context("paper")

    #Plot clock time
    
    sns.lineplot(x = 'Cores', y='Clock_Time', ax = ax, data=df, marker='o', label ='Actual-Time')
    sns.lineplot(x = 'Cores', y='Ideal_Time', ax = ax, data=df, marker='o', label ='Ideal-Time', linestyle='--')
    ax.set_xlabel("Core Count")
    ax.set_ylabel('Wall-Clock-Time')
    ax.set_xscale('log', base =2)
    ax.set_title(plot_title)
    ax.legend()
    
def plot_efficiency(ax, cores,efficiency_actual, ideal_efficiency,plot_title):
    df = pd.DataFrame({
        'Cores': cores,
        'Actual_Efficiency': efficiency_actual,
        'Ideal_Efficiency': ideal_efficiency
    })

    sns.set_style("whitegrid")
    sns.set_context("paper")

    #Plot efficiency
    sns.lineplot(x = 'Cores', y='Actual_Efficiency', ax = ax, data=df, marker='o', label ='Actual Efficiency')
    sns.lineplot(x = 'Cores', y='Ideal_Efficiency', ax = ax, data=df, marker='o', label ='Ideal Efficiency', linestyle='--')
    ax.set_xlabel("Core Count")
    ax.set_ylabel('Efficiency')
    ax.set_xscale('log', base =2)
    ax.set_title(plot_title)
    ax.legend() 

def plot_speedup(ax, cores, speedup, ideal_speedup ,plot_title):
    df = pd.DataFrame({
        'Cores': cores,
        'Speedup': speedup,
        'Ideal_speedup': ideal_speedup
    })

    sns.set_style("whitegrid")
    sns.set_context("paper")

    #Plot speedup

    sns.lineplot(x = 'Cores', y='Speedup', ax = ax, data=df, marker='o', label ='Actual Speedup')
    sns.lineplot(x = 'Cores', y='Ideal_speedup', ax =ax, data=df, marker='o', label ='Ideal Speedup', linestyle='--')
    ax.set_xlabel("Core Count")
    ax.set_ylabel('Speedup')
    ax.set_xscale('log', base =2)
    ax.set_title(plot_title)
    ax.legend()
    
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

            fig, axes = plt.subplots(1,3, figsize=(15,5))
            

            
            plot_efficiency(axes[0],cores, efficiency_actual, ideal_efficiency, plot_title=f'{key} Efficiency')
            plot_wall_time(axes[1],cores, actual_comp_time, ideal_times, plot_title=f'{key} Time')
            plot_speedup(axes[2] ,cores, speedup, ideal_speedup ,plot_title=f'{key} Speedup')

            fig.tight_layout()
            plt.show()
                
            

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


    grouped_by_cores = df.groupby('Cores').agg(
        {
            'Albany Piro': ['mean', 'std'],
            'Total Fill Time': ['mean', 'std'],
            'Precond': ['mean', 'std'],
            'Total Lin': ['mean', 'std']
        }
    )

    #groups the dataframe by cores by adding the values for each run and calculating the mean and std deviation for each timer on each core case
    #Indexed by Core, Timers are the column names with subcolums mean and std
    print(grouped_by_cores)

    # create a new list that is sorted by the Column names in grouped_by cores and adds a _ between the timer name and mean/std
    grouped_by_cores.columns = ['_'.join(col).strip() for col in grouped_by_cores.columns.values]
    
    print(grouped_by_cores.columns)
    timers = ['Albany Piro', 'Total Fill Time', 'Precond', 'Total Lin']
    colors = ['b', 'g', 'r', 'c']
    #scatterplot
    #loops through grouped_by_cores indexes which are [4,8,16,32,64]
    for core in grouped_by_cores.index:
        plt.figure(figsize=(12, 8))
        for i, timer in enumerate(timers):
            plt.subplot(2, 2, i+1)
            core_data = df[df['Cores'] == core]
            #all core that match the current core in grouped_cores_by_index
            plt.scatter(range(1,len(core_data['Run'])+1), core_data[timer], label=f'{timer}', color=colors[i])
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

    plt.show()


    # Generate ideal values for plotting
    cores = sorted(df['Cores'].unique())
    run =sorted(df['Run'].unique())
    ideal_efficiency = [100]*len(cores)

    x = create_sorted_dictionary(df, timers, cores)
    get_metrics(x)

    #Wall clock-time
    sns.relplot(data = df, x = 'Cores', y = 'Albany Piro', kind ="line", hue = 'Run', errorbar = 'sd')
    plt.xscale('log', base = 2)
    
    plt.xticks(cores) 

   # plt.show()

def efficiency(df, timer,cores):
    grouped = df.groupby('Run')
    efficiency_actual = []
    
    for i, (name, group) in enumerate(grouped):
        val = group[timer].to_numpy()
        base_comp_time = val[0]
        
        #print(base_comp_time)
        
        ideal_times=(base_comp_time/[2**core for core in range(len(cores))])
        #print(ideal_times)
        efficiency_run = (ideal_times/val) *100
        efficiency_actual.extend(efficiency_run)

    


    
    # Flatten the list of arrays for printing
    return efficiency_actual



timers = ['Albany Piro', 'Total Fill Time', 'Precond', 'Total Lin']

efficiency_df = pd.DataFrame()

for timer in timers:
    
    eff = efficiency(df, timer,cores)
   

    efficiency_df[f"Efficiency {timer}"] = eff
    
    df_sorted = df.sort_values(by=['Run', 'Cores'])

    df_final = pd.concat([df_sorted.reset_index(drop=True), efficiency_df.reset_index(drop=True)], axis=1)

    sns.relplot(data = df_final, x = 'Cores', y = f'Efficiency {timer}', kind ="line",  errorbar = 'sd', marker ='o')
    plt.errorbar(data = df_final, x ='Cores', y= f'Efficiency {timer}', yerr=0.5, fmt='o', color='black', alpha=0.5)
    plt.xscale('log', base =2 )
    plt.title(f"Efficiency {timer}")

print(df_final)
    






plt.show()
#print(df_final)


#plt.show()

""" Albany Piro  Total Fill Time   Precond  Total Lin  Cores  Run
0       35.4208         5.134360  18.10790   12.06220      4    1
1       35.5050         5.136560  18.21150   12.04370      4    2
2       35.6224         5.124010  18.23330   12.14310      4    3
3       35.5578         5.154960  18.14840   12.14020      4    4
4       35.7281         5.138670  18.27460   12.19200      4    5
5       25.3387         2.702860  12.25670   10.28760      8    1
6       25.3760         2.684140  12.28510   10.31910      8    2
7       25.2045         2.622860  12.25420   10.24240      8    3
8       25.4112         2.698110  12.32620   10.30150      8    4
9       25.4368         2.689290  12.24600   10.41230      8    5
10      18.8883         1.564090   8.96121    8.27806     16    1
11      19.0200         1.480770   9.04482    8.40888     16    2
12      18.9314         1.487720   9.03144    8.32569     16    3
13      18.9375         1.485960   8.95094    8.41899     16    4
14      18.7272         1.453910   8.99935    8.18949     16    5
15      16.3237         0.901591   7.49015    7.83321     32    1
16      16.4383         0.913484   7.56840    7.85492     32    2
17      16.8101         0.906870   7.67405    8.13519     32    3
18      16.1649         0.907061   7.48247    7.67906     32    4
19      16.3724         0.899890   7.50026    7.87201     32    5
20      15.3698         0.619458   6.97466    7.66880     64    1
21      15.6374         0.624863   6.98562    7.92969     64    2
22      15.3428         0.617566   6.88277    7.74364     64    3
23      14.8645         0.603233   6.82484    7.34092     64    4
24      15.7100         0.608277   6.90416    8.09720     64    5 """

df_long = df.pivot(index = 'Cores', columns = 'Run')   
df_final_long = df_final.pivot(index = 'Cores', columns = 'Run')

df_long.head()
dfffff = df.melt(id_vars=['Cores', 'Run'], var_name ='Timer', value_name= 'Time')
print(dfffff)

grouped_by_cores_2 = df.groupby('Cores').agg(
        {
            'Albany Piro': ['mean'],
            'Total Fill Time': ['mean'],
            'Precond': ['mean'],
            'Total Lin': ['mean']
        }
    )


grouped_by_cores_2.columns = ['Albany Piro_mean', 'Total Fill Time_mean', 'Precond_mean', 'Total Lin_mean']
grouped_by_cores_2 = grouped_by_cores_2.reset_index()


print(grouped_by_cores_2)


#print(grouped_by_cores_2.set_index('Cores'))
gruuu  = grouped_by_cores_2.melt(id_vars= ['Cores'], value_vars= ['Albany Piro_mean', 'Total Fill Time_mean', 'Precond_mean', 'Total Lin_mean' ], var_name = 'Timer', value_name = 'Time')

print(gruuu)
sns.catplot(data= gruuu, y = 'Time', hue = 'Timer', col= 'Cores', kind= 'bar')
sns.catplot(data= dfffff, x = 'Cores', y = 'Time',  col= 'Timer', kind= 'box')
#smaller
plt.show() 



lol =dfffff.set_index('Cores')
print(lol)

""" for core in dfffff['Cores'].unique():
    lal =lol.loc[lol.index[core]]

    for timer in dfffff['Timer'].unique():

        lul =lal[(lal['Timer']==timer)]
        print(lul)
        sns.boxplot(data= lul,  x = 'Run', y = 'Time', label = f'{timer}' )
        plt.show()  """





        



   

    #efficiency_actual = [(ideal/actual) *100 for ideal,actual in zip(ideal_times,actual_comp_time) ]
   # ideal_times.append(base_comp_time/(2**i))



