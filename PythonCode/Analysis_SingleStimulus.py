# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 10:09:37 2021

@author: RamanLab
"""


# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 12:31:06 2021

@author: RamanLab
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import pandas as pd
import os

#Change directory to code folder
os.chdir(r"C:\Users\chris\Desktop\Raw Data\Python Code")
from FreezingAnalysis_Scripts2 import generate_velocity_matrix, freeze_analysis, freeze_secondary_analysis, freeze_pct, freeze_timeline

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

freeze_threshold = 2
frame_rate = 30


    
path = r"C:\Users\chris\Desktop\Raw Data\Figure2\Loom (30fps)\MF Combined"


#SET APPROPRIATE TITLES
c1_s1_title = 'Single_Loom_MFCombined'


#SET COHORT NAME
cohort_name = 'Single_Loom_MFCombined'







#Test if python Output folder exists - if not, create it.

os.chdir(path)
if not os.path.exists('PythonOutput'):
    os.makedirs('PythonOutput')
parent_dir = path + '/' + 'PythonOutput'
os.chdir(parent_dir)


    
c1_s1_csv = path + '\singleTrial'

# Load csv files and generate velocity matrices for each cohort: 
c1_s1_files = os.listdir(c1_s1_csv)
for i in range(len(c1_s1_files)):
    c1_s1_files[i] = c1_s1_files[i][0:19]




c1_s1_velocity, c1_s1_time = generate_velocity_matrix(frame_rate, c1_s1_csv)
 


c1_s1_duration, c1_s1_latency = freeze_analysis(c1_s1_velocity, freeze_threshold, frame_rate); del(c1_s1_duration[0])



c1_s1_freeze_data = freeze_secondary_analysis(c1_s1_duration)

c1_s1_freeze_pct = freeze_pct(frame_rate, c1_s1_velocity, freeze_threshold, 20, 10)


c1_s1_freeze_timeline = freeze_timeline(frame_rate, c1_s1_velocity, freeze_threshold, 10, 7)





# Convert numpy arrays to dataframes for export to csv/prism
c1_s1_dataframe = pd.DataFrame(data = c1_s1_freeze_data, index = c1_s1_files, columns = ['Duration (s)', 'Num Bouts', 'Max Bout'])
c1_s1_freeze_pct_df = pd.DataFrame(data = c1_s1_freeze_pct, index = c1_s1_files, columns = ['Baseline Freeze Pct', 'Stimulus Freeze Pct'])
c1_s1 = pd.concat([c1_s1_dataframe, c1_s1_freeze_pct_df], axis = 1)





analysis_windows = ['-10 - 0s', '0 - 10s', '10 - 20s', '20 - 30s', '30 - 40s', '40 - 50s', '50 - 60s']
c1_s1_freeze_timeline_dataframe = pd.DataFrame(data = c1_s1_freeze_timeline, index = c1_s1_files, columns = analysis_windows)


excel_filename = cohort_name + '.xlsx'

#Save to Excel file
os.chdir(parent_dir)
with pd.ExcelWriter(excel_filename) as writer:
    c1_s1.to_excel(writer, sheet_name = 'Session1_Freezing Analysis')
    c1_s1_freeze_timeline_dataframe.to_excel(writer, sheet_name = 'Session1_Freeze Timeline')
    


