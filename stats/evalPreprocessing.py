
# Author: Maximilian Noppel
# Date: April 2021


#%%

import pandas as pd

dat = pd.read_csv("results/preprocessingResult.csv",header=None)
print(f"-----------------------------------------------------")
print(f"EVALUATION OF PREPROCESSING PHASE:")
print(f"-----------------------------------------------------")
print(f"Found {len(dat)} dts files")
print(f"Successfully preprocessed {len(dat[dat[1]==0])}. {len(dat[dat[1]==0])/len(dat)*100:.0f}%")
print(f"Preprocessing failed of {len(dat[dat[1]!=0])} files.")
print(f"-----------------------------------------------------")