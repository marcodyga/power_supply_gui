##########################################################
#                   PowerSupply GUI                      #
# developed by Marco Dyga as part of his Master's and    #
# PhD theses in the group of Prof. Lukas Gooßen, Chair   #
# of Organic Chemistry I, Ruhr-Universität Bochum.       #
##########################################################

from tkinter import *
from powersupplycontrol import powersupplyframe

# get configuration from config.txt
f = open("config.txt", "r")
config = {}
for this_line in f:
    no_comment = this_line.split("#")  # remove comments
    no_comment = no_comment.strip() # remove trailing and leading spaces
    if no_comment != "":
        stuff = no_comment[0].split(" ", 1)
        stuff[0] = stuff[0].strip()
        stuff[1] = stuff[1].strip()
        config[stuff[0]] = stuff[1]
f.close()

# Window building
root = Tk()
root.title("PowerSupply GUI")

psframes = []
# for i in range(int(config["npowersupplies"])):
    # psframes.append(powersupplyframe(root, i, config))
    # psframes[i].grid(row=i, column=0, padx=5, pady=5)

psframes.append(powersupplyframe(root, 0, config))
psframes[0].grid(row=0, column=0, padx=5, pady=5)
psframes.append(powersupplyframe(root, 1, config))
psframes[1].grid(row=1, column=0, padx=5, pady=5)
psframes.append(powersupplyframe(root, 2, config))
psframes[2].grid(row=2, column=0, padx=5, pady=5)
psframes.append(powersupplyframe(root, 3, config))
psframes[3].grid(row=2, column=1, padx=5, pady=5)



mainloop()

