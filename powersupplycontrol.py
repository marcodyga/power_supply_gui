import powersupply
import time
import getpass
import os
import sys
from tkinter import *
from functools import partial

try:
    # I am not allowed to upload tooltip.py to this repository, as CC-BY-SA 3.0 licence (StackOverflow.com) 
    # is incompatible with any "normal" open-source licence, be it MIT licence or even GPLv3.
    # 
    # So if you want the tooltip, get the code from Alberto Vassena under the following URL:
    # https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter/41079350#41079350
    # Copy it into a file called tooltip.py, and add it to the folder in which this file is located.
    # Then it should work normally...
    # Otherwise, you will not see a warning tooltip, why the sample name turns red sometimes.
    import tooltip
except ImportError:
    pass

class powersupplyframe(Frame):
    
    def __init__(self, root, number, config):
        super().__init__(root, borderwidth=3, relief=GROOVE)
        self.root = root
        self.noutputs = 4
        self.rows = []
        self.cols = ['#', 'U', 'I', 't', 'Sample Name', '', '']
        self.time_remaining = [0] * self.noutputs
        self.ps = powersupply.PowerSupply()
        self.number = number
        self.config = config
        self.targetTimes = [0] * self.noutputs
        self.startTimes = [0] * self.noutputs
        # unit conversion setup
        voltage_unit = StringVar(self)
        voltage_unit.set(config["voltunit"])
        voltage_units = {"V": 1.0, "mV": 0.001}
        current_unit = StringVar(self)
        current_unit.set(config["currunit"])
        current_units = {"A": 1.0, "mA": 0.001, "µA": 0.000001}
        time_unit    = StringVar(self)
        time_unit.set(config["timeunit"])
        time_units    = {"h": 60.0, "min": 1.0, "s": 1.0/60}
        self.units = {self.cols[1][0]: voltage_units, self.cols[2][0]: current_units, self.cols[3][0]: time_units}
        self.unitvars = {self.cols[1][0]: voltage_unit, self.cols[2][0]: current_unit, self.cols[3][0]: time_unit}
        self.units_optionMenus = {}
        # this list is necessary, if we want to recalculate the values in the entries after the unit has changed.
        self.currently_used_units = [voltage_unit.get(), current_unit.get(), time_unit.get()] 
        
        self.build()
    
    def build(self):
        # Table crown
        self.tcrown = Frame(self)
        # Connection status indicator
        self.numberLabel = Frame(self.tcrown)
        nl1 = Label(self.numberLabel, text="PowerSupply #")
        nl1.grid(row=0, column=0, sticky=E)
        nl2 = Label(self.numberLabel, text=str(self.number), font="Helvetica 12 bold")
        nl2.grid(row=0, column=1, sticky=W)
        self.numberLabel.grid(row=0, column=0, sticky=W)
        self.connectionFrame = Frame(self.tcrown)
        self.statusIndicator = Label(self.connectionFrame, text="\u2717 Not connected", bg="red", fg="white")
        self.statusIndicator.grid(row=0, column=0)
        self.connButton = Button(self.connectionFrame, text="Connect", command=self.PSConnect)
        self.connButton.grid(row=0, column=1)
        self.disconnButton = Button(self.connectionFrame, text="Disconnect", command=self.PSDisconnect)
        self.disconnButton.grid(row=0, column=2)
        self.connectionFrame.grid(row=0, column=1, sticky=E)
        # place the tcrown
        self.tcrown.grid(row=0, column=0, columnspan=len(self.cols), sticky=N+E+S+W)
        self.tcrown.grid_columnconfigure(1, weight=1)
        
        # Table
        self.table = Frame(self)
        
        # Table head
        self.thead_frames = []
        this_row = []
        for ic, col in enumerate(self.cols):
            self.thead_frames.append(Frame(self.table))
            this_row.append(Label(self.thead_frames[ic], text=col).grid(row=0, column=0))
            if col == 'U' or col == "I" or col == "t":
                self.units_optionMenus[col[0]] = OptionMenu(self.thead_frames[ic], self.unitvars[col[0]], *self.units[col[0]].keys(), command=lambda _: self.refresh_unit_conversion())
                self.units_optionMenus[col[0]].grid(row=0, column=1)
            self.thead_frames[ic].grid(row=0, column=ic)
        self.rows.append(this_row)
            
        # Table body
        for output in range(1, self.noutputs+1):
            row = output
            this_row = []
            for ic, col in enumerate(self.cols):
                if ic == 0:
                    this_row.append(Label(self.table, text=output))
                elif ic > 0 and ic <= 3:
                    this_row.append(Entry(self.table, width=12))
                elif ic == 4:
                    vcmd = self.register(self.check_sample_name)
                    this_row.append(Entry(self.table, width=25, validate='key', validatecommand=(vcmd, "%P", "%W")))
                elif ic == 5:
                    this_row.append(Button(self.table, text="Start", command=partial(self.startPowerSupply, output)))
                elif ic == 6:
                    this_row.append(Button(self.table, text="Stop", command=partial(self.stopPowerSupply, output, False)))
            for ic, obj in enumerate(this_row):
                obj.grid(row=row, column=ic)
            self.rows.append(this_row)

        # one row for changing the values of all text fields.
        self.all_row = []
        for ic, col in enumerate(self.cols):
            if ic == 0:
                self.all_row.append(Label(self.table, text="ALL"))
            elif ic > 0 and ic <= 3:
                vcmd = self.register(self.write_to_all)
                self.all_row.append(Entry(self.table, width=12, validate='key', validatecommand=(vcmd, ic, "%P")))
            elif ic == 4:
                vcmd = self.register(self.write_to_all)
                self.all_row.append(Entry(self.table, width=25, validate='key', validatecommand=(vcmd, ic, "%P")))
        for ic, obj in enumerate(self.all_row):
            obj.grid(row=len(self.rows), column=ic, pady=3, sticky=S)
        
        # place the Table
        self.table.grid(row=1, column=0)
        
        # Bottom row: Buttons for Start all, stop all and clear.
        self.bottomrow = Frame(self)
        self.start_all_button = Button(self.bottomrow, text="Start all", command=self.start_all)
        self.start_all_button.grid(row=0, column=0)
        self.stop_all_button = Button(self.bottomrow, text="Stop all", command=self.stop_all)
        self.stop_all_button.grid(row=0, column=1)
        self.clear_table_button = Button(self.bottomrow, text="Clear table", command=self.clear_table)
        self.clear_table_button.grid(row=0, column=2)
        self.bottomrow.grid(row=2, column=0)
        
        # enter default values from config
        self.clear_table()
        
        # lock buttons until PS is connected
        self.lock_buttons()
        
    def PSConnect(self):
        port = self.config["port"+str(self.number)]
        success = self.ps.connect(port)
        if success: 
            print("Connected successfully.")
            self.statusIndicator["bg"] = "green"
            self.statusIndicator["text"] = "\u2713 Connected"
            self.unlock_buttons()
            # check if swapfiles are present and restart the runs if necessary...
            for channel in range(1, self.noutputs+1):
                swap_fname = self.get_swap_filename(channel)
                if os.path.isfile(swap_fname):
                    # uh oh, need to restart
                    f = open(swap_fname, "r")
                    old_starttime = float(f.readline()) # unix timestamp
                    old_targettime_min = float(f.readline()) # in minutes
                    old_targettime_sec = old_targettime_min * 60
                    endtime = old_starttime + old_targettime_sec
                    new_targettime_sec = endtime - time.time()
                    if new_targettime_sec <= 0:
                        # it already should have turned itself off
                        self.ps.powerOff(channel)
                    else:
                        old_voltage = f.readline()
                        old_current = f.readline()
                        old_samplename = f.readline()
                        new_targettime_min = new_targettime_sec / 60
                        voltage, current, time_input = self.get_display_values(old_voltage.strip(), old_current.strip(), new_targettime_min)
                        self.writeToEntry(self.rows[channel][1], voltage) # voltage
                        self.writeToEntry(self.rows[channel][2], current) # current
                        self.writeToEntry(self.rows[channel][3], time_input) # time
                        self.writeToEntry(self.rows[channel][4], old_samplename.strip() + "_restored") # sample name
                        self.startPowerSupply(channel)
        return

    def PSDisconnect(self):
        self.stop_all()
        self.lock_buttons()
        self.ps.disconnect()
        self.statusIndicator["bg"] = "red"
        self.statusIndicator["text"] = "\u2717 Not connected"
        return
        
    def unlock_buttons(self):
        self.start_all_button["state"] = NORMAL
        self.stop_all_button["state"] = NORMAL
        for row in self.rows:
            if row[5] != None and row[6] != None:
                row[5]["state"] = NORMAL
                row[6]["state"] = NORMAL
        
    def lock_buttons(self):
        self.start_all_button["state"] = DISABLED
        self.stop_all_button["state"] = DISABLED
        for row in self.rows:
            if row[5] != None and row[6] != None:
                row[5]["state"] = DISABLED
                row[6]["state"] = DISABLED
        
    def writeToEntry(self, entry, text):
        readonly = False
        if entry["state"] == 'readonly':
            readonly = True
            entry.configure(state="normal")
        entry.delete(0, END)
        entry.insert(0, text)
        if readonly:
            entry.configure(state="readonly")
        return

    def startPowerSupply(self, output):
        if self.time_remaining[output-1] <= 0:
            # get values from entries and do the unit conversion to standard units (V, A, min)
            voltage, current, time_input = self.get_standard_values(output)
            samplename = self.rows[output][4].get().strip()
            # write to power supply
            self.ps.writeVoltage(voltage, output)
            self.ps.writeCurrent(current, output)
            if not os.path.exists(self.config["path"+str(self.number)]):
                os.makedirs(self.config["path"+str(self.number)])
            # check if file already exists
            fname = self.config["path"+str(self.number)] + "/" + str(samplename) + ".ely"
            time_from_last_run = 0.0
            if os.path.isfile(fname):
                # if it exists, then get the last time value and continue from there.
                f = open(fname, "r")
                while True:
                    line = f.readline().split(" ")
                    if line != [""]:
                        lastline = line
                    else:
                        break
                try:
                    time_from_last_run = float(lastline[0])
                except ValueError:
                    time_from_last_run = 0.0
                f.close()
            # write Header into file
            f = open(fname, "a")
            f.write("# Date: " + time.strftime("%d.%m.%Y %H:%M:%S") + "\n")
            f.write("# Operator: " + getpass.getuser() + "\n")
            f.write("# Device Name: " + self.ps.readDeviceName() + "\n")
            f.write("# Device Number: " + str(self.number) + "\n")
            f.write("# Target Voltage: " + voltage + " V\n")
            f.write("# Target Current: " + current + " A\n")
            f.write("# Target time "+str(time_input)+" min\n")
            f.write("#%8s %9s %9s\n" % ("t [min]", "U [V]", "I [A]"))
            f.close()
            # make the Entries read-only
            self.rows[output][1].configure(state='readonly') # voltage
            self.rows[output][2].configure(state='readonly') # current
            self.rows[output][4].configure(state='readonly') # sample name
            # create "swap-file" for restoring in case of crash
            f = open(self.get_swap_filename(output),"w")
            f.write(str(time.time()) + "\n")
            f.write(str(time_input) + "\n")
            f.write(str(voltage) + "\n")
            f.write(str(current) + "\n")
            f.write(samplename + "\n")
            # start run
            print("Powering on", output)
            self.targetTimes[output-1] = float(time_input) + time_from_last_run # minutes
            self.startTimes[output-1] = time.time() # unix timestamp
            print("Target voltage "+str(voltage)+" V")
            print("Target current "+str(current)+" A")
            print("Target time "+str(time_input)+" min")
            self.ps.powerOn(output)
            self.time_remaining[output-1] = int(float(time_input) * 60000)
            self.run(output)
        self.clear_table_button["state"] = "disabled"
        return
        
    def stopPowerSupply(self, output, reset_time = True):
        if reset_time: self.targetTimes[output-1] = 0
        self.end_run(output)
        return
    
    def start_all(self):
        for output in range(1, self.noutputs+1):
            self.startPowerSupply(output)
    
    def stop_all(self):
        for output in range(1, self.noutputs+1):
            self.stopPowerSupply(output)
    
    def clear_table(self):
        # enter default values from config
        self.write_to_all(self.cols.index("U"), self.config["defvolt"]) # Voltage
        self.write_to_all(self.cols.index("I"), self.config["defvolt"]) # Current
        # clear sample name and time
        self.write_to_all(self.cols.index("t"), "")
        self.write_to_all(self.cols.index("Sample Name"), "")
        # all_row
        self.writeToEntry(self.all_row[self.cols.index("U")], self.config["defvolt"])
        self.writeToEntry(self.all_row[self.cols.index("I")], self.config["defcurr"])
        self.writeToEntry(self.all_row[self.cols.index("t")], "")
        self.writeToEntry(self.all_row[self.cols.index("Sample Name")], "")
        return
    
    def writeCurrentValues(self):
        for output in range(1, self.noutputs+1):
            voltage = self.ps.readTargetVoltage(output)
            self.writeToEntry(self.rows[output][1], voltage)
            print("Output", output, "Voltage", voltage)
            current = self.ps.readTargetCurrent(output)
            self.writeToEntry(self.rows[output][2], current)
            print("Output", output, "Current", current)
            time = round(self.time_remaining[output-1] / 60000.0, 2)
            self.writeToEntry(self.rows[output][3], time)
        return

    def run(self, channel):
        ''' Controls measurement '''
        delay = 1000   # time in milliseconds after which this function calls itself
        # check if the time is over
        #print(self.time_remaining[channel-1])
        # define remaining time precisely from start time and target time
        self.time_remaining[channel-1] = self.targetTimes[channel-1] * 60000.0 - (time.time() - self.startTimes[channel-1]) * 1000.0
        time_input_unit = self.unitvars[self.cols[3][0]]
        remaining_mins = self.time_remaining[channel-1] / 60000.0
        if self.time_remaining[channel-1] > 0:
            self.after(delay, self.run, channel)
            # get data
            rem_time = self.targetTimes[channel-1] - remaining_mins
            voltage = self.ps.readVoltage(channel)
            current = self.ps.readCurrent(channel)
            samplename = self.rows[channel][4].get().strip()
            if samplename == "":
                samplename = "out"+str(channel)
            # write it into file
            f = open(self.config["path"+str(self.number)] + "/" + str(samplename) + ".ely", "a")
            f.write("%5.3f %3.5f %3.5f\n" % (rem_time, voltage, current))
            f.close()
            # Refresh the text box
            self.writeToEntry(self.rows[channel][3], round(remaining_mins / self.units[self.cols[3][0]][time_input_unit.get()], 2))
            # if maximum voltage is reached, turn off the power supply
            if float(voltage) > float(self.config["maxvolt"]):
                self.time_remaining[channel-1] = 0
                self.end_run(channel)
        else:
            samplename = self.rows[channel][4].get().strip()
            f = open(self.config["path"+str(self.number)] + "/" + str(samplename) + ".ely", "a")
            f.write("# Run ended at " + time.strftime("%d.%m.%Y %H:%M:%S") + "\n")
            f.close()
            self.end_run(channel)
            self.writeToEntry(self.rows[channel][3], 0.0)
            if self.time_remaining == [0] * self.noutputs:
                self.clear_table_button["state"] = "normal"
        return
    
    def end_run(self, channel):
        self.ps.powerOff(channel)
        # Reset the read-only state of the entries to normal
        self.rows[channel][1].configure(state='normal') # voltage
        self.rows[channel][2].configure(state='normal') # current
        self.rows[channel][4].configure(state='normal') # sample name
        self.targetTimes[channel-1] = 0
        # remove swap-file
        if self.ps.ser != False:
            if os.path.isfile(self.get_swap_filename(channel)):
                os.remove(self.get_swap_filename(channel))
        return
        
    def refresh_unit_conversion(self):
        ''' recalculates units on all entries which use them '''
        # get the units in the table head
        voltage_unit = self.unitvars[self.cols[1][0]].get()
        current_unit = self.unitvars[self.cols[2][0]].get()
        time_input_unit = self.unitvars[self.cols[3][0]].get()
        for output in range(1, self.noutputs+1):
            # convert the values first into the standard units
            # then write the values into the entries
            voltage, current, time_input = self.get_standard_values(output)
            # convert it now into the units in the table head
            try:
                voltage = float(voltage) / self.units[self.cols[1][0]][voltage_unit]
                voltage = round(voltage, 5)
                if voltage.is_integer():
                    voltage = int(voltage)
                self.writeToEntry(self.rows[output][1], voltage)
            except ValueError:
                pass
            try:
                current = float(current) / self.units[self.cols[2][0]][current_unit]
                current = round(current, 5)
                if current.is_integer():
                    current = int(current)
                self.writeToEntry(self.rows[output][2], current)
            except ValueError:
                pass
            try:
                time_input = float(time_input) / self.units[self.cols[3][0]][time_input_unit]
                time_input = round(time_input, 5)
                if time_input.is_integer():
                    time_input = int(time_input)
                self.writeToEntry(self.rows[output][3], time_input)
            except ValueError:
                pass
        # now overwrite the currently used units
        self.currently_used_units = [voltage_unit, current_unit, time_input_unit]
        return
    
    def get_standard_values(self, output):
        ''' gets the values from the Voltage, Current and Time entries, and calculates them into standard
            units (V, A and min) '''
        voltage = self.rows[output][1].get()
        voltage = voltage.replace(',','.')
        if voltage == "":
            voltage = "0"
        if voltage != "max":
            voltage_unit = self.currently_used_units[0]
            voltage = str(float(voltage) * self.units[self.cols[1][0]][voltage_unit]) # convert to Volts
        current = self.rows[output][2].get()
        current = current.replace(',','.')
        if current == "":
            current = "0"
        current_unit = self.currently_used_units[1]
        current = str(float(current) * self.units[self.cols[2][0]][current_unit]) # convert to Amperes
        time_input = self.rows[output][3].get()
        time_input = time_input.replace(',','.')
        if time_input == "":
            time_input = "0"
        time_input_unit = self.currently_used_units[2]
        time_input = str(float(time_input) * self.units[self.cols[3][0]][time_input_unit]) # convert to minutes
        return voltage, current, time_input
        
    def get_display_values(self, voltage, current, time_input):
        ''' takes values for voltage, current and time in standard units (V, A, and min), and converts
            them into the units currently set at the display units '''
        if voltage != "max":
            voltage_unit = self.currently_used_units[0]
            voltage = str(float(voltage) / self.units[self.cols[1][0]][voltage_unit]) # convert from Volts
        current_unit = self.currently_used_units[1]
        current = str(float(current) / self.units[self.cols[2][0]][current_unit]) # convert from Amperes
        time_input_unit = self.currently_used_units[2]
        time_input = str(float(time_input) / self.units[self.cols[3][0]][time_input_unit]) # convert from minutes
        return voltage, current, time_input
        
    def check_sample_name(self, samplename, widgetname):
        fname = self.config["path"+str(self.number)] + "/" + str(samplename) + ".ely"
        entry = self.root.nametowidget(widgetname)
        if samplename != "" and os.path.isfile(fname):
            # if it exists, then give the entry a red border.
            entry.configure(bg="#ffb5b5")
            if "tooltip" in sys.modules:
                if hasattr(entry, "tooltip"):
                    entry.tooltip.bind()
                else:
                    entry.tooltip = tooltip.Tooltip(entry, text="This sample name already exists. Data will be appended to file " + samplename + ".ely.", waittime=0)
        else:
            entry.configure(bg="#ffffff")
            if hasattr(entry, "tooltip"):
                entry.tooltip.unbind()
        return True
        
    def get_swap_filename(self, channel):
        return str(self.number) + "-" + str(channel) + ".RUNNING"
        
    def write_to_all(self, ic, text):
        ic = int(ic)
        for output in range(1, self.noutputs+1):
            if self.time_remaining[output-1] <= 0:
                entry = self.rows[output][ic]
                self.writeToEntry(entry, text)
        return True
    
    
    
