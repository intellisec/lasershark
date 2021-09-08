# Author: Maximilian Noppel
# Date: April 2021


import os

import pandas as pd


dat = pd.read_csv(f"results/parseResult.csv",index_col=[0])

print(f"We found {len(dat.groupby('dtsfile'))} individual boards.")

datParsed = dat[dat["parsing"] == 1]
print(f"We found {len(datParsed.groupby('dtsfile'))} individual parsable boards.")

datParsedWithAtLeastOneLEDs = datParsed[datParsed["mode"].notnull()]
print(f"We found {len(datParsedWithAtLeastOneLEDs.groupby('dtsfile'))} individual parsable boards with at least one LED.")


datActiveHigh = dat[dat["mode"] == "ACTIVE_HIGH"]
datActiveLow = dat[dat["mode"] == "ACTIVE_LOW"]
datUnknownGPIO = dat[dat["mode"] == "UNKNOWN_gpio"]
datUnknownPCA955x = dat[dat["mode"] == "UNKNOWN_pca955x"]
datUnknownPCA9532 = dat[dat["mode"] == "UNKNOWN_pca9532"]
datUnknownPWM = dat[dat["mode"] == "UNKNOWN_pwm"]
print(f"We found {len(datActiveHigh)} individual ACTIVE_HIGH LEDs.")
print(f"We found {len(datActiveLow)} individual ACTIVE_LOW LEDs.")
print(f"We found {len(datUnknownGPIO)} individual UNKNOWN_gpio LEDs.")
print(f"We found {len(datUnknownPCA955x)} individual UNKNOWN_pca955x LEDs.")
print(f"We found {len(datUnknownPCA9532)} individual UNKNOWN_pca9532 LEDs.")
print(f"We found {len(datUnknownPWM)} individual UNKNOWN_pwm LEDs.")


datActiveHighBoards = datActiveHigh.groupby("dtsfile")
datActiveLowBoards = datActiveLow.groupby("dtsfile")
print(f"We found {len(datActiveHighBoards)} individual parsable boards with at least one ACTIVE_HIGH LED.")
print(f"We found {len(datActiveLowBoards)} individual parsable boards with at least one ACTIVE_LOW LED.")

