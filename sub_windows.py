import matplotlib.pyplot as plt
import tkinter as TK
import numpy as np
import pydicom as pyd
import os, cv2
from scipy.optimize import curve_fit
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import PolygonSelector
from matplotlib.path import Path

CMAP = ["jet","gnuplot","gnuplot2","CMRmap","ocean","gist_earth","gist_stern","terrain",
        "cubehelix","brg","gist_rainbow","rainbow","nipy_spectral","gist_ncar"]

class SelectFromCollection(object):
    def __init__(self, ax, collection, alpha_other=0.3):
        self.canvas = ax.figure.canvas
        self.collection = collection
        self.alpha_other = alpha_other

        self.poly  = PolygonSelector(ax, self.onselect)

    def onselect(self, verts):
        print(verts)
        path = Path(verts)
        self.canvas.draw_idle()

    def disconnect(self):
        self.poly.disconnect_events()
        self.canvas.draw_idle()

class MAP_VIEWER: #3
    def __init__(self, master, src, fig_index=3, lock=False, win_title='Image Viewer', title='Image map'):
        self.POPUP = TK.Toplevel(master)
        self.POPUP.geometry('650x575+100+100')
        self.screen_width = self.POPUP.winfo_screenwidth()
        self.screen_height = self.POPUP.winfo_screenheight()
        self.src = src; self.idx = 0
        self.POPUP.title(win_title)
        self.POPUP.resizable(0,0)
        self.fig_index = fig_index
        self.SI_FRAME = TK.Frame(self.POPUP)
        self.SI_FRAME.place(x=0,y=0,width=650,height=540)
        self.VALUE = TK.StringVar(); self.VALUE.set('None')
        self.SI_FIG = plt.figure(self.fig_index,[7,6])
        self.SI_CANVAS = FigureCanvasTkAgg(self.SI_FIG, master=self.SI_FRAME)
        self.SI_CANVAS.get_tk_widget().pack(fill='both')

        self.ax = self.SI_FIG.add_subplot(111)
        self.IM = self.ax.imshow(self.src, cmap='jet')
        self.title=title
        plt.title(self.title); plt.grid(b=None)
        self.SI_FIG.colorbar(self.IM)
        
        self.SI_CANVAS.draw()
        self.VMIN, self.VMAX = self.src.min(), self.src.max()
        toolbarFrame = TK.Frame(master=self.POPUP)
        toolbarFrame.place(x=0,y=540,width=600)
        toolbar = NavigationToolbar2Tk(self.SI_CANVAS, toolbarFrame)
        if lock: self.POPUP.grab_set()
        self.POPUP.protocol('WM_DELETE_WINDOW',self.Close)
        self.RANGE_SET = TK.Button(self.POPUP, text='Range', command=self.Range_Setup)
        self.RANGE_SET.place(x=240,y=544,width=45,height=30)
        self.TEXT = TK.Label(self.POPUP, textvariable=self.VALUE)
        self.TEXT.place(x=290, y=544, width=200, height=30)
        self.poly  = PolygonSelector(self.ax, self.onselect)
        #self.POPUP.mainloop()
    
    def onselect(self, verts):
        MASK = np.zeros_like(self.src)
        MASK = cv2.fillPoly(MASK, [np.array(verts,np.int32)], 255)
        VALUE = self.src[np.where(MASK!=0)].mean() 
        self.VALUE.set('{0}'.format( VALUE ))
        print(VALUE)
        path = Path(verts)
        self.SI_CANVAS.draw_idle()

    def Close(self):
        plt.close(self.SI_FIG)
        self.POPUP.destroy()

    def Range_Setup(self):
        self.window = TK.Toplevel(self.POPUP)
        self.window.config(bg='#1E1E1E')
        self.window.geometry('210x170+{0}+{1}'.format(self.screen_width//2-105, self.screen_height//2-85))
        self.window.resizable(0,0)
        self.LABEL_INTERVAL1 = TK.Label(self.window, text='VMIN',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_INTERVAL1.place(x=10,y=10,width=70, height=20)
        self.INPUT_INTERVAL1 = TK.Entry(self.window)
        self.INPUT_INTERVAL1.place(x=85,y=10,width=95, height=20)
        self.INPUT_INTERVAL1.insert(0,self.VMIN)
        self.LABEL_INTERVAL2 = TK.Label(self.window, text='VMAX',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_INTERVAL2.place(x=10,y=50,width=70, height=20)
        self.INPUT_INTERVAL2 = TK.Entry(self.window)
        self.INPUT_INTERVAL2.place(x=85,y=50,width=95, height=20)
        self.INPUT_INTERVAL2.insert(0,self.VMAX)
        self.LABEL_CMAP = TK.Label(self.window, text='CMAP',background='#1E1E1E',foreground='#FFFFFF')
        self.LABEL_CMAP.place(x=10,y=90,width=70, height=20)
        self.MODE_COMBOBOX = ttk.Combobox(self.window, height=30, values=CMAP, state='readonly')
        self.MODE_COMBOBOX.place(x=85,y=90,width=95)
        self.MODE_COMBOBOX.current(self.idx)
        self.PROCESS = TK.Button(self.window, command=self.Range_Setup_Close, text='Change',bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771' )
        self.PROCESS.place(x=60,y=130,width=90,height=30)
        self.window.grab_set()

    def PLOT(self):
        #plt.figure(self.fig_index); plt.cla()
        self.SI_FIG = plt.figure(self.fig_index,[7,6])
        self.ax = self.SI_FIG.add_subplot(111)
        if self.title!='': plt.title(self.title)
        plt.grid(b=None);self.VALUE.set('')
        self.IM = self.ax.imshow(self.src,  cmap=CMAP[self.idx],vmin=self.VMIN, vmax=self.VMAX)
        self.SI_FIG.colorbar(self.IM)
        self.SI_CANVAS.draw()
        self.poly  = PolygonSelector(self.ax, self.onselect)

    def Range_Setup_Close(self):
        try: self.VMIN = float(self.INPUT_INTERVAL1.get()); self.VMAX = float(self.INPUT_INTERVAL2.get())
        except: messagebox.showerror('ERROR!',"Invalid parameter!"); return None
        self.idx=self.MODE_COMBOBOX.current()
        self.SI_FIG.clear(); self.PLOT()
        self.window.destroy()

class LIST_VIEWER: #3
    def __init__(self, master, lock=False, title='FILE LIST'):
        self.FLIST = []
        self.POPUP = TK.Toplevel(master.WINDOW)
        self.Master = master
        self.My_Screen = [self.POPUP.winfo_screenwidth(), self.POPUP.winfo_screenheight()]
        self.POPUP.geometry('350x615+{0}+{1}'.format(self.My_Screen[0]//2+300//2, 100))
        self.POPUP.title(title)
        self.POPUP.resizable(0,0)

        self.TABLE = ttk.Treeview(self.POPUP, columns = ['#0'])
        self.TABLE.column('#0' ,width=350)
        self.TABLE.heading('#0' , text='File')
        self.TABLE.place(x=10,y=10,width=310,height=535)

        self.V_SCROLL = TK.Scrollbar(self.POPUP, jump=True)
        self.V_SCROLL.place(x=320,y=10, width=20, height=555)
        self.V_SCROLL.config(command=self.TABLE.yview)

        self.H_SCROLL = TK.Scrollbar(self.POPUP, jump=True, orient='horizontal')
        self.H_SCROLL.place(x=10,y=535, width=310, height=20)
        self.H_SCROLL.config(command=self.TABLE.xview)

        self.CLEAR = TK.Button(self.POPUP, text='초기화', command=self.Reset_List)
        self.CLEAR.place(x=10,y=575,width=330, height=30)

        self.TABLE.bind('<Double-Button-1>', self.Load_list_file)
        self.POPUP.protocol('WM_DELETE_WINDOW',self.Close)
    
    def Close(self):
        self.Master.FILE_LIST_WINDOW = False
        self.POPUP.destroy()

    def Reset_List(self):
        self.TABLE.delete(*self.TABLE.get_children())
        self.Master.WHOLE_LIST = []
    
    def Add_List(self, PATH):
        idx = len(self.FLIST)
        if PATH not in self.FLIST:
            self.TABLE.insert('','end',text=PATH, values=idx)
            self.FLIST.append(PATH)
        return self.FLIST
    
    def Load_list_file(self, a=None):
        GET = self.TABLE.item(self.TABLE.focus())['text']
        if GET!='':
            self.Master.FILE_OPEN_DICOMS(override=GET)
