# LaserShark: Establishing Fast, Bidirectional Communication into Air-Gapped Systems

Physical isolation, so called air-gapping, is an effective method
for protecting security-critical computers and networks. While it
might be possible to introduce malicious code through the supply
chain, insider attacks, or social engineering, communicating with
the outside world is prevented. Different approaches to breach this
essential line of defense have been developed based on electro-
magnetic, acoustic, and optical communication channels. However,
all of these approaches are limited in either data rate or distance,
and frequently offer only exfiltration of data. We present a novel
approach to infiltrate data to air-gapped systems without any additional
hardware on-site. By aiming lasers at already built-in LEDs
and recording their response, we are the first to enable a
long-distance (25 m), bidirectional, and fast (18.2 kbps in & 100 kbps out)
covert communication channel. The approach can be used against
any office device that operates LEDs at the CPU’s GPIO interface.

# Overview of Covert Channels

The following table summarizes related approaches and puts the
effectivity of the LaserShark attack in perspective. 

<img src="https://intellisec.org/research/lasershark/cc-overview.svg" width="900">

For further details please consult the
[conference publication](https://intellisec.org/research/lasershark/2021-acsac.pdf).

# Code

This repository contains all code used during the experiments, raw data
of the hardware measurements, and scripts to plot them. Since
reproducing the results is dependent on a specific setup of attacker
and target devices, we provide a simplified experiment based on a
Raspberry Pi, an Arduino, and an ordinary laser pointer instead.

Without any hardware on-site, it is still possible to build the required
kernel modules, plot measurements, and determine the hardware statistics
presented in the paper.

* [Plot hardware measurements](measurements/README.md)
* [Determine device statistics](stats/README.md)
* [Build device images](docs/build.md) (Hardware needed eventually)
* [Simple demo setup](docs/quickstart.md) (Hardware needed)


# Publication
A detailed description of our work will been presented at the
37th Annual Computer Security Applications Conference (ACSAC 2021)
in December 2021. If you would like to cite our work, please use the
reference as provided below:

```
@inproceedings{KuePreNopSchRieWre21,
  author =    {Niclas Kühnapfel and Stefan Preußler and
               Maximilian Noppel and Thomas Schneider and
               Konrad Rieck and Christian Wressnegger},
  title =     {LaserShark: Establishing Fast, Bidirectional
               Communication into Air-Gapped Systems},
  booktitle = {Proc. of 37th Annual Computer Security
               Applications Conference (ACSAC)},
  year =      2021,
  month =     dec
}
```

A preprint of the paper is available [here](https://intellisec.org/research/lasershark/2021-acsac.pdf).
