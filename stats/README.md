# Lasershark: Linux Kernel Evaluation on DeviceTree Files

The goal of this part is to evaluate how many of the registered boards in the linux kernel might be vulnerable for the Lasersharks attack. Therefore we `git clone` the linux kernel and evaluate every contained `.dts` file to see if we find LEDs connected to the GPIO ports. In order to execute this evaluation you need `git`, `gcc` and `python` including the `venv` module to be installed. Please, also make sure that you have at least 16GB of RAM and 32GB of disk space available.


## Run all
If you want to run phases at once just execute
```bash
bash run.sh
```

Otherwise run the individual phases one after the other as follows:

## Preprocessing Phase
As `.dts` use C++ preprocessor inlcudes and macros we first need to preprocess them with a C++ preprocessor. Use the `preprocess.sh` script therefore. In the first run this clones the linux kernel repository. This might take a while. Once the repo is cloned, it runs every `.dts` in the linux kernel through the C++ preprocessor to resolve the includes and macros. Every preprocessed file is stored as `_processed.dts` files. Also a list of all files is saved in the `results` folder.

Execute
```bash
bash preprocess.sh
```
in this repository's directory.


### Evaluation
In the next step we evaluate the preprocessing. Run

```bash
bash evalPreprocessing.sh
```
in the repository's directory. This should provide you with an output similar to 

```
-----------------------------------------------------
EVALUATION OF PREPROCESSING PHASE:
-----------------------------------------------------
Found 2279 dts files
Successfully preprocessed 2200. 97%
Preprocessing failed of 79 files.
-----------------------------------------------------
```

Note that this script sets up a python virtual environment.

## Parsing Phase
In the next phase we parse the preprocessed `.dts` files and generate a `csv` file with one row for each found LED and at least one row for each board, even if not LED was found. Note that only the device tree for the GPIO, PCA955x, PCA9532 and PWM drivers are implemented. Most of the other LED IC-drivers are not accessable as inputs and could therefore not be used for our attack. LEDs connected via such a output-only driver are not recognized by our program therefore. Run

```bash
bash parse.sh
```

in the repository's directory.

This will parse all the preprocessed `.dts` files and generate a `.csv` which lists all the found LEDs. Note that even if this step is parallized, it might take a while.

## Final Evaluation
For the final evaluation run

```bash
bash evaluating.sh
```

This results in the following output

```
We found 2183 individual boards.
We found 933 individual parsable boards.
We found 422 individual parsable boards with at least one LED.
We found 45 individual ACTIVE_HIGH LEDs.
We found 6 individual ACTIVE_LOW LEDs.
We found 1173 individual UNKNOWN_gpio LEDs.
We found 0 individual UNKNOWN_pca955x LEDs.
We found 0 individual UNKNOWN_pca9532 LEDs.
We found 0 individual UNKNOWN_pwm LEDs.
We found 18 individual parsable boards with at least one ACTIVE_HIGH LED.
We found 6 individual parsable boards with at least one ACTIVE_LOW LED.
```

We find that 45% of the boards in the device tree (422 out of 933) have at least one LED registered at a GPIO port and are thus potentially vulnerable. In practice, however, the exact number of devices is difficult to determine as the LEDs might, for instance, not be visible from the outside. Also, our analysis cannot make a statement on the piece numbers of the boards and products.
