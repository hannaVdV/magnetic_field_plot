# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 12:04:42 2021

@author: hannav
"""
import numpy as np
from scipy.interpolate import griddata
import serial
import serial.tools.list_ports
import tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import time 

#global variable tells if we need auto plotting or not
plot_data = False
#global variable that connects to the serial port
ser = None
#global variables for plotting the function
window = None
fig = None
canvas = None
new = []


def get_COM_list():
    """Looks how many Prots thre are and makes a list, sets which port to use"""
    find_com = serial.tools.list_ports
    COM = find_com.comports()
    COM_list = []
    for x in COM:
        COM_list.append(x[0])
    return COM_list


def verknupfung(port):
    """ Connect to a serial port, given the port"""
    global ser
    print("COM choice:", port)
    try:
        ser = serial.Serial(
            port=port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.05,
        )
    except Exception as e:
        print(e)
        ser = None


def get_grid():
    """ reads data from the serial port (if initialized) and returns a 2D grid"""
    global ser
    while True:
        try:
            z = ser.readline()
            if z != b"":
                z = z.decode("utf-8")
                z = z.split(",")
                z[-1] = z[-1].replace("\r\n", "")
                z = [float(j) for j in z]

                yses = [0, 2, 4, 1, 3, 0, 2, 4]
                xses = [3, 4, 3, 2, 2, 1, 0, 1]

                grid_x, grid_y = np.mgrid[0:4:5j, 0:4:5j]
                grid_z = griddata((xses, yses), z, (grid_x, grid_y), method="linear")
                new.clear()
                return grid_z                

            else:
                leg = len(new)
                new.append(leg + 1)

                if leg == 100:
                    new.clear()
                    break

        except Exception as e:
            print(e)
            return None


def plot():
    """ plots the data on the Tk fig/canvas """
    global fig, canvas, nodata
    #plotting the graph, if we have data
    grid_z = get_grid()
        
    if grid_z is None:
        error_message = "No data: Did you select the serial port?"
        nodata = tkinter.Label(window, text = error_message) 
        nodata.grid(row=2, column=0, columnspan=2, padx='5', pady='5', sticky="w") 
        print(error_message)
        return

    N = 100
    fig.clear()
    ax1 = fig.add_subplot(111)
    ax1.set_title("Measurement:   "+time.asctime())
    z_plot = ax1.contourf(grid_z, N, cmap="viridis")
    fig.colorbar(z_plot, ax=ax1)
    canvas.draw()


def remove():
    """remove the error message"""
    nodata.destroy()


def loop():
    """checks if we need a plot, and reschedules itself after 200ms"""
    global plot_data, window
    if plot_data:
        plot()
    window.after(100, loop)


def toggle():
    """toggle the state of the plot data"""
    global plot_data
    plot_data = not plot_data
    #changing text on toggle_button
    if plot_data is True:
        toggle_button.config(text="Auto Update ON", bg = "#bcbcbc")
    else:
        toggle_button.config(text="Auto Update OFF" ,bg = "#eeeeee")


def main():
    global window, fig, canvas, toggle_button,nodata
    #the main Tkinter window
    window = tkinter.Tk()
    #setting the title
    window.title("Magnetic field plot")
    #dimensions of the main window
    window.geometry("586x470")
    window.resizable(width=False, height=False)


    #chose a Port
    value_inside = tkinter.StringVar(window)
    value_inside.set("Select a port: ")
    question_menu = tkinter.OptionMenu(
        window, value_inside, *get_COM_list(), command=verknupfung
        )
    question_menu.grid(row=1, column=0, padx=5, pady=5)
    question_menu.config(width = 17)
    question_menu.config(height = 2)


    #button that displays the plot
    plot_button = tkinter.Button(
        master=window, command=plot, height=2, width=20, text="Plot once"
    )
    #place the button in main window
    plot_button.grid(row=1, column=1, padx=5, pady=5)
    plot_button.config(width = 17)

      
    #buttons that start/stop the loop
    toggle_button = tkinter.Button(
        master=window, command=toggle, height=2, width=20, text= "Auto Update OFF", bg = "#eeeeee"
    )
    toggle_button.grid(row=1, column=2, padx=5, pady=5)
    toggle_button.config(width = 17)

    #button ends programm
    quit_button = tkinter.Button(
        window, text="Quit", height=2, width=20, command=window.destroy, bg = "#e54747"
    )
    quit_button.grid(row=1, column=3, padx=5, pady=5)
    quit_button.config(width = 17)


    #button that displays the plot
    remove_error = tkinter.Button(
        master=window, command = remove, height=2, width=20, text="Remove error message"
    )
    #place the button in main window
    remove_error.grid(row=2, column=3,padx=5, pady=5)
    remove_error.config(width = 17)
    
    
    #the figure that will contain the plot
    fig = Figure(figsize=(8, 5))
    #creating the Tkinter canvas
    #containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=window)
    #placing the canvas on the Tkinter window
    canvas.get_tk_widget().grid(row=0, column = 0, columnspan = 4, padx=5)


    #run the gui
    window.after(200, loop)
    window.mainloop()

if __name__ == "__main__":
    #execute only if run as a script
    main()