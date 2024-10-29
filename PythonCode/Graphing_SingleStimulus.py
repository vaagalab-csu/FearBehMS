# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 13:57:56 2022

@author: chris
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import pandas as pd
import os
import matplotlib as mpl
import matplotlib.cm as cm


matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
plt.rcParams["font.family"] = "Arial"

freeze_threshold = 2
dart_threshold = 32.5
frame_rate = 30

#%%
# Load csv files and generate velocity matrices for each cohort: 
    

title = '1xSweepF'

cohort_directory = r"C:\Users\chris\Desktop\Behavior Manuscript\Figure2\DLC Output\Loom (30fps)\MF Combined\SingleTrial"
analysis_directory = r"C:\Users\chris\Desktop\Behavior Manuscript\Figure2"

cohort_filenames = os.listdir(cohort_directory)

os.chdir(cohort_directory)

sample_data = pd.read_csv(cohort_filenames[0], header = 2)
all_velocity = np.zeros((len(cohort_filenames), len(sample_data)))
all_below_threshold = np.zeros((len(cohort_filenames), len(sample_data)))
all_below_threshold_time = np.zeros((len(cohort_filenames), len(sample_data)))


fig, (ax1, ax2) = plt.subplots(2,1, sharex = True, dpi = 300, figsize = (4,3), gridspec_kw={'height_ratios': [1.5,2]})
for animals in range(len(cohort_filenames)):
    data = pd.read_csv(cohort_filenames[animals], header = 2)
    
    length_array = len(data['x'])
    body_parts = 7
    
    vid_length = length_array / frame_rate
    vid_time_array = np.linspace(0,vid_length,length_array) - 10
    avg_time_int = vid_length / length_array
    
    pixel_to_cm = 25/235 #conversion factor to convert number of pixels      
    
    x_coord_data = np.zeros((length_array,body_parts))
    y_coord_data = np.zeros((length_array,body_parts))
    
    
    for i in range(0,body_parts):
        if i == 0:
            string = 'x'
        else:
            string = 'x.'+str(i)
        x_coord_data[:,i] = data[string]
 
        if i == 0:
            string = 'y'
        else:
            string = 'y.'+str(i)
        y_coord_data[:,i] = data[string]
        
    x_coord_avg = np.mean(x_coord_data,axis = 1) * pixel_to_cm
    y_coord_avg = np.mean(y_coord_data,axis = 1) * pixel_to_cm
        
    velocity = np.zeros(length_array)    
    
    below_threshold_velocity = np.zeros((length_array))
    below_threshold_time = np.zeros((length_array))
    above_threshold_velocity = np.zeros((length_array))
    above_threshold_time = np.zeros((length_array))
    darting_velocity = np.zeros((length_array))
    darting_time = np.zeros((length_array))
    
    for k in range(length_array-1):
        velocity[k] = (np.sqrt((x_coord_avg[k+1]-x_coord_avg[k])**2 +
                            (y_coord_avg[k+1]-y_coord_avg[k])**2)) / avg_time_int


    
    for x in range(10,length_array):
        if np.all(velocity[x-5:x+5] < freeze_threshold):
            below_threshold_velocity[x] = velocity[x]
            below_threshold_time[x] = vid_time_array[x]
            
    for x in range(10,length_array):
        if np.all(velocity[x-5:x+5] > dart_threshold):
            darting_velocity[x] = velocity[x]
            darting_time[x] = vid_time_array[x]

    
    below_threshold_velocity[below_threshold_velocity == 0] = np.nan
    below_threshold_velocity[below_threshold_velocity != np.nan] = 1
    below_threshold_time[below_threshold_time == 0] = np.nan
    
    all_velocity[animals,:] = velocity
    all_below_threshold[animals,:] = below_threshold_velocity
    all_below_threshold_time[animals,:] = below_threshold_time

#Selects first 3 from cohort and last 3 from cohort - shows M and F equally if combined sex
total = len(cohort_filenames)
listanimals = np.arange(0,total,1)
waterfall_position = np.linspace(0,total,total)

all_velocity2 = all_velocity

for i in range(len(listanimals)):
    vel_temp = all_velocity[listanimals[i],:]
    below_temp = all_below_threshold[listanimals[i],:]
    below_temp_time = all_below_threshold_time[listanimals[i],:]
    
    ax1.plot(below_temp_time, below_temp + waterfall_position[i], linewidth = 1.5, color = 'red')
 
#plt.plot(vid_time_array,all_velocity[i,:]+waterfall_position[i], linewidth = 0.5, color = 'black')
#plt.plot(all_below_threshold_time[i,:], all_below_threshold[i,:]+ waterfall_position[i], linewidth = 0.5, color = 'red')
ax1.set_xlim(-10,30)
ax1.set_ylim(0,len(listanimals)+2)
ax1.set_yticks([0,5,10,15,20])
ax1.axvspan(0, 20, alpha=0.25, color='grey')
ax1.set_ylabel('Animal ID')
#plt.title(title)

all_velocity2 = all_velocity
new_avg = all_velocity

for i in range(new_avg.shape[0]):
    tmp_velocity = new_avg[i,:]
    tmp_velocity[tmp_velocity < 2] = 1
    tmp_velocity[tmp_velocity > 2] = 0
    
    new_avg[i,:] = tmp_velocity
    
avg_freeze = np.mean(new_avg, axis = 0)
avg_freeze = avg_freeze[0:-1]

avg_freeze_smoothed = []
window_size = 10
i = 0
while i < len(avg_freeze) - window_size + 1:
   
    window = avg_freeze[i : i + window_size]
 
    # Calculate the average of current window
    window_average = round(sum(window) / window_size, 2)
     
    # Store the average of current
    # window in moving average list
    avg_freeze_smoothed.append(window_average)
     
    # Shift window to right by one position
    i += 1
    

ax2.plot(vid_time_array[0:-10],avg_freeze_smoothed, linewidth = 1, color = 'black')
ax2.set_ylim(0,1)
ax2.set_ylabel('% Animals Immobile')
ax2.set_xlabel('Time (sec)')




plt.tight_layout()



os.chdir(analysis_directory)
plt.savefig(title + '.pdf')




