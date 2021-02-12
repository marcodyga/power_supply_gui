# PowerSupply GUI

## Introduction

This software allows to use the HMP4040 laboratory power supply by Rohde&Schwarz / HAMEG for electrochemical reactions.

The software turns on the power supply with the given settings for current and voltage, and automatically turns it off after the given time has passed.

It also logs current and voltage values, which can then later be imported e.g. into an electronic lab notebook (Sciformation ELN).

## Third-party software

This software is written in [Python 3](http://python.org), and intended to run on Windows.

The pyserial library is required, it can be installed using pip:

```
pip install pyserial
```

To access the HMP4040 power supplies, you also need the [HO720/HO730 USB Virtual COM Port Driver](https://www.rohde-schwarz.com/de/treiber/hmp/). After installing the driver, follow the instructions provided by Rohde&Schwarz to enable the **Virtual COM Port**. 

*Optional:* The tooltip function, which is used to explain to the user why the text field for the name turns red, was taken from StackOverflow.com. Unfortunately, it is therefore licensed under CC-BY-SA 3.0, which is incompatible with my GitHub repository. So, optionally, you can copy the code from Alberto Vassena under the following URL into a file called "tooltip.py" and add it to the folder in which this file is located:

[https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter/41079350#41079350]

## How to use

You will first need to configure the software in *config.txt*. Most importantly, the "ports" must be set.

The ports are defined by the HMP4040 driver - you can look up the port numbers (something like COM5) in the Device Manager under "Ports (COM & LPT)". If you have correctly installed the Virtual COM Port, you should see the "HO720 Virtual COM Ports", and the corresponding port numbers should be written there. Enter these numbers into the *config.txt*.

You should also define the number and layout of the power supplies, by changing the parameter *npowersupplies* in *config.txt*, and modifying the layout in *gui.py* according to your needs.

To start the software, simply run *gui.py*.