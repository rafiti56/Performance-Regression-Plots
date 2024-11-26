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

class case:
    def __init__(self, folder_path, file_pattern):
        self.folder_path =folder_path
        self.results ={}
        self.file_pattern  = file_pattern

    def get_sorted_files(self):
        #define function get_sorted_file swhich takes folder_path and file_pattern as inputs
        files = os.listdir(self.folder_path)
        #retrieves a list of all files and directories in the specified folder path
        matched_files = [f for f in files if re.match(self.file_pattern, f)]
        #sorts through files in folder and retrieves a list of all files that match the specified file pattern
        sorted_files = sorted(matched_files, key=lambda x: (int(re.findall(r'\d+', x)[0]), int(re.findall(r'run(\d+)', x)[0])))
        #sorts the matched files, lambda is a pyython featuer that creates anonymous functions, it then extracts the numerical values in the filenames as a tuple(primary, secondary)
        return sorted_files

    def process_files(self):
        #specifies file pattern
        file_pattern = self.file_pattern # Adjust the pattern as needed to match the specific files
        sorted_files = self.get_sorted_files()
        #calls for get_sorted files function and assigns it to sorted_files
        
        
        for filename in sorted_files:
            #for each filename in sorted_files (loops through each item on the list)
            file_path = os.path.join(self.folder_path, filename)
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

def scitest(y, conf = 0.99):
    
    n = len(y)
    var = tdist.ppf((1 + conf)/2, n-1)
    std_error = (y.std() / np.sqrt(n))
    mean = np.mean(y)
    upper_bound = mean + var*std_error
    lower_bound = mean - var*std_error
    return (lower_bound, upper_bound)


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


def trim_mean(x, p=.1):
    '''
    Trim a series to remove egregious outliers, and then return the mean.
    Input:
        x : series to trim
        p : maximum proportion of data to remove
    '''
    return trim(x, p).mean()

def trim_std(x, p=.1):
    '''
    Trim a series to remove egregious outliers, and then return the standard deviation.
    Inputs:
        x : series to trim
        p : maximum proportion of data to remove
    '''
    print(trim(x, p).std())
    return trim(x, p).std()

def trimmed_stats(x, p=.1, var=True):
    '''
    Get trimmed mean and std or variance
    '''
    if var:
        return trim_mean(x, p), np.square(trim_std(x, p))
    else:
        return trim_mean(x, p), trim_std(x, p)
    
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

if __name__ == "__main__":
    #Change to folder path where the text files are located
    folder_path = r'C:\Users\rcaller\Documents\GitHub\Performance-Regression-Plots\text_files\serial_gauss_vs_serial_block_vs_4threads'


    #Change data_'variable_name1' in all ocurrences
    data_GaussSeidel = case(folder_path, r'new_cores\d+_run\d+')

    data_BlockJacobi = case(folder_path, r'old_cores\d+_run\d+')
    #Change _'variable_name2' in all ocurrences
    data_4threads = case(folder_path, r'OP4_cores\d+_run\d+')

    data_4threads.process_files()

    data_GaussSeidel.process_files()

    data_BlockJacobi.process_files()

    data_list =[]

    #Change labeling
    process_data(data_4threads.results, '4threads')
    process_data(data_GaussSeidel.results, 'GaussSeidel')
    process_data(data_BlockJacobi.results, 'BlockJacobi')

        
    # Convert the list to a DataFrame
    df = pd.DataFrame(data_list)

    # Now df contains the combined data from both datasets with an additional 'Dataset' column to distinguish them

    #Add a new colum to get the ratio of linear iterations/non-linear iterations for the solver
    #USe "np.floor function to round down to get an integer"
    df['Linear/Nonlinear'] = np.floor(df['No of Linear Iterations'] / df['No of NonLinear Iterations'])

    avgIters = []
    #Creates a ne wempty list to loop over and store the avgIterations values from the df Dataframe, it then takes the average number of the ratio of linear/nonlinear iterations for each unique core count in a Dataset
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
            
    avgItersDf = pd.DataFrame(avgIters)

    plt.figure()


    sns.pointplot( data=avgItersDf, x='Cores', y='Average Iterations', hue='Dataset', dodge= True )
    plt.xlabel('Nodes')
    plt.ylabel('Average No. of Iterations')


    plt.title(f'Linear / NonLinear Iterations ')
    #plt.savefig(f'No of Iterations', dpi =300)

    df_4threads = df[df['Dataset'] == '4threads']

    df_GaussSeidel = df[df['Dataset'] == 'GaussSeidel']

    df_BlockJacobi = df[df["Dataset"] == 'BlockJacobi']


    altered_BlockJacobi = df_BlockJacobi.melt(id_vars=['Cores', 'Run', 'Dataset'], var_name ='Timer', value_name= 'Time')
    altered_4threads = df_4threads.melt(id_vars=['Cores', 'Run', 'Dataset'], var_name ='Timer', value_name= 'Time')
    altered_GaussSeidel = df_GaussSeidel.melt(id_vars=['Cores', 'Run', 'Dataset'], var_name ='Timer', value_name= 'Time')

    timers = ['Albany Piro', 'Total Fill Time', 'Precond', 'Total Lin']
    cores = [4,8,16,32,64]

    final_time_BlockJacobi = df_BlockJacobi.drop(['No of NonLinear Iterations', 'No of Linear Iterations', 'Linear/Nonlinear'], axis =1)

    final_time_GaussSeidel = df_GaussSeidel.drop(['No of NonLinear Iterations', 'No of Linear Iterations', 'Linear/Nonlinear'], axis =1)

    final_time_4threads = df_4threads.drop(['No of NonLinear Iterations', 'No of Linear Iterations', 'Linear/Nonlinear'], axis =1)

    final_BlockJacobi_melt = final_time_BlockJacobi.melt(id_vars=['Cores', 'Run', 'Dataset'], var_name ='Timer', value_name= 'Time')

    final_GaussSeidel_melt = final_time_GaussSeidel.melt(id_vars=['Cores', 'Run', 'Dataset'], var_name ='Timer', value_name= 'Time')

    final_4threads_melt = final_time_4threads.melt(id_vars=['Cores', 'Run', 'Dataset'], var_name ='Timer', value_name= 'Time')

    efficiency_df_BlockJacobi = pd.DataFrame()
    efficiency_df_4threads = pd.DataFrame()
    efficiency_df_GaussSeidel = pd.DataFrame()

    for timer in timers:
            
            efficiency_df_BlockJacobi[f"Efficiency {timer}"] = efficiency(df_BlockJacobi, timer,cores)
            efficiency_df_4threads[f"Efficiency {timer}"] = efficiency(df_4threads, timer,cores)
            efficiency_df_GaussSeidel[f"Efficiency {timer}"] = efficiency(df_GaussSeidel, timer,cores)

            df_sorted_BlockJacobi = df_BlockJacobi.sort_values(by=['Run', 'Cores',])
            df_sorted_4threads = df_4threads.sort_values(by=['Run', 'Cores', ]) 
            df_sorted_GaussSeidel = df_GaussSeidel.sort_values(by=['Run', 'Cores', ]) 

            df_final_BlockJacobi = pd.concat([df_sorted_BlockJacobi.reset_index(drop=True), efficiency_df_BlockJacobi.reset_index(drop=True)], axis=1)
            df_final_4threads =  pd.concat([df_sorted_4threads.reset_index(drop=True), efficiency_df_4threads.reset_index(drop=True)], axis=1)
            df_final_GaussSeidel = pd.concat([df_sorted_GaussSeidel.reset_index(drop=True), efficiency_df_GaussSeidel.reset_index(drop=True)], axis=1)

    df_eff_4threads = df_final_4threads.drop(['Albany Piro', 'Total Fill Time', 'Precond', 'Total Lin', 'No of Linear Iterations', "No of NonLinear Iterations", 'Linear/Nonlinear'], axis =1 )
    
    eff_plot_4threads = df_eff_4threads.melt(id_vars=['Cores', 'Run', 'Dataset'], var_name = 'Efficiency', value_name = 'Percentage')


    df_eff_GaussSeidel = df_final_GaussSeidel.drop(['Albany Piro', 'Total Fill Time', 'Precond', 'Total Lin', 'No of Linear Iterations', "No of NonLinear Iterations", 'Linear/Nonlinear'], axis =1 )

    eff_plot_GaussSeidel = df_eff_GaussSeidel.melt(id_vars=['Cores', 'Run', 'Dataset'], var_name = 'Efficiency', value_name = 'Percentage')

    
    df_eff_BlockJacobi = df_final_BlockJacobi.drop(['Albany Piro', 'Total Fill Time', 'Precond', 'Total Lin', 'No of Linear Iterations', "No of NonLinear Iterations", 'Linear/Nonlinear'], axis =1 )
    eff_plot_BlockJacobi = df_eff_BlockJacobi.melt(id_vars=['Cores', 'Run', 'Dataset'], var_name = 'Efficiency', value_name = 'Percentage')

    unique_effs = eff_plot_4threads['Efficiency'].unique()



    for i, timer in enumerate(unique_effs):
        eff_df_GaussSeidel = eff_plot_GaussSeidel[eff_plot_GaussSeidel['Efficiency'] == timer]
        eff_df_4threads = eff_plot_4threads[eff_plot_4threads['Efficiency'] == timer]
        eff_df_BlockJacobi = eff_plot_BlockJacobi[eff_plot_BlockJacobi['Efficiency'] == timer]

        plt.figure()
        #unique_xs= sorted(eff_df['Cores'].unique())
        sns.pointplot( data=eff_df_4threads, x=eff_df_4threads['Cores'], y=eff_df_4threads['Percentage'], errorbar = scitest, capsize = 0.3, color = 'red', errwidth= 0.75, join =False, dodge= True )
        sns.boxplot(data=eff_df_4threads, x=eff_df_4threads['Cores'],    y=eff_df_4threads['Percentage'], showcaps= False, linewidth= 0.5, color= 'red', label = '4threads', whis=(0,100), showmeans =True, meanprops={"marker":"s","markerfacecolor":"white", "markeredgecolor":"blue"}, dodge= True)

        sns.pointplot( data=eff_df_GaussSeidel, x=eff_df_GaussSeidel['Cores'], y=eff_df_GaussSeidel['Percentage'], errorbar = scitest, capsize = 0.3, color= 'orange', errwidth= 0.75, join =False , dodge = True)
        sns.boxplot(data=eff_df_GaussSeidel, x=eff_df_GaussSeidel['Cores'],    y=eff_df_GaussSeidel['Percentage'], showcaps= False, linewidth= 0.5, color= 'orange', label = 'GaussSeidel', whis=(0,100), showmeans =True, meanprops={"marker":"s","markerfacecolor":"white", "markeredgecolor":"blue"}, dodge= True)

        sns.pointplot( data=eff_df_BlockJacobi, x=eff_df_BlockJacobi['Cores'], y=eff_df_BlockJacobi['Percentage'], errorbar = scitest, capsize = 0.3, color= 'orange', errwidth= 0.75, join =False , dodge = True)
        sns.boxplot(data=eff_df_BlockJacobi, x=eff_df_BlockJacobi['Cores'],    y=eff_df_BlockJacobi['Percentage'], showcaps= False, linewidth= 0.5, color= 'orange', label = 'BlockJacobi', whis=(0,100), showmeans =True, meanprops={"marker":"s","markerfacecolor":"white", "markeredgecolor":"blue"}, dodge= True)

        plt.xlabel('Nodes')
        plt.ylabel('Percentage')
        plt.legend()
        plt.title(f'Box Plot with Mean Error Bars - Efficiency: {timer}')
        #plt.savefig(f'Efficiency {timer} Boxplot with mean errror bars', dpi =300)

    """ mean_list = []

    for core in cores:
        
        core_group_4threads = df_4threads[df_4threads['Cores']== core]
        core_group_GaussSeidel = df_GaussSeidel[df_GaussSeidel['Cores']== core]

        for timer in timers:

            log_mean, log_lower, log_upper= trimmed_ttest_bounds(np.log(core_group_GaussSeidel[timer]), np.log(core_group_4threads[timer]))
            mean_list.append({
                'Cores': core,
                'Timer': timer,
                'Mean Difference': log_mean,
                'Bounds': (log_lower,log_upper)
            })
    mean_df = pd.DataFrame(mean_list) """

    unique_timers = final_4threads_melt['Timer'].unique()

    for i, timer in enumerate(unique_timers):
        # Filter dataframe for the current timer
        timer_df_4threads = final_4threads_melt[final_4threads_melt['Timer'] == timer]
        timer_df_GaussSeidel = final_GaussSeidel_melt[final_GaussSeidel_melt['Timer'] == timer]
        timer_df_BlockJacobi = final_BlockJacobi_melt[final_BlockJacobi_melt['Timer'] == timer]
        
        plt.figure()
        unique_sorted_4threads= sorted(timer_df_4threads['Cores'].unique())
        #4threads
        sns.pointplot( data=timer_df_4threads, x=timer_df_4threads['Cores'], y=timer_df_4threads['Time'], errorbar = scitest, capsize = 0.3, color = 'red', errwidth= 0.75, join =False )
        sns.boxplot(data=timer_df_4threads, x=timer_df_4threads['Cores'],    y=timer_df_4threads['Time'], showcaps= False, linewidth= 0.5, color= 'red', label = '4threads', whis=(0,100), showmeans =True, meanprops={"marker":"s","markerfacecolor":"white", "markeredgecolor":"blue"})
        #GaussSeidel
        sns.pointplot( data=timer_df_GaussSeidel, x=timer_df_GaussSeidel['Cores'], y=timer_df_GaussSeidel['Time'], errorbar = scitest, capsize = 0.3, color= 'orange', errwidth= 0.75, join =False )
        sns.boxplot(data=timer_df_GaussSeidel, x=timer_df_GaussSeidel['Cores'],    y=timer_df_GaussSeidel['Time'], showcaps= False, linewidth= 0.5, color= 'orange',  label = 'GaussSeidel' , whis=(0,100), showmeans =True, meanprops={"marker":"s","markerfacecolor":"white", "markeredgecolor":"blue"})
        #BlockJacobi
        sns.pointplot( data=timer_df_BlockJacobi, x=timer_df_BlockJacobi['Cores'], y=timer_df_BlockJacobi['Time'], errorbar = scitest, capsize = 0.3, color= 'orange', errwidth= 0.75, join =False )
        sns.boxplot(data=timer_df_BlockJacobi, x=timer_df_BlockJacobi['Cores'],    y=timer_df_BlockJacobi['Time'], showcaps= False, linewidth= 0.5, color= 'orange',  label = 'BlockJacobi' , whis=(0,100), showmeans =True, meanprops={"marker":"s","markerfacecolor":"white", "markeredgecolor":"blue"})
        

        """ for core in cores:

            core_df = mean_df[mean_df['Cores'] ==core]

            sci_timer = mean_df[mean_df['Timer'] == timer]
            table_data = sci_timer[['Cores', 'Mean Difference', 'Bounds']].copy()
            table_data['Bounds'] = table_data['Bounds'].apply(lambda x: f'({np.exp(x[0]):.2f}, {np.exp(x[1]):.2f})')
            table_data['Mean Difference'] = table_data['Mean Difference'].apply(lambda x: f'{np.exp(x):.2f}')
            
            
            table_data = table_data.values

        col_labels = ["Nodes", 'MPI Speedup' , "99% CI: (LL, UL)" ]
        table = plt.table(cellText=table_data, colLabels=col_labels, cellLoc='center', loc='bottom', bbox=[0, -0.75, 1, 0.5]) """


        plt.subplots_adjust(bottom=0.4)

        #sns.pointplot(data = ideal_time_df, x = 'Cores', y='Ideal Times', marker='o', label ='Ideal-Time', linestyle='--')
        plt.xlabel('Nodes')
        plt.ylabel('Wall-clock time')
        plt.legend()
        plt.ylim(ymin = 0)
        plt.title(f'Timer: {timer}')
        plt.show()
        #plt.savefig(f'{timer} Boxplot with mean errror bars', dpi =300)
