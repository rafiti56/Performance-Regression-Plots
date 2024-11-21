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
    file_pattern = r'MPI_cores\d+_run\d+'  # Adjust the pattern as needed to match the specific files
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
                "Total Fill Time": r'Albany: Total Fill Time: (\d+\.\d+)',
                "Precond": r'NOX Total Preconditioner Construction: (\d+\.\d+)',
                "Total Lin": r'NOX Total Linear Solve: (\d+\.\d+)',
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

def process_files2(folder_path):
    #specifies file pattern
    #change to text_file pattern
    file_pattern = r'2threads_cores\d+_run\d+'  # Adjust the pattern as needed to match the specific files
    sorted_files = get_sorted_files(folder_path, file_pattern)
    #calls for get_sorted files function and assigns it to sorted_files
    results_2threads = {}
    
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
            if core not in results_2threads:
                #Add core as a key in the dictionary if not there
                results_2threads[core] = {}
            if run not in results_2threads[core]:
                #Adds run as a nested dictionary under core key and creates and empty list to append the extracted timer values from the file (Piro, Albany, FIll, linsonve)
                results_2threads[core][run] = []
            results_2threads[core][run].append(extracted_timers)
    #print(results_front)
    return results_2threads

def trim(x, p=.1, threshold=3, outliers=False):
    '''
    Remove observations that may be outliers - suspiciously far from the average.
    At most [floor(len(x)*p)] points are removed.
    Input:
        x : data to trim
        p : proportion of data to remove
    '''
    n = len(x)
    if p == 0 or n < np.ceil(1/p):
        return (x, []) if outliers else x

    # Trim most extreme observations if more than [threshold] std away.
    n_remove = int(np.floor(n*p))
    dev = np.abs(x - np.median(x))/(mad(x) + 1e-8)
    order = np.argsort(np.abs(x - np.median(x)))

    keep = []
    out = []
    for i in range(n):
        if dev[i] < threshold or i in order[:n-n_remove]:
            keep.append(i)
        else:
            out.append(i)

    return (x[keep], x[out]) if outliers else x[keep]

###################################################################################################
def trim_mean(x, p=.1):
    '''
    Trim a series to remove egregious outliers, and then return the mean.
    Input:
        x : series to trim
        p : maximum proportion of data to remove
    '''
    return trim(x, p).mean()

###################################################################################################
def trim_std(x, p=.1):
    '''
    Trim a series to remove egregious outliers, and then return the standard deviation.
    Inputs:
        x : series to trim
        p : maximum proportion of data to remove
    '''
    print(trim(x, p).std())
    return trim(x, p).std()

###################################################################################################
def trimmed_stats(x, p=.1, var=True):
    '''
    Get trimmed mean and std or variance
    '''
    if var:
        return trim_mean(x, p), np.square(trim_std(x, p))
    else:
        return trim_mean(x, p), trim_std(x, p)


def trimmed_ttest(x, y=None, with_pval=True):
    '''
    Get t-statistic for difference in two independent samples with unequal variance.
    Useful if the means of the samples are roughly normal (e.g. data is normal, or
    sample size large enough, say 30+)
    Input:
        x, y : samples to compare. If y is None, performs one-sample t-test of mean==0
    '''
    
    xmean, xvar = trimmed_stats(x, var=True)
    if y is None:
        n = len(x)
        tstat = xmean / (np.sqrt(xvar/(n-2)) + 1e-8)
    else:
        
        ymean, yvar = trimmed_stats(y, var=True)
        k, n = len(x), len(x)+len(y)
        if n <= 2:
            return (0, 1) if with_pval else 0

        rss = (k-1)*xvar + (n-k-1)*yvar
        sigma = np.sqrt(rss/(n-2)) + 1e-8
        tstat = np.sqrt(k*(n-k)/n)*(ymean-xmean)/sigma
    pval = 2*tdist.cdf(-np.abs(tstat), n-2)
    return (tstat, pval) if with_pval else tstat


def scitest(y, conf = 0.99):
    
            n = len(y)
            var = tdist.ppf((1 + conf)/2, n-1)
            std_error = (y.std() / np.sqrt(n))
            mean = np.mean(y)
            upper_bound = mean + var*std_error
            lower_bound = mean - var*std_error
            return (lower_bound, upper_bound)
            
            #print(var)

class res:
    def __init__(self, folder_path, file_pattern):
        self.folder_path =folder_path
        self.results ={}
        self.file_pattern  = file_pattern

    def get_sorted_files(folder_path, file_pattern):
        #define function get_sorted_file swhich takes folder_path and file_pattern as inputs
        files = os.listdir(folder_path)
        #retrieves a list of all files and directories in the specified folder path
        matched_files = [f for f in files if re.match(file_pattern, f)]
        #sorts through files in folder and retrieves a list of all files that match the specified file pattern
        sorted_files = sorted(matched_files, key=lambda x: (int(re.findall(r'\d+', x)[0]), int(re.findall(r'run(\d+)', x)[0])))
        #sorts the matched files, lambda is a pyython featuer that creates anonymous functions, it then extracts the numerical values in the filenames as a tuple(primary, secondary)
        return sorted_files

    def process_files(self):
        #specifies file pattern
        file_pattern = self.file_pattern # Adjust the pattern as needed to match the specific files
        sorted_files = get_sorted_files(self.folder_path, file_pattern)
        #calls for get_sorted files function and assigns it to sorted_files
        
        
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
                    "No of NonLinear Iterations": r'NOX Total Linear Solve: .* \[(\d+)\]',
                    "No of Linear Iterations": r'Belos: Operation Prec\*x: .* \[(\d+)\]'
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
                if core not in self.results:
                    #Add core as a key in the dictionary if not there
                    self.results[core] = {}
                if run not in self.results[core]:
                    #Adds run as a nested dictionary under core key and creates and empty list to append the extracted timer values from the file (Piro, Albany, FIll, linsonve)
                    self.results[core][run] = []
                self.results[core][run].append(extracted_timers)
        #print(results_front)
        return self.results





# Define a function to process each dataset
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
            # It then stores the data in a list where each index is the values for the timers and their corresponding core count and run number

def trimmed_bounds(x, p=.1, alpha=0.01):
    '''
    Get confidence interval for the mean of a trimmed time series
    '''
    
    n = len(x)
    mean, std = trimmed_stats(x, p, var=False)
    stderr = std / np.sqrt(n)
    tcrit = tdist.isf(alpha/2, n-1)
    upper = mean + tcrit * stderr
    lower = mean - tcrit * stderr
    return mean, lower, upper

def jerry_test(df, timers, cores):
    for core in cores:
        core_group = df[df['Cores']== core]
        for timer in timers:
            y = core_group[timer]
            print(y)
            var = trimmed_bounds(y)
            print(var)


def trimmed_ttest_bounds(x, y, p=.1, alpha=0.01, num_tests=1):
    '''
    Get confidence interval for the difference between means
    '''
    
    xmean, xvar = trimmed_stats(x, p, var=True)
    n = len(x)
    
    ymean, yvar = trimmed_stats(y, p, var=True)
    m = len(y)

    rss = (n-1)*xvar + (m-1)*yvar
    sigma = np.sqrt(rss/(n+m-2)) + 1e-8
    stderr = sigma / np.sqrt(n*m/(n+m))
    #tstat = np.sqrt(n*m/(n+m))*(ymean-xmean)/sigma
    tcrit = tdist.isf(alpha/(2*num_tests), df=n+m-2)
    meandiff = xmean-ymean
    upper = meandiff + tcrit * stderr
    lower = meandiff - tcrit * stderr
    return meandiff, lower, upper

def efficiency(df, timer,cores):
    grouped = df.groupby('Run')
    efficiency_actual = []
    
    for i, (name, group) in enumerate(grouped):
        val = group[timer].to_numpy()
        print(val)
        base_comp_time = val[0]
        
        #print(base_comp_time)

        for i in range(len(val)):
            #previous time
            if i  == 0:
                efficiency_actual.append(100)
            else:
                #previous time
                tm = val[i-1]
                tn = val[i]
                n = cores[i]
                m = cores[i-1]
                eff = (tm/tn)/(n/m)*100
                print(eff)
                efficiency_actual.append(eff)

    return efficiency_actual


if __name__ == "__main__":
    folder_path = r'C:\Users\Rafael\OneDrive\Documents\GitHub\Performance-Regression-Plots\text_files\OPMPI_2threads_vs_MPI_only_text'



    data_2threads = res(folder_path, r'OP_cores\d+_run\d+')

    data_MPI = res(folder_path, r'MPI_cores\d+_run\d+')

    data_MPI.process_files()

    data_2threads.process_files()

    


    data_list =[]

    #Change labeling
    process_data(data_MPI.results, 'MPI')
    process_data(data_2threads.results, '2threads')

    
    # Convert the list to a DataFrame
    df = pd.DataFrame(data_list)

    print(df)
    print(df["No of Linear Iterations"])

    # Now df contains the combined data from both datasets with an additional 'Dataset' column to distinguish them
    df['Linear/Nonlinear'] = np.floor(df['No of Linear Iterations'] / df['No of NonLinear Iterations'])
    
    #round down using np.floor to integer number for average number of iterations
    print(df['Linear/Nonlinear'])
    print(df)

    avgIters = []

    for dataset in df['Dataset'].unique():
        datagroup = df[df['Dataset'] == dataset]
        for core in df['Cores'].unique():
            coreGroup = datagroup[datagroup['Cores'] == core]
            avgIterations = np.mean(coreGroup['Linear/Nonlinear'])
            avgIters.append({
                'Average Iterations': avgIterations,
                'Cores': core,
                'Dataset': dataset

            })
    #avgIters = df.groupby('Cores')['Linear/Nonlinear'].mean().tolist()
    print(avgIters)
    avgItersDf = pd.DataFrame(avgIters)
    print(avgItersDf)

    plt.figure()
    
    
    sns.pointplot( data=avgItersDf, x='Cores', y='Average Iterations', hue='Dataset', dodge= True )
    plt.xlabel('Nodes')
    plt.ylabel('Average No. of Iterations')
    
    
    plt.title(f'Linear / NonLinear ')
    plt.savefig(f'No of Iterations', dpi =300)



    df_MPI = df[df['Dataset'] == 'MPI']

    df_2threads = df[df['Dataset'] == '2threads']

    altered_MPI = df_MPI.melt(id_vars=['Cores', 'Run', 'Dataset'], var_name ='Timer', value_name= 'Time')
    altered_2threads = df_2threads.melt(id_vars=['Cores', 'Run', 'Dataset'], var_name ='Timer', value_name= 'Time')
    
    

    timers = ['Albany Piro', 'Total Fill Time', 'Precond', 'Total Lin']


   

    cores = [4,8,16,32,64]

    #efficiency
    efficiency_df_MPI = pd.DataFrame()
    efficiency_df_2threads = pd.DataFrame()

    print(df.columns)
    for timer in timers:
            
            
            eff_MPI = efficiency(df_MPI, timer,cores)
            eff_2threads = efficiency(df_2threads, timer,cores)
        
            efficiency_df_MPI[f"Efficiency {timer}"] = eff_MPI
            efficiency_df_2threads[f"Efficiency {timer}"] = eff_2threads

            
            df_sorted_MPI = df_MPI.sort_values(by=['Run', 'Cores', ]) 
            #########################
            df_sorted_2threads = df_2threads.sort_values(by=['Run', 'Cores', ]) 

            df_final_MPI = pd.concat([df_sorted_MPI.reset_index(drop=True), efficiency_df_MPI.reset_index(drop=True)], axis=1)
            df_final_2threads = pd.concat([df_sorted_2threads.reset_index(drop=True), efficiency_df_2threads.reset_index(drop=True)], axis=1)
    print(df_final_MPI)
    df_eff_MPI = df_final_MPI.drop(['Albany Piro', 'Total Fill Time', 'Precond', 'Total Lin', 'No of Linear Iterations', "No of NonLinear Iterations", 'Linear/Nonlinear'], axis =1 )
    
    eff_melt_MPI = df_eff_MPI.melt(id_vars=['Cores', 'Run', 'Dataset'], var_name = 'Efficiency', value_name = 'Percentage')


    df_eff_2threads = df_final_2threads.drop(['Albany Piro', 'Total Fill Time', 'Precond', 'Total Lin', 'No of Linear Iterations', "No of NonLinear Iterations", 'Linear/Nonlinear'], axis =1 )
    
    eff_melt_2threads = df_eff_2threads.melt(id_vars=['Cores', 'Run', 'Dataset'], var_name = 'Efficiency', value_name = 'Percentage')

    print(eff_melt_MPI)

    unique_effs = eff_melt_MPI['Efficiency'].unique()

    for i, timer in enumerate(unique_effs):
        eff_df_2threads = eff_melt_2threads[eff_melt_2threads['Efficiency'] == timer]
        eff_df_MPI = eff_melt_MPI[eff_melt_MPI['Efficiency'] == timer]
        plt.figure()
        #unique_xs= sorted(eff_df['Cores'].unique())
        sns.pointplot( data=eff_df_MPI, x=eff_df_MPI['Cores'], y=eff_df_MPI['Percentage'], errorbar = scitest, capsize = 0.3, color = 'red', errwidth= 0.75, join =False, dodge= True )
        sns.boxplot(data=eff_df_MPI, x=eff_df_MPI['Cores'],    y=eff_df_MPI['Percentage'], showcaps= False, linewidth= 0.5, color= 'red', label = 'MPI', whis=(0,100), showmeans =True, meanprops={"marker":"s","markerfacecolor":"white", "markeredgecolor":"blue"}, dodge= True)

        sns.pointplot( data=eff_df_2threads, x=eff_df_2threads['Cores'], y=eff_df_2threads['Percentage'], errorbar = scitest, capsize = 0.3, color= 'orange', errwidth= 0.75, join =False , dodge = True)
        sns.boxplot(data=eff_df_2threads, x=eff_df_2threads['Cores'],    y=eff_df_2threads['Percentage'], showcaps= False, linewidth= 0.5, color= 'orange', label = '2threads', whis=(0,100), showmeans =True, meanprops={"marker":"s","markerfacecolor":"white", "markeredgecolor":"blue"}, dodge= True)
        plt.xlabel('Nodes')
        plt.ylabel('Percentage')
        plt.legend()
        plt.title(f'Box Plot with Mean Error Bars - Efficiency: {timer}')
        plt.savefig(f'Efficiency {timer} Boxplot with mean errror bars', dpi =300)

    tstat_list = []

    for core in cores:
        
        core_group_MPI = df_MPI[df_MPI['Cores']== core]
        core_group_2threads = df_2threads[df_2threads['Cores']== core]

        for timer in timers:

            tstat, pval= trimmed_ttest(core_group_MPI[timer], core_group_2threads[timer], with_pval=True)
            tstat_list.append({
                'Cores': core,
                'Timer': timer,
                'Tstat': tstat,
                'Pval': pval,
            })
    tstat_df = pd.DataFrame(tstat_list)
##################################################################################################
    mean_list = []

    for core in cores:
        
        core_group_MPI = df_MPI[df_MPI['Cores']== core]
        core_group_2threads = df_2threads[df_2threads['Cores']== core]

        for timer in timers:

            log_mean, log_lower, log_upper= trimmed_ttest_bounds(np.log(core_group_2threads[timer]), np.log(core_group_MPI[timer]))
            mean_list.append({
                'Cores': core,
                'Timer': timer,
                'Mean Difference': log_mean,
                'Bounds': (log_lower,log_upper)
            })
    mean_df = pd.DataFrame(mean_list)

   
    

    

    
    
    """  altered_MPI['Timer_front'] = altered_MPI['Time']
    merge_df = altered_MPI
    merge_df['Timer_2threads']  = altered_2threads['Time']
    merge_df['Time'] = merge_df['Timer_2threads'] - merge_df['Timer_front'] 
    difference = merge_df.drop(columns=['Timer_front', 'Timer_2threads', 'Dataset']) """

    """  sci_list = []

    for core in cores:
        sci_cores = difference[difference['Cores'] == core]
        

        for timer in timers:
            sci_time = (sci_cores[sci_cores['Timer'] == timer ])
            ll, ul = scitest(sci_time['Time'])
            sci_list.append({
                'Cores': core,
                'Timer': timer,
                'Difference': sci_time['Time'].mean(),
                'Bounds': (ll,ul)
                
            })
    sci_df = pd.DataFrame(sci_list) """


    unique_timers = altered_MPI['Timer'].unique()

    for i, timer in enumerate(unique_timers):
        # Filter dataframe for the current timer
        timer_df_MPI = altered_MPI[altered_MPI['Timer'] == timer]
        timer_df_2threads = altered_2threads[altered_2threads['Timer'] == timer]

        
        plt.figure()
        unique_sorted_MPI= sorted(timer_df_MPI['Cores'].unique())
        #MPI
        sns.pointplot( data=timer_df_MPI, x=timer_df_MPI['Cores'], y=timer_df_MPI['Time'], errorbar = scitest, capsize = 0.3, color = 'red', errwidth= 0.75, join =False )
        sns.boxplot(data=timer_df_MPI, x=timer_df_MPI['Cores'],    y=timer_df_MPI['Time'], showcaps= False, linewidth= 0.5, color= 'red', label = 'MPI', whis=(0,100), showmeans =True, meanprops={"marker":"s","markerfacecolor":"white", "markeredgecolor":"blue"})
        #2threads
        sns.pointplot( data=timer_df_2threads, x=timer_df_2threads['Cores'], y=timer_df_2threads['Time'], errorbar = scitest, capsize = 0.3, color= 'orange', errwidth= 0.75, join =False )
        sns.boxplot(data=timer_df_2threads, x=timer_df_2threads['Cores'],    y=timer_df_2threads['Time'], showcaps= False, linewidth= 0.5, color= 'orange',  label = '2threads' , whis=(0,100), showmeans =True, meanprops={"marker":"s","markerfacecolor":"white", "markeredgecolor":"blue"})

        

        for core in cores:

            core_df = mean_df[mean_df['Cores'] ==core]

            sci_timer = mean_df[mean_df['Timer'] == timer]
            table_data = sci_timer[['Cores', 'Mean Difference', 'Bounds']].copy()
            table_data['Bounds'] = table_data['Bounds'].apply(lambda x: f'({np.exp(x[0]):.2f}, {np.exp(x[1]):.2f})')
            table_data['Mean Difference'] = table_data['Mean Difference'].apply(lambda x: f'{np.exp(x):.2f}')
            
          
            table_data = table_data.values

        col_labels = ["Nodes", 'MPI Speedup' , "99% CI: (LL, UL)" ]
        table = plt.table(cellText=table_data, colLabels=col_labels, cellLoc='center', loc='bottom', bbox=[0, -0.75, 1, 0.5])


        plt.subplots_adjust(bottom=0.4)

        #sns.pointplot(data = ideal_time_df, x = 'Cores', y='Ideal Times', marker='o', label ='Ideal-Time', linestyle='--')
        plt.xlabel('Nodes')
        plt.ylabel('Wall-clock time')
        plt.legend()
        plt.ylim(ymin = 0)
        plt.title(f'Timer: {timer}')
        plt.savefig(f'{timer} Boxplot with mean errror bars', dpi =300)