# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Example: plot individual paths in dataset

# %% [markdown]
# In this notebook I load the dataset, and set up an interactive plot that will show any larva path in the dataset. When the arena is composed of two or eight food patches, the location of the patches is also displayed.

# %% [markdown]
# ## Initialize and read dataset

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pathlib
import ipywidgets as widgets

path_read = pathlib.Path('data_all_rdp.pkl.xz') 

assert path_read.is_file(), f"\nFile `{path_read}` does not exist ! \n ** Please make sure you have run `preprocess_data.py`**"
data_all = pd.read_pickle(path_read)
data_all = data_all.sort_index()

arenas = ['Homogeneous', 'Two', 'Eight', 'Nonnutrient']
substrates = ['Sucrose','Yeast','Agar','Gel','Apple_juice']
larvae = ['Rover','Sitter','Anosmic']
experiments = ['exp1','exp2','exp3']


# %% [markdown]
# ## Main functions to plot the trajectory for a single larva

# %%
def color_selector(arena,substrate,larva):
    """
    Select color based on substrate.
    """
    if substrate == 'Yeast':
        return 'tab:orange'
    elif substrate == 'Sucrose':
        return 'tab:green'
    elif substrate == 'Agar':
        return 'tab:blue'
    elif substrate == 'Apple_juice':
        return 'tab:pink'
    elif (arena == 'Nonnutrient') and (substrate == 'Agar'):
        return 'tab:gray'
    elif (arena == 'Nonnutrient') and (substrate == 'Gel'):
        return 'tab:olive'

def get_selection(data_all,arena,substrate,larva,exp,singlelarva):
    """
    Selects a specific trajectory in the dataframe `data_all`
    """
    if (arena,substrate,larva,exp,singlelarva) in data_all.index:
        return data_all.loc[arena,substrate,larva,exp,singlelarva]
    else:
        return None

def plot_one_trajectory(arena,substrate,larva,exp,singlelarva):
    """
    Plots the trajectory of the single larva specified in the arguments. 
    Returns None if the larva does not exist.
    
    Turning points are indicated by circles.
    """
    mydf = get_selection(data_all,arena,substrate,larva,exp,singlelarva)
    if mydf is None:
        return None
    col_box = color_selector(arena,substrate,larva) 
    fig = plt.figure(figsize=(10,10))
    xplot = mydf.x
    idxkeep = ~np.isnan(xplot)
    xplot=xplot[idxkeep]
    yplot = mydf.y[idxkeep]
    idx_turns = mydf.idx_turn_points
    xturns = mydf.x[idx_turns]
    yturns = mydf.y[idx_turns]
    ax = fig.add_subplot(1, 1, 1)
    ax.set_aspect(1)
    ax.set_xlim(0,275)
    ax.set_ylim(0,275)
    ax.plot(xplot,yplot,color='black',alpha=0.4) # plots full trajectory
    ax.scatter(xturns,yturns,marker='o',color=col_box) # plots turns
    ax.set_title(f'{arena} {substrate} {larva} {exp} {singlelarva}')
    if arena == 'Two':
        scale = 1 # number of pixels per mm
        patch_info =mydf.patch_info
        circle1 = plt.Circle((patch_info[0][0]/scale, patch_info[0][1]/scale), patch_info[0][2]/scale, color=col_box, alpha=0.2)
        circle2 = plt.Circle((patch_info[1][0]/scale, patch_info[1][1]/scale), patch_info[1][2]/scale, color=col_box, alpha=0.2)
        ax.add_patch(circle1)
        ax.add_patch(circle2)
    elif arena == 'Eight':
        scale = 1 # number of pixels per mm
        patch_info =mydf.patch_info
        for K in range(8):
            cirKle = plt.Circle((patch_info[K][0]/scale, patch_info[K][1]/scale), patch_info[K][2]/scale, color=col_box, alpha=0.2)
            ax.add_patch(cirKle)
        
    return fig



# %% [markdown]
# ## Interactive plot
# The script below generates an interactive menu that allows only to select the larvae that are included in the dataframe.

# %%

def get_possible_substrates(data_all,arena):
    df_are = data_all.loc[arena]
    return df_are.index.get_level_values(0).unique()

def get_possible_larvae(data_all,arena,substrate):
    df_sub = data_all.loc[arena,substrate]
    return df_sub.index.get_level_values(0).unique()

def get_possible_experiments(data_all,arena,substrate,larva):
    df_lar = data_all.loc[arena,substrate,larva]
    return df_lar.index.get_level_values(0).unique()

def get_possible_singlelarva(data_all,arena,substrate,larva,experiment):
    df_singlelarva = data_all.loc[arena,substrate,larva,experiment]
    return df_singlelarva.index.get_level_values(0).unique()

def set_menu_subs(change):
    menu_subs.options = get_possible_substrates(data_all,change['new'])
def set_menu_larvae(change):
    menu_larvae.options = get_possible_larvae(data_all,menu_are.value,change['new'])
def set_menu_exps(change):
    menu_exps.options = get_possible_experiments(data_all,menu_are.value,menu_subs.value,change['new'])
def set_menu_singlelarva(change):
    menu_singlelarva.options = get_possible_singlelarva(data_all,menu_are.value,menu_subs.value,menu_larvae.value,change['new']) 


menu_are = widgets.Dropdown(options=arenas)
menu_are.observe(set_menu_subs, names='value')

menu_subs = widgets.Dropdown(options=[])
menu_subs.observe(set_menu_larvae, names='value')

menu_larvae = widgets.Dropdown(options=[])
menu_larvae.observe(set_menu_exps, names='value')

menu_exps= widgets.Dropdown(options=[])
menu_exps.observe(set_menu_singlelarva, names='value')

menu_singlelarva= widgets.Dropdown(options=[])


allmenus = widgets.Box(children=[menu_are,menu_subs,menu_larvae,menu_exps,menu_singlelarva])


thesingleplot = widgets.interactive_output(plot_one_trajectory,{'arena':menu_are,'substrate':menu_subs,'larva':menu_larvae,'exp':menu_exps,'singlelarva':menu_singlelarva})

display(allmenus,thesingleplot)


# %%
# test a single larva, dataframe and plot
# dftest = get_selection(data_all,'Two','Yeast','Sitter','exp1','L1')
# plot_one_trajectory('Two','Yeast','Sitter','exp1','L1')

# %%
