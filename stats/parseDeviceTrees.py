# Python script to parse the device tree files
# Author: Maximilian Noppel
# Date: April 2021

import sys
import os
import re
import subprocess

import pandas as pd
from pydevicetree import Devicetree

from joblib import Parallel, delayed

from drivers.leds_gpio import leds_gpio
from drivers.leds_pca955x import leds_pca955x
from drivers.leds_pca9532 import leds_pca9532
from drivers.leds_pwm import leds_pwm



outputfile = f"results/parseResult.csv"


class ParserError(Exception):
    def __init__(self,eStr=None):
        self.eStr = eStr
        pass

class PreprocessingError(Exception):
    def __init__(self,eStr=None):
        self.eStr = eStr
        pass


def evaluateDT(testfile):
    # There are some undocumented keywords in dts
    # In the following I remove em from the file
    # before passing it to the pydevicetree lib
    # See https://elinux.org/Device_Tree_Source_Undocumented


    try:
        with open(testfile,"r") as f:
            s = f.read()
            f.close()

        s = re.sub(r'.*/omit-if-no-ref/.*;','',s)
        s = re.sub(r'/omit-if-no-ref/', '', s)

        s = re.sub(r'.*/bits/.*;', '', s)

        # s = re.sub(r'.*/delete-node/.*;', '', s)
        # s = re.sub(r'.*/delete-property/.*;', '', s)

        with open(testfile,"w") as f:
            f.write(s)
            f.close()
    except Exception as e:
        print("Warn: Cleaning of dts file failed:",e)

    try:
        tree = Devicetree.parseFile(testfile)
    except Exception as e:
        print(testfile,e)
        # Parsing failed!
        return None

    return leds_gpio(tree,testfile), leds_pca955x(tree,testfile), leds_pca9532(tree,testfile), leds_pwm(tree,testfile)

def generateRows(line,leds,driver):
    rows = []

    if leds is None:
        return rows
    if len(leds) == 0:
        return rows

    print(f"{driver}: FOUND {len(leds)} LEDS")
    for led in leds:
        rows.append({
            "dtsfile": line.replace("_processed.dts",""),
            "parsing": 1,
            "driver":driver,
            "label": led["label"], # see Documentation/devicetree/bindings/leds/common.txt
            "mode": led["mode"], # only valid for leds-gpio, leds-pwm
            "trigger":led["trigger"], # see Documentation/devicetree/bindings/leds/common.txt
            "color":led["color"], # see Documentation/devicetree/bindings/leds/common.txt
            "function":led["function"] # see Documentation/devicetree/bindings/leds/common.txt
        })

    return rows

def handleLine(line,wd):
    line = line.strip()
    if len(line) == 0:
        return []

    result = []

    #print(f"Parsing {line}")
    basename = os.path.basename(line)
    dirname = os.path.dirname(line)

    os.chdir(dirname)
    evaluationResult = evaluateDT(basename)
    os.chdir(wd)

    if evaluationResult is None:
        #print(f"PARSERERROR")
        result.append({
            "dtsfile": line.replace("_processed.dts",""),
            "parsing": 0
        })
    else:
        (gpio, pca955x, pca9532, pwm) = evaluationResult
        #print("EvalResult: ",evaluationResult)
        gpioIsNoneOrEmpty = gpio is None or len(gpio) == 0
        pca955xIsNoneOrEmpty = pca955x is None or len(pca955x) == 0
        pca9532IsNoneOrEmpty = pca9532 is None or len(pca9532) == 0
        pwmIsNoneOrEmpty = pwm is None or len(pwm) == 0

        if gpioIsNoneOrEmpty and pca955xIsNoneOrEmpty and pca9532IsNoneOrEmpty and pwmIsNoneOrEmpty:
            #print(f"NO LED FOUND AT ALL")
            result.append({
                "dtsfile": line.replace("_processed.dts",""),
                "parsing": 1
            })
        else:
            r = generateRows(line, gpio, "leds-gpio   ")
            if not r is None:
                result.extend(r)
            r = generateRows(line, pca955x, "leds-pca955x")
            if not r is None:
                result.extend(r)
            r = generateRows(line, pca9532, "leds-pca9532")
            if not r is None:
                result.extend(r)
            r = generateRows(line, pwm, "leds-pwm    ")
            if not r is None:
                result.extend(r)

    return result

def main():

    with open(f"results/listProcessedDTS.txt") as f:
        home = os.getcwd()
        os.chdir("linux")
        wd = os.getcwd()
        lines = f.readlines()
        results = Parallel(n_jobs=8,verbose=True)(delayed(handleLine)(line,wd) for line in lines)
        f.close()
    os.chdir(home)

    r = []
    for res in results:
        r.extend(res)

    pd.DataFrame(r).to_csv(outputfile)


if __name__ == "__main__":
    main()