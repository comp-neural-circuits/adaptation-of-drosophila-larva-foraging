# preprocess_data.py
# Reads the data, applies the RDP algorithm and saves it as a single dataframe.

#%%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pathlib # to find current path
from tqdm import tqdm

import sys
import regex

import itertools

from rdp import rdp

path_thisfile = pathlib.Path(__file__).parent.resolve() 

path_data = path_thisfile / 'Data' 

if not path_data.is_dir():
  raise ValueError(f"\nDirectory `{path_data}` does not exist!")

arenas = ['Homogeneous', 'Two_patches', 'Nonnutrient_patches', 'Eight_patches']
substrates = ['Sucrose','Yeast','Agar','Gel','Apple_juice']
larvae = ['Rover','Sitter','Anosmic']

for dd in arenas:
  dfull = path_data/dd
  if not dfull.is_dir():
    raise ValueError(f"\nDirectory `{dfull}` does not exist, please import the data first!")


all_combinations = itertools.product(arenas,substrates,larvae) 

def path_in_data(combination):
  arena,sub,lar = combination
  fullpath = path_data / arena / sub / lar
  if fullpath.is_dir():
    return fullpath
  else:
    return pathlib.Path('')

all_paths =[]
path_elements = []

for combination in all_combinations:
  fullpath = path_in_data(combination)
  if len(str(fullpath)) > 5:
    all_paths.append(fullpath)
    path_elements.append(combination)
    
  
n_sessions = len(all_paths)  

#%%%

def clean_format_data(
    data_as_csv, frames_list, exp_ind, factor_frames, factor_frames2):
    """
    Just cleans the information in the experimental spreadsheets and organizes
    the data in a dataframe

    Parameters
    ----------
    data_as_csv: DataFrame
        contains output of FIMTrack software
    frames_list: list
        just stores the info about number of frames in each experiment
    exp_ind: int
        index of experiment (1, 2, 3)
    factor_frames: int
        number to divide the spreadsheet length to keep only coords info
    factor_frames2: int
        depending on how the table was generated, we redefine factor_frames

    Returns
    -------
    data_clean: DataFrame
        organized dataframe with clean data
    frames_list_aux: list
        accumulates info about number of frames per experiment
    """
    data_as_csv = data_as_csv.select_dtypes(exclude=['object'])
    #
    # this a trick because some tables have all the info available and others
    # have only information about x,y coordinates... I know that there are no tables with less
    # than 4000 frames :)
    # I also check if the total number of coordinates is an even number,
    # because half the coordinates are x and the other half is y.
    #
    frames = int(len(data_as_csv)/factor_frames)
    if frames < 4000:
        frames = int(len(data_as_csv)/factor_frames2)
    data_clean = data_as_csv[0:frames]
    # drop columns that have ALL NaN values
    data_clean = data_clean.dropna(how='all',axis=1)
    name_list = []
    for ii in range(len(data_clean.columns)):
        name_list.append('exp' + str(exp_ind) + '_larva_' + str(ii))
    data_clean.columns = name_list
    frame_list_aux = np.append(frames_list, len(name_list)*[frames], axis = 0)
    if frames%2 != 0:
      raise ValueError('Error, odd number of frames on table' + str(exp_ind))
    return(data_clean, frame_list_aux)



#%%%

def get_exp_and_larva_str(k:str):
  rr=regex.search('^exp([0-9]*)_larva_([0-9]*)$',k)
  assert not (rr is None) , f"wrong string value! Cannot parse this: {k} "
  return 'exp'+rr.group(1),'L'+rr.group(2)

def read_single_dataset(arena,substrate,larva,datapath,scale=8.0,dt=0.5):
  #scale is number of pixels per mm
  #dt = 0.5 # frame rate = 2 Hz
  factor_frames = 15 # when the table is bigger and has more lines than necessary
  factor_frames2 = 1 # when the table is small

  print(f"""
  ############################
      Now reading and processing data from:
      arena      : {arena}
      substrate  : {substrate}
      larva type : {larva}
  ##############################    
        """)
  if not datapath.is_dir():
    raise ValueError(f"\nDirectory `{datapath}` does not exist!")
 
  rdp_epsilon =  10/scale if 'Yeast' in substrate else 20/scale
  
  data_total = []
  frames_list = []
  data_aux = pd.read_csv(datapath / 'table1.csv', header = None)
  data1, frames_list = clean_format_data(data_aux, frames_list, 1, factor_frames, factor_frames2)
  data_aux = pd.read_csv(datapath / 'table2.csv', header = None)
  data2, frames_list = clean_format_data(data_aux, frames_list, 2, factor_frames, factor_frames2)
  path_tab3 = datapath / 'table3.csv'
  all_three = path_tab3.is_file()
  if not all_three:
    print('\n Warning! This experiment only has 2 sessions instead of 3 \n')
  if all_three:
    data_aux = pd.read_csv(path_tab3, header = None)
    data3, frames_list = clean_format_data(data_aux, frames_list, 3, factor_frames, factor_frames2)
    data_total = pd.concat([data1, data2, data3], axis=1)
  else:
    data_total = pd.concat([data1, data2], axis=1)
  frames_info = np.transpose(pd.DataFrame(frames_list))
  # read patch centers in two patches experiments
  is_two_patches = (arena == 'Two_patches') or (arena == 'Nonnutrient_patches')
  is_eight_patches = arena == 'Eight_patches'
  if is_two_patches:
    patch_files = ['ROI_coord1.csv', 'ROI_coord2.csv','ROI_coord3.csv'] if all_three \
      else ['ROI_coord1.csv', 'ROI_coord2.csv']
    patch_info = [pd.read_csv(datapath / pf, header=None) for pf in patch_files]
  if is_eight_patches:
    patch_files = ['ROI_coord1.csv', 'ROI_coord2.csv','ROI_coord3.csv'] if all_three \
      else ['ROI_coord1.csv', 'ROI_coord2.csv']
    patch_info = [pd.read_csv(datapath / pf, skiprows=[0],header=None) for pf in patch_files]

  # experiment number and larva number
  mult = pd.MultiIndex.from_tuples([get_exp_and_larva_str(s) for s in  data_total.columns.values])
  data_total.columns=mult
  frames_info.columns=mult
  dfout = pd.DataFrame(index=mult,columns=['x','y','nframes','time',\
     'simple_trajectory','idx_turn_points','rdp_mask','rdp_epsilon','patch_info'])
  for mm in mult:
    nfra = int(frames_info.loc[0,mm]/2)
    xy = data_total.loc[:,mm].values/scale # convert to millimeters here
    x = xy[0:nfra]
    y = xy[nfra:2*nfra] # removes extra tail of NaN added by first dataframe operation
    coord_nan = np.isnan(x)
    assert not np.all(np.isnan(x)) , 'All values are NaNs... why?'
    time_points = np.arange(0,nfra,1)
    time = time_points * dt
    total_times = time_points[~coord_nan]
    coord_fix = np.column_stack([x[~coord_nan],y[~coord_nan]])
    simple_traj = rdp(coord_fix, epsilon=rdp_epsilon)
    rdp_mask = rdp(coord_fix, epsilon=rdp_epsilon, return_mask = True)
    idx_turn_points = total_times[rdp_mask]
    dfout.loc[mm,'nframes'] = nfra
    dfout.loc[mm,'x'] = x
    dfout.loc[mm,'y'] = y
    dfout.loc[mm,'time'] = time
    dfout.loc[mm,'simple_trajectory'] = simple_traj
    dfout.loc[mm,'idx_turn_points'] = idx_turn_points
    dfout.loc[mm,'rdp_mask'] = rdp_mask
    dfout.loc[mm,'rdp_epsilon'] =rdp_epsilon
    # add patch coordinates and radii
    if is_two_patches or is_eight_patches:
      if mm[0] == 'exp1':
        my_patch = patch_info[0]
      elif mm[0] == 'exp2':
        my_patch = patch_info[1]
      elif mm[0] == 'exp3':
        my_patch = patch_info[2]
      else:
        raise Exception('Wrong experiment parameter {} '.format(mm[0]))
      # also, convert to millimiters
      if is_two_patches:
        dfout.loc[mm,'patch_info'] =\
          [[my_patch[1][k]/scale, my_patch[2][k]/scale, my_patch[3][k]/(2*np.pi*scale)] for k in range(2)]
      elif is_eight_patches:
        dfout.loc[mm,'patch_info'] =\
          [[my_patch[1][k]/scale, my_patch[2][k]/scale, my_patch[3][k]/(2*np.pi*scale)] for k in range(8)]
  if "Nonnutrient" in arena:
    arena= "Nonnutrient"
  elif "Two" in arena:
    arena= "Two"
  elif "Eight" in arena:
    arena= "Eight"
  # add extra indexes for environment, substrate and larva  
  supermult = pd.MultiIndex.from_tuples([ \
     (arena,substrate,larva) + others for others in dfout.index.values])
  dfout.index = supermult
  return dfout

#%%

print("""
------------------------------------------
Starting to read and preprocess all data.
*WARNING* this might take up to 30 min.
------------------------------------------
      """)

df_read = []

for k in tqdm(range(n_sessions)): # n_sessions
  arena, substrate, larva = path_elements[k]
  fullpath = all_paths[k]
  df_read.append(read_single_dataset(arena, substrate, larva, fullpath))
  pass

data_all = pd.concat(df_read)

savename = path_thisfile / 'data_all_rdp.pkl.xz'

print(f"""
      **READING DONE!**
      Now saving as {savename}
      """)

data_all.to_pickle(savename)
