
# Adaptation of Drosophila larva foraging in response to changes in food resources

**Data and code for the paper :**
> Wosniack et al. eLife 2022;11:e75826. DOI: https://doi.org/10.7554/eLife.75826

The code has been tested on a Linux system using conda 22.11 and Python 3.9

## Setup of Python environment

It is reccomended to use `conda` to initialize a new environment based on the `env-wosniac22.yml` file included.

```bash
conda env create --name wosniack22 --file env-wosniack22.yml
```

Please use VsCode or Jupyter lab to best visualize the code.

## Download data

Data has been uploaded on Zenodo:  [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7438188.svg)](https://doi.org/10.5281/zenodo.7438188).

You can ether dowload it from the link provided, and copy it in the `Data` folder, or run the script `initialize_data.py`.

## Preprocessing of data

To speed up subsequent scripts, the first step is to read and pre-preocess the data, saving it in a single pandas dataframe. To do so, please run the `preprocess_data.py` script.

### Data structure

Each dataframe row corresponds to one larva recorded in a sesion. Comlums are:

+ **x** :  the x coordinates of the larva trajectory, sampled every 0.5 seconds
+ **y** :  the y coordinates of the larva trajectory, sampled every 0.5 seconds
+ **nframes** : total number of frames, corrisponding to a 50 min recording time
+ **time** : time vector in seconds. Corresponds to `(0:nframes)*0.5`
+ **simple_trajectory**: array of (x,y) coordinates of trajectory, after the RDP algorithm is applied
+ **idx_turn_points**: `<TO-DO>`
+ **rdp_mask**: binary mask that indicates which x and y elements have been selected by the RDP algorithm.
+ **rdp_epsilon**: the epsilon value used in the RDP algorithm
+ **patch_info**: if two patches are present, it containes the patch cetenrs and their size.

## Visualize paths of single larvae

The notebook in `plot_single_path.ipynb` reads the preprocessed data and allows to select and visualize any path in the dataset.
