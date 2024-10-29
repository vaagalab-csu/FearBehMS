# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 12:24:18 2020

@author: RamanLab
"""


    
    
def generate_velocity_matrix(frame_rate, freeze_path):
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    import os
        
    
    os.chdir(freeze_path)
    filenames = os.listdir(freeze_path)
    
    data = pd.read_csv(filenames[0], header = 2)
    
    length_array = len(data['x'])
    body_parts = 6
    
    vid_length = length_array / frame_rate
    vid_time_array = np.linspace(0,vid_length,length_array) - 10
    avg_time_int = vid_length / length_array
    velocity_matrix = np.zeros((length_array,len(filenames)))
    position_matrix_x = np.zeros((length_array,len(filenames)))
    position_matrix_y = np.zeros((length_array,len(filenames)))
    
    arena_length_cm = 25
    arena_length_pixels = 230 #For current raspberry pi videos!!!
    pixel_to_cm = arena_length_cm/arena_length_pixels #conversion factor to convert number of pixels 
    freeze_threshold = 2
      
    
    for j in range(len(filenames)):  
        data = pd.read_csv(filenames[j], header = 2)
        x_coord_data = np.zeros((length_array,body_parts))
        y_coord_data = np.zeros((length_array,body_parts))
        
        for i in range(0,body_parts):
            if i == 0:
                string = 'x'
            else:
                string = 'x.'+str(i)
            x_coord_data[:,i] = data[string][0:2250]
            if i == 0:
                string = 'y'
            else:
                string = 'y.'+str(i)
            y_coord_data[:,i] = data[string][0:2250]
            
        x_coord_avg = np.mean(x_coord_data,axis = 1) * pixel_to_cm
        y_coord_avg = np.mean(y_coord_data,axis = 1) * pixel_to_cm
        
        velocity = np.zeros(length_array)
        velocity_smoothed = np.zeros(length_array)
        
        for k in range(length_array-1):
            velocity[k] = (np.sqrt((x_coord_avg[k+1]-x_coord_avg[k])**2 +
                                (y_coord_avg[k+1]-y_coord_avg[k])**2)) / avg_time_int
            
        for k in range(5,length_array-5):
                velocity_smoothed[k] = np.mean(velocity[k-5:k+5]) 
                
        velocity_matrix[:,j] = velocity_smoothed
        position_matrix_x[:,j] = x_coord_avg
        position_matrix_y[:,j] = y_coord_avg
    
    return velocity_matrix, vid_time_array
    
def freeze_analysis(velocity, freeze_threshold, frame_rate):
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    import os
    
    
    num_animals = velocity.shape[1]

    freeze_durations = [[]]
    latency = np.array([])
    
    
    for k in range(num_animals):
        baseline_time = 10
        len_record = velocity.shape[0]
        vid_length = len_record / frame_rate
        vid_time_array = np.linspace(0,vid_length,len_record) - baseline_time
        velocity_tmp = velocity[:,k]
        
        #remove leading/trailing 0's from record (from rolling average)
        velocity_tmp = velocity_tmp[5:-5]
        vid_time_array = vid_time_array[5:-5]


        test = np.diff(np.sign(velocity_tmp - freeze_threshold)) 
        
        freeze_enter = np.array([])
        freeze_exit = np.array([])
        
        freeze_enter = np.asarray(np.where(test < 0),dtype = 'float64').flatten()
        freeze_exit = np.asarray(np.where(test > 0),dtype = 'float64').flatten()
        

        
        #Filter enter/exit frames to be greater than 300 (frame start of stimulus with baseline 10 s)
        freeze_enter_filtered = np.array(list(filter(lambda x: (x > baseline_time * frame_rate), freeze_enter)))
        freeze_exit_filtered = np.array(list(filter(lambda x: (x >  baseline_time * frame_rate), freeze_exit)))
        
        freeze_enter_filtered = freeze_enter_filtered.astype('int')
        freeze_exit_filtered = freeze_exit_filtered.astype('int')
        
        if freeze_exit_filtered.size == 0: freeze_exit_filtered = np.append(freeze_exit_filtered,len_record-11)
        
        #correct for condition in which animal is freezing at end of record 
        if freeze_enter_filtered[-1] > freeze_exit_filtered[-1]: freeze_exit_filtered = np.append(freeze_exit_filtered, len_record-11)
        
        #correct for condition in which animal is freezing at the beginning of the record
        if freeze_enter_filtered[0] > freeze_exit_filtered[0]: 
            freeze_enter_filtered = np.insert(freeze_enter_filtered, 0, baseline_time * frame_rate)
        
        
        freeze_enter_time = vid_time_array[freeze_enter_filtered]
        freeze_exit_time = vid_time_array[freeze_exit_filtered]
        
        freeze_duration = freeze_exit_time - freeze_enter_time
        
        freeze_duration_filtered = np.array(list(filter(lambda x: (x > 1), freeze_duration)))
            
        
        freeze_durations.append(freeze_duration_filtered)
        
        latency = np.append(latency, min(freeze_enter_time))
        

        

    return freeze_durations, latency

def freeze_secondary_analysis(duration):
    
    
    import numpy as np
    
    freeze_matrix = np.zeros((len(duration), 3))
    
    freeze_sum = np.array([])
    freeze_mean = np.array([])
    freeze_median = np.array([])
    freeze_num_bout = np.array([])
    freeze_max_bout = np.array([]) 
    
    for i in range(len(duration)):
         freeze_matrix[i,0] = np.sum(duration[i])
         freeze_matrix[i,1] = len(duration[i])
         if len(duration[i]) == 0: freeze_matrix[i,2] = 0
         else: freeze_matrix[i,2] = np.max(duration[i])

    return freeze_matrix
                   
def freeze_pct(frame_rate, velocity, freeze_threshold, analysis_length, baseline):
    import numpy as np
    baseline = baseline * frame_rate #expresses baseline length in terms of number of frames
    analysis_length = analysis_length * frame_rate #expresses analysis length in terms of number of frames
    
    steps = [0, baseline, baseline+analysis_length]
    
    num_animals = velocity.shape[1] #Extract the number of animals/records being analyzed
    
    baseline_freeze = np.zeros(num_animals) #Create an empty array to hold baseline freeze duration
    stimulus_freeze = np.zeros(num_animals) #Create an empty array to hold stimulus freeze duration
    
    baseline_vel = np.array((baseline,num_animals)) #creates a 2d array with enough rows for each baseline frame and enough columns for each animal
    stimulus_vel = np.array((analysis_length, num_animals)) #creates a 2d array for stimulus velocity for each animal

    
    freeze_matrix = np.zeros((num_animals, 2))
    
    for an in range(num_animals):
        velocity_tmp = velocity[:,an]
        velocity_tmp = velocity_tmp[steps[0]:steps[-1]]
        for k in range(len(steps)-1):
            enter_frame = np.array([])
            exit_frame = np.array([])
            indx = []
    
            indx = np.diff(np.sign(velocity_tmp[steps[k]:steps[k+1]] - freeze_threshold))
    
            enter_frame = np.asarray(np.where(indx < 0),dtype = 'float64').flatten()
            exit_frame = np.asarray(np.where(indx > 0),dtype = 'float64').flatten()
            
            enter_frame = enter_frame + steps[k]
            exit_frame = exit_frame + steps[k]
        
            #Correction for if there are no exit frames (animal remains frozen in single bout through entire analysis period)
            if exit_frame.size == 0: exit_frame = np.append(exit_frame, steps[k+1])
            #Correction for if there are no enter frames(animal remains frozen in single bout through entire analysis period)
            if enter_frame.size == 0: enter_frame = np.append(enter_frame, steps[k])
            #Correction for if animal is already freezing at start of analysis window - add index of analysis start
            if enter_frame[0] > exit_frame[0]: enter_frame = np.insert(enter_frame,0,steps[k])
            if enter_frame[-1] > exit_frame[-1]: exit_frame = np.append(exit_frame,steps[k+1])
    
    
            duration = exit_frame - enter_frame
            
            #Filter list of durations for those over 15 frames in length (500 ms)
            duration_filtered = np.array(list(filter(lambda x: (x > round(frame_rate/2,0)), duration)))
            
            freeze_matrix[an,k] = (sum(duration_filtered) / (steps[k+1]-steps[k])) * 100  
    
    return freeze_matrix
    
def freeze_timeline(frame_rate, velocity, freeze_threshold, step_size, num_steps):
    import numpy as np
    step_size = step_size * frame_rate
    freeze_threshold = 2
    
    num_animals = velocity.shape[1]
    
    freeze_matrix = np.zeros((num_animals, num_steps))
    steps = np.array([0])
    
    for i in range(1,num_steps+1):
        steps = np.append(steps, steps[i - 1] + step_size)
    steps = steps.astype('int')
                       
    
    for an in range(num_animals):
        velocity_tmp = velocity[:,an]
        velocity_tmp = velocity_tmp[steps[0]:steps[-1]]
        for k in range(len(steps)-1):
            enter_frame = np.array([])
            exit_frame = np.array([])
            indx = []
    
            indx = np.diff(np.sign(velocity_tmp[steps[k]:steps[k+1]] - freeze_threshold))
    
            enter_frame = np.asarray(np.where(indx < 0),dtype = 'float64').flatten()
            exit_frame = np.asarray(np.where(indx > 0),dtype = 'float64').flatten()
            
            enter_frame = enter_frame + steps[k]
            exit_frame = exit_frame + steps[k]
        
            #Correction for if there are no exit frames (animal remains frozen in single bout through entire analysis period)
            if exit_frame.size == 0: exit_frame = np.append(exit_frame, steps[k+1])
            #Correction for if there are no enter frames(animal remains frozen in single bout through entire analysis period)
            if enter_frame.size == 0: enter_frame = np.append(enter_frame, steps[k])
            #Correction for if animal is already freezing at start of analysis window - add index of analysis start
            if enter_frame[0] > exit_frame[0]: enter_frame = np.insert(enter_frame,0,steps[k])
            if enter_frame[-1] > exit_frame[-1]: exit_frame = np.append(exit_frame,steps[k+1])
    
    
            duration = exit_frame - enter_frame
            
            #Filter list of durations for those over 15 frames in length (500 ms)
            duration_filtered = np.array(list(filter(lambda x: (round(frame_rate/2,0)), duration)))
            
            freeze_matrix[an,k] = (sum(duration_filtered) / step_size) * 100    
    
    return freeze_matrix
    
def freeze_timeline_2(frame_rate, velocity, freeze_threshold, step_size = 10, num_steps = 3):
    import numpy as np
    step_size = step_size * frame_rate
    freeze_threshold = 2
    
    num_animals = velocity.shape[1]
    
    freeze_matrix = np.zeros((num_animals, num_steps))
    steps = np.array([0])
    
    for i in range(1,num_steps+1):
        steps = np.append(steps, steps[i - 1] + step_size)
    steps = steps.astype('int')
                       
    
    for an in range(num_animals):
        velocity_tmp = velocity[:,an]
        velocity_tmp = velocity_tmp[steps[0]:steps[-1]]
        for k in range(len(steps)-1):
            enter_frame = np.array([])
            exit_frame = np.array([])
            indx = []
    
            indx = np.diff(np.sign(velocity_tmp[steps[k]:steps[k+1]] - freeze_threshold))
    
            enter_frame = np.asarray(np.where(indx < 0),dtype = 'float64').flatten()
            exit_frame = np.asarray(np.where(indx > 0),dtype = 'float64').flatten()
            
            enter_frame = enter_frame + steps[k]
            exit_frame = exit_frame + steps[k]
        
            #Correction for if there are no exit frames (animal remains frozen in single bout through entire analysis period)
            if exit_frame.size == 0: exit_frame = np.append(exit_frame, steps[k+1])
            #Correction for if there are no enter frames(animal remains frozen in single bout through entire analysis period)
            if enter_frame.size == 0: enter_frame = np.append(enter_frame, steps[k])
            #Correction for if animal is already freezing at start of analysis window - add index of analysis start
            if enter_frame[0] > exit_frame[0]: enter_frame = np.insert(enter_frame,0,steps[k])
            if enter_frame[-1] > exit_frame[-1]: exit_frame = np.append(exit_frame,steps[k+1])
    
    
            duration = exit_frame - enter_frame
            
            #Filter list of durations for those over 15 frames in length (500 ms)
            duration_filtered = np.array(list(filter(lambda x: (round(frame_rate/2,0)), duration)))
            
            freeze_matrix[an,k] = (sum(duration_filtered) / step_size) * 100  


def velocity_analysis(frame_rate, velocity, baseline, analysis):
    import numpy as np
    
    base_start = 0
    base_end = frame_rate * baseline
    
    stim_start = base_end + 1
    stim_end = stim_start + (baseline * frame_rate)
    
    num_animals = velocity.shape[1]
    

    velocity_matrix = np.zeros((num_animals, 2))
    
    for an in range(num_animals):
        velocity_tmp = velocity[:,an]
        baseline = np.mean(velocity_tmp[base_start:base_end])
        stimulus = np.mean(velocity_tmp[stim_start:stim_end])
        
        velocity_matrix[an,0] = baseline
        velocity_matrix[an,1] = stimulus
    return velocity_matrix    
        
    
    

    
    