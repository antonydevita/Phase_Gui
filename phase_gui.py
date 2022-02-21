"""
phase_gui.py

Description: Phase analysis Python GUI
Author:      Antony Devita
Created:     March 18, 2021
Copyright:   (C) KCF Technologies, 2021
License:     Property of KCF Technologies, not licensed for external use.
Python:      3.9.5
"""

import csv
from datetime import datetime
import numpy as np
import math
import reqFromAPI
from matplotlib import pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import zipfile


def find_nearest_index(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def round_n(x, n):
    if x == 0:
        return x
    else:
        return round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))


class colormanager:
    def __init__(self, number_colors=14):
        self.number_colors = number_colors
        self.color_map = plt.get_cmap('nipy_spectral')
        self.colors = [self.color_map(1.0*i/self.number_colors)
                       for i in range(self.number_colors)]
        self.used = [False for i in range(self.number_colors)]
        return

    def get_color(self):
        i = 0
        while i < self.number_colors:
            if self.used[i] == False:
                self.used[i] = True
                return self.colors[i]
            i = i + 1
        return self.color_map(0.0)

    def free_color(self, color):
        self.used[self.colors.index(color)] = False
        return


class getfileGUI:
    def __init__(self, window):

        self.loaded = False

        self.window = window
        self.window.title('Open Data')

        button_file = tk.Button(
            self.window, command=self.choosefile, text='Select File')
        # pack(side='top',fill=tk.BOTH,expand=True)
        button_file.grid(row=0, columnspan=2)

        button_API = tk.Button(
            self.window, command=self.fileFromAPI, text='Select File using API')
        button_API.grid(row=1, columnspan=2)

        self.show_filename = tk.StringVar()
        self.label_filename = tk.Label(
            self.window, textvariable=self.show_filename)
        # pack() #side = 'top',fill=tk.BOTH,expand=True)
        self.label_filename.grid(row=2, columnspan=2)

        self.entrylabel_alias = tk.Label(self.window, text='Name')
        self.entry_alias = tk.Entry(self.window)
        self.entrylabel_alias.grid(row=3, column=0)
        self.entry_alias.grid(row=3, column=1)

        self.entrylabel_port = tk.Label(self.window, text='Port')
        self.entry_port = tk.Entry(self.window)
        self.entrylabel_port.grid(row=4, column=0)
        self.entry_port.grid(row=4, column=1)

        self.button_close = tk.Button(
            self.window, command=self.finish, text='Load')  # text='Done')
        # pack(side='top',fill=tk.BOTH,expand=True)
        self.button_close.grid(row=5, columnspan=2)

        return

    def fileFromAPI(self):

        self.subwindow2 = tk.Tk()
        self.subwindow2.title("Open Data from API")

        self.filename = None

        self.entrylabel_alias = tk.Label(self.subwindow2, text='Name')
        self.entry_alias = tk.Entry(self.subwindow2)
        self.entrylabel_alias.grid(row=0, column=0)
        self.entry_alias.grid(row=0, column=1)

        self.entrylabel_APIkey = tk.Label(self.subwindow2, text='API Key')
        self.APIkey = tk.Entry(self.subwindow2)
        self.entrylabel_APIkey.grid(row=1, column=0)
        self.APIkey.grid(row=1, column=1)

        self.entrylabel_node = tk.Label(
            self.subwindow2, text='Node Serial Number')
        self.node = tk.Entry(self.subwindow2)
        self.entrylabel_node.grid(row=2, column=0)
        self.node.grid(row=2, column=1)

        self.entrylabel_date = tk.Label(self.subwindow2, text='Date')
        self.entry_date = tk.Entry(self.subwindow2)
        self.entrylabel_date.grid(row=3, column=0)
        self.entry_date.grid(row=3, column=1)

        self.entrylabel_time = tk.Label(self.subwindow2, text='Time')
        self.entry_time = tk.Entry(self.subwindow2)
        self.entrylabel_time.grid(row=4, column=0)
        self.entry_time.grid(row=4, column=1)

        self.entrylabel_localZip = tk.Label(
            self.subwindow2, text='Local ZIP File Name')
        self.entry_localZip = tk.Entry(self.subwindow2)
        self.entrylabel_localZip.grid(row=5, column=0)
        self.entry_localZip.grid(row=5, column=1)

        self.entrylabel_X = tk.Label(self.subwindow2, text='X')
        self.entry_X = tk.Entry(self.subwindow2)
        self.entrylabel_X.grid(row=6, column=0)
        self.entry_X.grid(row=6, column=1)

        self.entrylabel_Y = tk.Label(self.subwindow2, text='Y')
        self.entry_Y = tk.Entry(self.subwindow2)
        self.entrylabel_Y.grid(row=7, column=0)
        self.entry_Y.grid(row=7, column=1)

        self.entrylabel_port = tk.Label(self.subwindow2, text='Port')
        self.entry_port = tk.Entry(self.subwindow2)
        self.entrylabel_port.grid(row=8, column=0)
        self.entry_port.grid(row=8, column=1)

        self.button_close2 = tk.Button(
            self.subwindow2, command=self.finishFromAPI, text='Load')  # text='Done')
        self.button_close2.grid(row=9, columnspan=2)

        return

    def choosefile(self):
        self.filename = tk.filedialog.askopenfilename(
            parent=self.window, title='Select File')
        self.show_filename.set(self.filename[self.filename.rfind('/')+1:])
        return

    def finish(self):
        self.alias = self.entry_alias.get()
        self.port = self.entry_port.get()
        self.date = None
        self.node = None
        self.time = None
        self.X = None
        self.localZip = None
        self.Y = None
        self.APIkey = None
        self.window.destroy()
        return

    def finishFromAPI(self):
        self.alias = self.entry_alias.get()
        self.APIkey = self.APIkey.get()
        self.node = self.node.get()
        self.date = self.entry_date.get()
        self.time = self.entry_time.get()
        self.localZip = self.entry_localZip.get()
        self.X = self.entry_X.get()
        self.Y = self.entry_Y.get()
        self.port = self.entry_port.get()
        self.subwindow2.destroy()
        self.window.destroy()
        return


class phaseGUI:
    def __init__(self, window):
        self.window = window
        self.subwindow = window
        self.colormanager = colormanager()
        self.data = {}
        self.fileframes = {}
        self.selectedfiles = {}
        self.colors = {}
        self.frequencies = []
        self.selected = False
        self.initialize_gui()
        return

    def initialize_gui(self):
        #self.window = tk.Tk()
        self.window.title('Vibration Phase Analysis')
        #self.resize_event = self.window.bind("<Configure>",self.scale)

        self.frame_controls = tk.Frame(self.window)
        self.frame_controls.pack(side='left', fill=tk.BOTH, expand=False)

        tk.Label(self.frame_controls, text=' Close ').grid(row=2, column=0)
        tk.Label(self.frame_controls, text=' Name ').grid(row=2, column=1)
        tk.Label(self.frame_controls, text=' Info ').grid(row=2, column=2)
        tk.Label(self.frame_controls, text=' Show ').grid(row=2, column=3)
        tk.Label(self.frame_controls, text=' Frequency ').grid(row=2, column=4)
        tk.Label(self.frame_controls, text=' Amplitude ').grid(row=2, column=5)
        tk.Label(self.frame_controls, text='   Phase   ').grid(row=2, column=6)

        self.button_select_frequency = tk.Button(
            self.frame_controls, text=' Select Frequency ', command=lambda: self.select_frequency(float(self.entry_frequency.get())))
        self.entry_frequency = tk.Entry(self.frame_controls)
        self.button_select_frequency.grid(row=1, column=0, columnspan=3)
        self.entry_frequency.grid(row=1, column=4, columnspan=3)

        self.frame_plot = tk.Frame(self.window)
        self.frame_plot.pack(side='left', fill=tk.BOTH, expand=True)

        self.button_openfile = tk.Button(
            self.frame_controls, command=self.openfile, text=' Open File ')
        self.button_openfile.grid(row=0, columnspan=3)

        #self.offset_files = 1

        """
        self.frame_plot_time = tk.Frame(self.frame_plot)
        self.frame_plot_time.grid(row=0,column=0,columnspan=3)
        self.frame_plot_freq = tk.Frame(self.frame_plot)
        self.frame_plot_freq.grid(row=1,column=0,columnspan=3)
        self.frame_plot_angle = tk.Frame(self.frame_plot)
        self.frame_plot_angle.grid(row=2,column=0)
        self.frame_plot_phase = tk.Frame(self.frame_plot)
        self.frame_plot_phase.grid(row=2,column=1,columnspan=2)
        """

        self.frame_plot_time = tk.Frame(self.frame_plot)
        self.frame_plot_time.pack(fill=tk.BOTH, side=tk.TOP, expand=1)
        self.frame_plot_freq = tk.Frame(self.frame_plot)
        self.frame_plot_freq.pack(fill=tk.BOTH, side=tk.TOP, expand=1)

        self.frame_plot_bottom = tk.Frame(self.frame_plot)
        self.frame_plot_bottom.pack(fill=tk.BOTH, side=tk.TOP, expand=1)

        self.frame_plot_angle = tk.Frame(self.frame_plot_bottom)
        self.frame_plot_angle.pack(fill=tk.BOTH, side=tk.LEFT, expand=1)
        self.frame_plot_phase = tk.Frame(self.frame_plot_bottom)
        self.frame_plot_phase.pack(fill=tk.BOTH, side=tk.LEFT, expand=1)

        fig_scale = 1.5

        self.fig_time = plt.Figure(figsize=(3*fig_scale, fig_scale))
        self.canvas_time = FigureCanvasTkAgg(
            self.fig_time, master=self.frame_plot_time)
        self.canvas_time.get_tk_widget().pack(fill=tk.BOTH, side=tk.LEFT, expand=1)

        self.fig_freq = plt.Figure(figsize=(3*fig_scale, fig_scale))
        self.canvas_freq = FigureCanvasTkAgg(
            self.fig_freq, master=self.frame_plot_freq)
        self.canvas_freq.get_tk_widget().pack(fill=tk.BOTH, side=tk.LEFT, expand=1)

        self.fig_angle = plt.Figure(figsize=(fig_scale, fig_scale))
        self.canvas_angle = FigureCanvasTkAgg(
            self.fig_angle, master=self.frame_plot_angle)
        self.canvas_angle.get_tk_widget().pack(fill=tk.BOTH, side=tk.LEFT, expand=1)

        self.fig_phase = plt.Figure(figsize=(2*fig_scale, fig_scale))
        self.canvas_phase = FigureCanvasTkAgg(
            self.fig_phase, master=self.frame_plot_phase)
        self.canvas_phase.get_tk_widget().pack(fill=tk.BOTH, side=tk.LEFT, expand=1)

        self.event_motion = self.canvas_freq.mpl_connect(
            'motion_notify_event', self.onmove)
        self.event_leave = self.canvas_freq.mpl_connect(
            'axes_leave_event', self.leave)
        self.event_select = self.canvas_freq.mpl_connect(
            'button_press_event', self.click)
        self.event_scroll = self.canvas_freq.mpl_connect(
            'scroll_event', self.zoom)

        self.event_scroll_time = self.canvas_time.mpl_connect(
            'scroll_event', self.zoom)
        self.event_scroll_phase = self.canvas_phase.mpl_connect(
            'scroll_event', self.zoom)

        self.event_scroll_angle = self.canvas_angle.mpl_connect(
            'scroll_event', self.zoom_polar)

        # self.window.mainloop()
        return

    def scale(self, event):
        if event.widget == self.frame_plot:
            print(event.widget.widgetName, event.width, event.height)
            self.canvas_time.resize(event.width, event.height//3)
            self.canvas_freq.resize(event.width, event.height//3)
            self.canvas_angle.resize(event.width//3, event.height//3)
            self.canvas_phase.resize(
                (event.width-event.width//3), event.height//3)
            self.fig_time.set_size_inches(
                event.width/100, event.height/300, forward=True)
            self.fig_freq.set_size_inches(
                event.width/100, event.height/300, forward=True)
            self.fig_angle.set_size_inches(
                event.width/300, event.height/300, forward=True)
            self.fig_phase.set_size_inches(
                event.width/150, event.height/300, forward=True)
        return

    def openfile(self):
        subwindow = getfileGUI(tk.Toplevel(self.window))
        subwindow.button_close.wait_window()
        if not hasattr(subwindow, 'filename') or not hasattr(subwindow, 'alias') or not hasattr(subwindow, 'port'):
            return
        if subwindow.filename in self.data.keys():
            errorwindow = tk.Toplevel(self.window)
            tk.Label(errorwindow, text="Error: \"" +
                     str(subwindow.alias)+"\" already exists.").pack()
            tk.Button(errorwindow, text="Close",
                      command=errorwindow.destroy).pack()
            return
        data = {}
        data['filename'] = subwindow.filename
        data['alias'] = subwindow.alias
        data['port'] = int(subwindow.port)
        if (subwindow.APIkey != None):
            data['API Key'] = subwindow.APIkey
            csvName = subwindow.date[4:6] + subwindow.date[2:4] + '.csv'
            if (data['API Key'] != None):
                unixTime = reqFromAPI.dateToUNIX(
                    subwindow.date, subwindow.time)
                APIData = {}
                APIData['ZipFileName'] = subwindow.localZip + '.zip'
                APIData['APIKey'] = subwindow.APIkey
                APIData['node'] = subwindow.node
                APIData['UNIXTime'] = unixTime
                APIData['XVal'] = subwindow.X
                APIData['YVal'] = subwindow.Y
                APIData['alias'] = subwindow.alias
                APIData['port'] = int(subwindow.port)
                reqFromAPI.runit(APIData['ZipFileName'], APIData['APIKey'], [
                                 APIData['node']], APIData['UNIXTime'])
                with zipfile.ZipFile(APIData['ZipFileName']) as zipDataFile:
                    listofFiles = zipDataFile.namelist()
                    if (subwindow.X == '1' and subwindow.Y != '1'):
                        for file in listofFiles:
                            if (file.endswith('X/'+csvName)):
                                file = zipDataFile.extract(file)
                                with open(file) as csvfile:
                                    line = next(csvfile)
                                    tstamp, srate, _nsamp, * \
                                        amp = line.split(",")
                                    data['alias'] = APIData['alias']
                                    data['port'] = APIData['port']
                                    data['date'] = datetime.fromtimestamp(
                                        int(tstamp) / 1000)
                                    data['rate'] = float(srate)
                                    data['time'] = [
                                        1000 / data['rate'] * i + 2.04*(data['port']-1) for i in range(int(_nsamp))]
                                    data['amplitude'] = [float(a) for a in amp]
                                    self.calc(data)
                    elif (subwindow.X != '1' and subwindow.Y == '1'):
                        for file in listofFiles:
                            if file.endswith('Y/' + csvName):
                                file = zipDataFile.extract(file)
                                with open(file) as csvfile:
                                    line = next(csvfile)
                                    tstamp, srate, _nsamp, * \
                                        amp = line.split(",")
                                    data['alias'] = APIData['alias']
                                    data['port'] = APIData['port']
                                    data['date'] = datetime.fromtimestamp(
                                        int(tstamp) / 1000)
                                    data['rate'] = float(srate)
                                    data['time'] = [
                                        1000 / data['rate'] * i + 2.04*(data['port']-1) for i in range(int(_nsamp))]
                                    data['amplitude'] = [float(a) for a in amp]
                                    self.calc(data)

                    elif (subwindow.X == '1' and subwindow.Y == '1'):
                        print(listofFiles)
                        for file in listofFiles:
                            file = zipDataFile.extract(file)
                            with open(file) as csvfile:
                                line = next(csvfile)
                                tstamp, srate, _nsamp, *amp = line.split(",")
                                if (file.endswith('X/' + csvName)):
                                    data['alias'] = APIData['alias'] + ' X'
                                else:
                                    data['alias'] = APIData['alias'] + ' Y'
                                data['port'] = APIData['port']
                                data['date'] = datetime.fromtimestamp(
                                    int(tstamp) / 1000)
                                data['rate'] = float(srate)
                                data['time'] = [1000 / data['rate'] * i + 2.04 *
                                                (data['port']-1) for i in range(int(_nsamp))]
                                data['amplitude'] = [float(a) for a in amp]
                                self.calc(data)

                    else:
                        with open(data['filename']) as csvfile:
                            csvreader = csv.reader(csvfile, delimiter=',')
                            lines = [[column for column in row]
                                     for row in csvreader]
                            # '%Y-%m-%dT%H:%M:%S.%f')
                            data['date'] = datetime.strptime(
                                lines[1][1], '%d-%b-%Y %H:%M:%S %p')
                            data['rate'] = float(lines[2][1])
                            # = [float(row[0]) for row in data[4:]]
                            data['time'] = [
                                float(row[0])+2.04*(data['port']-1) for row in lines[4:]]
                            data['amplitude'] = [
                                float(row[1]) for row in lines[4:]]
                            self.calc(data)

    # calculate FFT and Phase
    def calc(self, data):
        print('it runs self.calc(data)')
        data['samples'] = len(data['time'])
        data['frequency'] = [x*data['rate']/data['samples']
                             for x in range(data['samples']//2+1)]
        data['fft'] = [np.abs(x)/data['samples'] *
                       2 for x in np.fft.rfft(data['amplitude'])]
        data['phase'] = [(180/math.pi*np.angle(x) - 360*.00204*f*(data['port']-1)) %
                         360 for x, f in zip(np.fft.rfft(data['amplitude']), data['frequency'])]
        data['frequency label'] = tk.StringVar()
        data['amplitude label'] = tk.StringVar()
        data['phase label'] = tk.StringVar()
        data['selected'] = tk.IntVar(value=1)
        data['gui'] = [
            tk.Button(self.frame_controls, command=lambda: self.deletefile(
                data['alias']), text='X'),
            tk.Label(self.frame_controls, text=data['alias']),
            tk.Button(self.frame_controls, command=lambda: self.showinfo(
                data['alias']), text='?'),
            tk.Checkbutton(
                self.frame_controls, variable=data['selected'], command=lambda: self.hide(data['alias'])),
            tk.Label(self.frame_controls,
                     textvariable=data['frequency label']),
            tk.Label(self.frame_controls,
                     textvariable=data['amplitude label']),
            tk.Label(self.frame_controls, textvariable=data['phase label'])
        ]
        data['color'] = self.colormanager.get_color()
        self.data[data['alias']] = data
        i = 0
        for frame in self.data[data['alias']]['gui']:
            frame.grid(row=len(self.data)+2, column=i)
            i = i + 1
        self.clear_selection()
        self.frequencies = sorted(
            list(set(self.data[data['alias']]['frequency']+self.frequencies)))
        self.plot()

    def deletefile(self, alias):
        # undraw all elements to reset
        for item in self.data.values():
            for frame in item['gui']:
                frame.grid_forget()
        # delete data for 'alias'
        for frame in self.data[alias]['gui']:
            frame.destroy()
        self.colormanager.free_color(self.data[alias]['color'])
        del self.data[alias]
        # redraw remaining elements
        i = 3
        for items in self.data.values():
            j = 0
            for frame in items['gui']:
                frame.grid(row=i, column=j)
                j = j + 1
            i = i + 1
        # replot the data
        self.plot()
        # clear the hover / lock-in data
        freq_list = []
        for key in self.data.keys():
            freq_list = freq_list + self.data[key]['frequency']
        self.frequencies = sorted(list(set(freq_list)))
        return

    def showinfo(self, alias):
        subwindow = tk.Toplevel(self.window)
        subwindow.title(alias+' info')
        # tk.Label(subwindow,text='test').grid(row=6,column=0)
        tk.Label(subwindow, text='Name:').grid(row=0, column=0)
        tk.Label(subwindow, text=alias).grid(row=0, column=1)
        tk.Label(subwindow, text='File:').grid(row=1, column=0)
        tk.Label(subwindow, text=self.data[alias]['filename']).grid(
            row=1, column=1)
        tk.Label(subwindow, text='Date:').grid(row=2, column=0)
        tk.Label(subwindow, text=self.data[alias]['date']).grid(
            row=2, column=1)
        tk.Label(subwindow, text='Port:').grid(row=3, column=0)
        tk.Label(subwindow, text=self.data[alias]['port']).grid(
            row=3, column=1)
        tk.Label(subwindow, text='Rate:').grid(row=4, column=0)
        tk.Label(subwindow, text=self.data[alias]['rate']).grid(
            row=4, column=1)
        tk.Label(subwindow, text='Samples:').grid(row=5, column=0)
        tk.Label(subwindow, text=self.data[alias]['samples']).grid(
            row=5, column=1)
        tk.Button(subwindow, command=subwindow.destroy,
                  text='Close').grid(row=6, columnspan=2)
        return

    def clearplot(self):
        self.fig_time.clear()
        self.fig_freq.clear()
        self.fig_angle.clear()
        self.fig_phase.clear()
        self.canvas_time.draw()
        self.canvas_freq.draw()
        self.canvas_angle.draw()
        self.canvas_phase.draw()
        self.fig_time.set_tight_layout(True)
        self.fig_freq.set_tight_layout(True)
        self.fig_angle.set_tight_layout(True)
        self.fig_phase.set_tight_layout(True)
        return

    def hide(self, alias):

        if self.data[alias]['selected'].get() == 1:
            visible = True
        else:
            visible = False

        plots = ['time plot', 'frequency plot',
                 'angle plot', 'phase plot', 'point']
        for plot in plots:
            if plot in self.data[alias].keys():
                self.data[alias][plot].set_visible(visible)
                if plot != 'angle plot':
                    self.scale_y_axis(self.data[alias][plot].axes)

        self.canvas_time.figure.axes[0].legend(
            bbox_to_anchor=(1.05, 1), loc='upper left')
        self.canvas_time.draw()
        self.canvas_freq.draw()
        self.canvas_angle.draw()
        self.canvas_phase.draw()

        return

    def plot(self):
        if len(self.data) == 0:
            self.clearplot()
            return
        self.fig_time.clear()
        self.fig_freq.clear()
        self.fig_angle.clear()
        self.fig_phase.clear()
        self.fig_time.set_tight_layout(True)
        self.fig_freq.set_tight_layout(True)
        self.fig_angle.set_tight_layout(True)
        self.fig_phase.set_tight_layout(True)
        # self.clear_selection()

        self.ax1 = self.fig_freq.add_subplot(111)
        for key in self.data.keys():
            self.data[key]['frequency plot'], = self.ax1.plot(
                self.data[key]['frequency'][1:], self.data[key]['fft'][1:], color=self.data[key]['color'], label=key)
            if self.data[key]['selected'].get() == 0:
                self.data[key]['frequency plot'].set_visible(False)
        self.ax1.set_xlabel('frequency (Hz)')
        self.ax1.set_ylabel('acceleration (g)')

        ax0 = self.fig_time.add_subplot(111)
        for key in self.data.keys():
            self.data[key]['time plot'], = ax0.plot(
                self.data[key]['time'], self.data[key]['amplitude'], color=self.data[key]['color'], label=key)
            if self.data[key]['selected'].get() == 0:
                self.data[key]['time plot'].set_visible(False)
        ax0.set_xlabel('time (ms)')
        ax0.set_ylabel('acceleration (g)')
        ax0.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        if len(self.data) == 0:
            self.clearplot()

        self.canvas_time.draw()
        self.canvas_freq.draw()
        self.canvas_angle.draw()
        self.canvas_phase.draw()
        if self.selected:
            self.plot_phase()
        return

    def plot_phase(self):
        self.fig_angle.clear()
        self.fig_phase.clear()
        self.fig_angle.set_tight_layout(True)
        self.fig_phase.set_tight_layout(True)

        ax2 = self.fig_angle.add_subplot(111, polar=True)
        for key in self.data.keys():
            index = find_nearest_index(
                self.data[key]['frequency'], self.frequency)
            angle = self.data[key]['phase'][index] / 180.0 * math.pi
            self.data[key]['angle plot'], = ax2.plot([angle, angle], [
                                                     0, self.data[key]['fft'][index]], color=self.data[key]['color'], label=key)
            if self.data[key]['selected'].get() == 0:
                self.data[key]['angle plot'].set_visible(False)
        ax2.set_yticklabels([])
        ax2.yaxis.grid(False)
        # ax2.set_theta_zero_location('N')

        ax3 = self.fig_phase.add_subplot(111)
        time = [i/1024*4/self.frequency*1000 for i in range(1024)]
        for key in self.data.keys():
            index = find_nearest_index(
                self.data[key]['frequency'], self.frequency)
            angle = self.data[key]['phase'][index] / 180 * math.pi
            self.data[key]['phase plot'], = ax3.plot(time, [math.cos(
                2*math.pi*self.data[key]['frequency'][index]*t/1000+angle) for t in time], color=self.data[key]['color'], label=key)
            if self.data[key]['selected'].get() == 0:
                self.data[key]['phase plot'].set_visible(False)
        ax3.set_xlabel('time (ms)')
        ax3.set_ylabel(str(self.frequencies[self.index])+' Hz phase')
        #ax3.set_ylabel(str(self.frequencies[self.index])+'Hz acceleration (normalized)')

        self.canvas_angle.draw()
        self.canvas_phase.draw()
        return

    def onmove(self, event):
        if self.selected:
            return
        if hasattr(self, 'locator'):
            self.locator.remove()
            del self.locator
        if event.inaxes:
            idx = find_nearest_index(self.frequencies, event.xdata)
            if idx == 0:
                idx += 1
            self.index = idx
            self.locator = self.ax1.axvline(
                x=self.frequencies[idx], color='black')
            self.canvas_freq.draw()
            for data in self.data.values():
                index = find_nearest_index(data['frequency'], event.xdata)
                data['frequency label'].set(data['frequency'][index])
                data['amplitude label'].set(round_n(data['fft'][index], 3))
                data['phase label'].set(int(data['phase'][index]))
        return

    def leave(self, leave):
        if self.selected:
            return
        self.clear_selection()
        return

    def click(self, event):
        if event.button == 1 and event.inaxes:
            #self.frequency = event.xdata
            self.select_frequency(event.xdata)
        if event.button == 3:
            self.clear_selection()
            self.fig_angle.clear()
            self.fig_phase.clear()
            self.canvas_angle.draw()
            self.canvas_phase.draw()
            self.fig_angle.set_tight_layout(True)
            self.fig_phase.set_tight_layout(True)
        return

    def select_frequency(self, frequency):
        self.clear_selection()
        self.selected = True
        self.frequency = frequency
        idx = find_nearest_index(self.frequencies, self.frequency)
        if idx == 0:
            idx += 1
        self.index = idx
        self.locator = self.ax1.axvline(x=self.frequencies[idx], color='black')
        for data in self.data.values():
            index = find_nearest_index(data['frequency'], self.frequency)
            if index == 0:
                index += 1
            data['frequency label'].set(data['frequency'][index])
            data['amplitude label'].set(round_n(data['fft'][index], 3))
            data['phase label'].set(int(data['phase'][index]))
            data['point'], = self.ax1.plot(
                data['frequency'][index], data['fft'][index], 'o', mfc=data['color'], mec='black', ms=10)
        self.canvas_freq.draw()
        self.plot_phase()
        return

    def clear_selection(self):
        if hasattr(self, 'locator'):
            self.locator.remove()
            del self.locator
        for data in self.data.values():
            data['frequency label'].set('')
            data['amplitude label'].set('')
            data['phase label'].set('')
            if 'point' in data.keys():
                data['point'].remove()
                del data['point']
        self.canvas_freq.draw()
        self.selected = False
        return

    def zoom_polar(self, event):
        if not event.inaxes:
            return
        canvas = event.canvas
        ax = event.inaxes
        factor = 1.5
        r_min, r_max = ax.get_ylim()
        maximum = ax.dataLim.get_points()[1][1]
        if event.button == 'up':
            r_max = r_max / factor
        elif event.button == 'down':
            r_max = r_max * factor
        if r_max > maximum * 1.05:
            r_max = maximum * 1.05
        ax.set_ylim(r_min, r_max)
        canvas.draw()
        return

    def zoom(self, event):
        if not event.inaxes:
            return
        canvas = event.canvas
        ax = event.inaxes
        factor = 1.5
        xmin, xmax = ax.get_xlim()
        span = xmax - xmin
        mid = event.xdata
        xdatamin = ax.dataLim.get_points()[0][0]
        xdatamax = ax.dataLim.get_points()[1][0]
        xmin0 = xdatamin - 0.05 * (xdatamax - xdatamin)
        xmax0 = xdatamax + 0.05 * (xdatamax - xdatamin)
        left = (event.xdata-xmin)/(xmax-xmin)
        if event.button == 'up':
            span = span / factor
        elif event.button == 'down':
            span = span * factor
        if span >= (xmax0 - xmin0):
            ax.set_xlim([xmin0, xmax0])
            canvas.draw()
            return
        xmin = event.xdata - left*span
        xmax = xmin + span
        if xmin < xdatamin-0.05/1.1*span:
            xmin = xdatamin-0.05/1.1*span
            xmax = xmin + span
        elif xmax > xdatamax+0.05/1.1*span:
            xmax = xdatamax+0.05/1.1*span
            xmin = xmax - span
        ax.set_xlim([xmin, xmax])
        self.scale_y_axis(ax)
        canvas.draw()
        return

    def scale_y_axis(self, ax):
        bot, top = ax.get_ylim()
        left, right = ax.get_xlim()
        lines = ax.get_lines()
        y_min = 1000000
        y_max = -1000000
        switch = False
        for line in lines:
            if line._visible == True:
                x = line.get_xdata()
                # Skip ax.vlines
                if len(x) == 2 and x[0] == x[1]:
                    continue
                y = line.get_ydata()
                y_inplot = [b for a, b in zip(
                    x, y) if a >= left and a <= right]
                # Skip if no data points
                if (len(y_inplot) == 0):
                    continue
                switch = True
                if max(y_inplot) > y_max:
                    y_max = max(y_inplot)
                if min(y_inplot) < y_min:
                    y_min = min(y_inplot)
        if not switch:
            y_min = 0
            y_max = 1
        else:
            buffer = 0.05*(y_max - y_min)
            y_max += buffer
            y_min -= buffer
        ax.set_ylim(y_min, y_max)
        return


window = tk.Tk()
app = phaseGUI(window)
window.mainloop()
