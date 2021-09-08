# Plotting Hardware Measurements

This section of the repository enables you generate various plots to
visualize hardware characteristics as used for the LaserShark attacks.

## Dependencies

All dependencies will be installed (hopefully) automagically when
executing the main plotting scripts, which however makes use of

- git
- python3
- pip
- python3-env

To install these on a Debian-based system, please run:

```bash
sudo apt install python3 python3-pip python3-venv
```

Additional dependencies (cf. `requirements.txt`) will installed
on-the-fly.

## Run the Scripts

We provide a bash script that generates all plots and additionally sets
symbolics links to identify figures used in the ACSAC 2021 paper. Please
run:

```bash
bash measurements/bin/plot.sh
```

The plots will be written to `measurements/out/`.

