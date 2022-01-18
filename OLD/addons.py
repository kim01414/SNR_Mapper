import cv2, os, pydicom, csv, math, scipy, time
import tkinter as TK
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from PIL import Image, ImageTk
from tkinter import filedialog, Tk, ttk, messagebox, Menu
from scipy import signal, ndimage

Options = ['ocean','gist_earth','terrain','gist_stern','gnuplot','gnuplot2','CMRmap',
                        'cubehelix','brg','gist_rainbow','rainbow','jet','nipy_spectral','gist_ncar']

def nothing(x=None):
    pass

def FATAL_ERROR(title='FATAL_ERROR',what='FATAL_ERROR_TEST'):
    messagebox.showerror(title, what)

def ERROR(title='ERROR',what='ERROR_TEST'):
    messagebox.showwarning(title, what)

def INFO(title='INFO',what='Info_TEST'):
    messagebox.showinfo(title,what)

def question(title='Question',what='Question Test'):
    rtn = messagebox.askyesno(title,what)
    return rtn



def gaussian_kernel(size, sigma=1):
    size = int(size) // 2
    x,y = np.mgrid[-size:size+1, -size:size+1]
    normal = 1 / (2.0*np.pi*sigma**2)
    g = np.exp( - ( (x**2 + y**2 ) / (2.0*sigma**2)) ) * normal
    return g

def IMAGE_PROCESS(img):
    IMG = img.copy()
    gKernel = gaussian_kernel(5, 1.4)
    blured = scipy.signal.convolve2d(IMG, gKernel)
    Kx = np.array([[-1,0,1],[-2,0,2],[-1,0,1]],np.float32)
    Ky = np.array([[1,2,1],[0,0,0],[-1,-2,-1]],np.float32)
    Ix = ndimage.filters.convolve(img,Kx)
    Iy = ndimage.filters.convolve(img,Ky)
    
    G = np.hypot(Ix, Iy) #hypotenuse
    G = G / G.max() * 255
    theta = np.arctan2(Iy, Ix)
    
    return G#(G, theta, Ix, Iy)

class ROI_LIST:
    def __init__(self, MAIN_PROGRAM, IMAGE_WINDOW, IMAGE):
        self.IMAGE = IMAGE
        self.MAIN_PROGRAM = MAIN_PROGRAM
        self.IMAGE_WINDOW = IMAGE_WINDOW
        self.MAIN = TK.Toplevel()
        self.MAIN.geometry('490x500+{0}+140'.format(self.MAIN_PROGRAM.SCREEN_SIZE[1]-500,0))
        self.MAIN.minsize(490,500)
        self.MAIN.resizable(1,1)
        self.MAIN.title('ROI LIST - {0}'.format(self.IMAGE.IMAGE_NAME.split('/')[-1]))
        self.MAIN.protocol('WM_DELETE_WINDOW',self.destroy)
        self.MAIN.bind('<Configure>',self.Resize_WINDOW)
        self.W, self.H = 490, 500
        
        self.TABLE =  TK.ttk.Treeview(self.MAIN, columns = ['#0', '#1', '#2', '#3'] )
        self.TABLE.column('#0',width=50)
        self.TABLE.column('#1',width=60)
        self.TABLE.column('#2',width=310)
        self.TABLE.column('#3',width=50)
        self.TABLE.heading('#0', text='Image#')
        self.TABLE.heading('#1', text='IMG_ROI#')
        self.TABLE.heading('#2', text='Points')
        self.TABLE.heading('#3', text='Type')
        self.TABLE.place(x=0 ,y=0,width=470,height=400)
        self.TABLE.bind('<Button-3>',self.COMMAND_TEST)

        self.TABLE_SCROLL = TK.Scrollbar(self.MAIN, jump=True)
        self.TABLE_SCROLL.place(x=470 ,y=30,width=20,height=500)
        self.TABLE_SCROLL.config(command=self.TABLE.yview)

        self.TABLE_SCROLL2 = TK.Scrollbar(self.MAIN, jump=True,orient='horizontal')
        self.TABLE_SCROLL2.place(x=0 ,y=480,width=490,height=20)
        self.TABLE_SCROLL2.config(command=self.TABLE.xview)
        self.Reload_ROIs()

    def COMMAND_TEST(self,event):
        iid = self.TABLE.identify_row(event.y)
        if iid:
            self.TABLE.selection_set(iid)
            print(self.TABLE.focus()), iid

    def Resize_WINDOW(self,event):
        W, H = self.MAIN.winfo_width(), self.MAIN.winfo_height()
        if self.W==W and self.H==H: return None
        self.TABLE.place_forget()
        self.TABLE_SCROLL.place_forget()
        self.TABLE_SCROLL2.place_forget()
        self.TABLE.place(x=0,y=0,width=W-20,height=H)
        self.TABLE_SCROLL.place(x=W-20,y=30,width=20,height=H)
        self.TABLE_SCROLL2.place(x=0,y=H-20,width=W-20,height=20)
        self.W, self.H = W, H

    def Reload_ROIs(self):
        self.TABLE.delete(*self.TABLE.get_children())
        INDEX=0
        for roi_idx in range(len(self.IMAGE.ROI_POINTs)):
            INDEX+=1
            VALUE = ['#{0}'.format(roi_idx+1),"'"+str(str(self.IMAGE.ROI_POINTs[roi_idx][0]).split('\n'))[3:-3]+"'",
                                                                                             self.IMAGE.ROI_TYPEs[roi_idx]]
            self.TABLE.insert('','end',text=1, values=VALUE,iid=str(INDEX))
    
    def destroy(self):
        self.Clear_ROIs()
        self.MAIN.destroy()
        self.IMAGE_WINDOW.ROI_LIST_OPEN=False

    def Clear_ROIs(self):
        self.TABLE.delete(*self.TABLE.get_children())

class IMAGE:
    def __init__(self, DIR):
        self.ROI_Current_pts = []
        self.ROI_POINTs = []
        self.ROI_SUB_POINTs = []
        self.ROI_TYPEs = []
        self.Cur_ROI = -1
        self.Need_Refresh = True
        self.MASK = None
        self.N_MASK = None
        self.IMAGE_NAME = DIR
        self.FILE = pydicom.dcmread(DIR) #DICOM 파일 불러오기
        self.Source_Intensity = self.FILE.pixel_array.copy() #원본 Intensity 기록
        self.shape = list(self.Source_Intensity.shape) #화면 출력용 이미지 크기 확인
        self.shape.extend([3]) #화면 출력용 이미지 GRAY to RGB
        self.MAX_INTENSITY = self.Source_Intensity.max()
        self.MIN_INTENSITY = self.Source_Intensity.min()
        self.MEAN_INTENSITY = self.Source_Intensity.mean()
        self.STD_INTENSITY = self.Source_Intensity.std()
        self.Threshold = -1
        self.W,self.H = self.shape[:2]
        self.W0, self.H0 = self.shape[:2]
        self.IsZoomed = False
        self.Zoomed = None
        self.Zoomed_Point = []
        self.scale = 1
        
    def Create_RGB_IMAGE(self, src, visible=True, plz_rtn=False):
        self.Source_Normalized = src / self.Source_Intensity.max() * 255 #화면 출력용 이미지
        self.Source_RGB = np.zeros(self.shape).astype(np.float64)
        self.Source_RGB[:,:,0], self.Source_RGB[:,:,1], self.Source_RGB[:,:,2], = self.Source_Normalized,self.Source_Normalized,self.Source_Normalized
        if plz_rtn==True: return self.Source_RGB.astype(np.uint8)
        self.Source_RGB = self.Source_RGB.astype(np.uint8)

        if visible==True: self.Source_RGB = self.Draw_ROI_LINES(self.Source_RGB)
        self.Source_RGB_TK = self.Convert_TK_IMAGE(self.Source_RGB)

    def Convert_TK_IMAGE(self, src):
        return ImageTk.PhotoImage(Image.fromarray(src))

    def Draw_ROI_LINES(self, src):
        GREEN = (0,255,0)
        RED = (255,0,0)
        YELLOW = (255,255,0)
        for pt in self.ROI_Current_pts: src[pt[1]][pt[0]] = YELLOW
        for idx in range(len(self.ROI_POINTs)):
            if self.Cur_ROI==idx: color=YELLOW
            elif self.ROI_TYPEs[idx]=='Normal': color = GREEN
            else: color = RED

            if self.ROI_POINTs[idx].shape[1]==2: #Circle
                X0, Y0 = self.ROI_POINTs[idx][0][0][0], self.ROI_POINTs[idx][0][0][1]
                X1, Y1 = self.ROI_POINTs[idx][0][1][0], self.ROI_POINTs[idx][0][1][1]
                X2, Y2 = (X0+X1)//2, (Y0+Y1)//2
                cv2.ellipse(src, (X2,Y2), (abs(X1-X2),abs(Y1-Y2)),0,0,360,color,1)
            else: #Free , Rectangular
                src = cv2.polylines(src, [self.ROI_POINTs[idx]], True, color, 1)
            cv2.putText(src,'#{0}'.format(idx+1),tuple(self.ROI_POINTs[idx][0][0]),cv2.FONT_HERSHEY_PLAIN, 1, color,1,cv2.LINE_AA)
        
        ######Create MASK for Normal ROIs#####
        self.MASK = np.zeros_like(self.Source_RGB)
        if len(self.ROI_POINTs)!=0:
            if 'Normal' not in self.ROI_TYPEs: self.MASK[:,:,:] = 255
            else: 
                for idx in range(len(self.ROI_POINTs)):
                    if self.ROI_TYPEs[idx]=='Normal':
                        if self.ROI_POINTs[idx].shape[1]!=2:
                            cv2.fillPoly(self.MASK, self.ROI_POINTs[idx], (255,255,255) )
                        else: 
                            X0, Y0 = self.ROI_POINTs[idx][0][0][0], self.ROI_POINTs[idx][0][0][1]
                            X1, Y1 = self.ROI_POINTs[idx][0][1][0], self.ROI_POINTs[idx][0][1][1]
                            X2, Y2 = (X0+X1)//2, (Y0+Y1)//2
                            cv2.ellipse(self.MASK, (X2,Y2), (abs(X0-X2),abs(Y0-Y2)), 0,0 ,360, (255,255,255),-1)
        else:  self.MASK[:,:,:] = 255
        return src

    def Apply_Threshold(self, threshold, Visible=True, force=False, refresh_noise=False):
        if self.Threshold!=threshold or force==True:
            if force==False: 
                if self.Need_Refresh==False: return None
                self.Threshold = threshold
            self.Need_Refresh = True
            y, x = np.where(self.Source_Intensity <= self.Threshold)
            self.COPIED = self.Source_Intensity.copy()
            self.COPIED[y,x] = 0
            self.Create_RGB_IMAGE(self.COPIED, Visible)
                
            if refresh_noise==True:
                if 'Noise' not in self.ROI_TYPEs: self.trash = self.Source_Intensity[y,x] #Threshold값 이하인 값들
                else:
                    self.N_MASK = np.zeros_like(self.Source_Intensity)
                    for idx in range(len(self.ROI_POINTs)):
                        if self.ROI_TYPEs[idx]=='Noise': 
                            if self.ROI_POINTs[idx].shape[1]!=2: cv2.fillPoly(self.N_MASK, self.ROI_POINTs[idx], (255,255,255) )
                            else: 
                                X0, Y0 = self.ROI_POINTs[idx][0][0][0], self.ROI_POINTs[idx][0][0][1]
                                X1, Y1 = self.ROI_POINTs[idx][0][1][0], self.ROI_POINTs[idx][0][1][1]
                                X2, Y2 = (X0+X1)//2, (Y0+Y1)//2
                                cv2.ellipse(self.N_MASK, (X2,Y2), (abs(X0-X2),abs(Y0-Y2)), 0,0 ,360, (255,255,255),-1)
                    self.trash = self.Source_Intensity[np.where(self.N_MASK==255)]
                self.trash_STD = self.trash.std()
                if self.trash_STD==0: self.trash_STD=1
            

class WIZARD:
    def __init__(self, IMAGE):
       # plt.rcParams.update({'figure.max_open_warning': 0})
        self.Wizard = TK.Toplevel()
        self.Wizard.geometry('800x520+560+240')
        self.Wizard.minsize(800,520)
        self.W, self.H = 800, 520
        self.Wizard.title('Color Mapping Wizard')
        self.Wizard.protocol('WM_DELETE_WINDOW',self.destroy)
        self.IMAGE = IMAGE
        self.THIS = self.IMAGE.COPIED / self.IMAGE.trash_STD
        self.Entries = [TK.StringVar(),TK.StringVar(),TK.StringVar(),TK.StringVar(),TK.StringVar()] 
        self.LABELs = []
        #TITLE, MIN, MAX, init_MIN, init_MAX
        self.Entries[0].set(self.IMAGE.IMAGE_NAME.split('/')[-1])
        self.Entries[1].set(str(self.THIS.min()))
        self.Entries[2].set(str(self.THIS.max()))
        self.Entries[3].set(str(self.THIS.min()))
        self.Entries[4].set(str(self.THIS.max()))
        self.Options = ['jet','ocean','gist_earth','terrain','gist_stern','gnuplot','gnuplot2',
                       'CMRmap','cubehelix','brg','gist_rainbow','rainbow','nipy_spectral','gist_ncar']
        self.IMAGE_SIZE = TK.StringVar()
        self.IMAGE_SIZE.set('Size: 640 x 480')
        self.GET_UI()
        self.Wizard.bind('<Configure>',self.Resize_WINDOW)
        
    def GET_UI(self):
        self.IMG_Properties = TK.LabelFrame(self.Wizard,text='Image Properties')
        self.IMG_Properties.place(x=525,y=20,width=250)
        self.IMAGE_SIZE_LABEL = TK.Label(self.IMG_Properties, textvariable=self.IMAGE_SIZE,anchor='w')
        self.IMAGE_SIZE_LABEL.pack()
        self.PRINT_MIN = TK.Label(self.IMG_Properties,textvariable=self.Entries[1],anchor='w')
        self.PRINT_MIN.pack()
        self.PRINT_MIN.bind('<Button-1>',self.Grab_MIN_Value)
        self.PRINT_MAX = TK.Label(self.IMG_Properties,textvariable=self.Entries[2],anchor='w')
        self.PRINT_MAX.pack()
        self.PRINT_MAX.bind('<Button-1>',self.Grab_MAX_Value)
        Y = 110
        self.Add_Label(525,Y,190,text='Color Preset:')
        self.cmap_combobox = TK.ttk.Combobox(self.Wizard, height=30, values=self.Options, state='readonly')
        self.cmap_combobox.place(x=530,y=Y+20,width=250)
        self.cmap_combobox.current(0)
        self.Add_Label(525,Y+50,250,text='Figure Title(한글X):')
        self.Title_Entry = TK.Entry(self.Wizard,textvariable=self.Entries[0])
        self.Title_Entry.place(x=530,y=Y+70,width=250)
        self.Add_Label(525,Y+100,190,text='Color Range:')
        self.Add_Label(525,Y+125,190,text='MIN')
        self.MIN_Entry = TK.Entry(self.Wizard,textvariable=self.Entries[3])
        self.MIN_Entry.place(x=565,y=Y+125,width=215)
        self.Add_Label(525,Y+145,190,text='MAX')
        self.MAX_Entry = TK.Entry(self.Wizard,textvariable=self.Entries[4])
        self.MAX_Entry.place(x=565,y=Y+145,width=215)
        self.f = None
        self.GET_IMAGE()
        self.IMAGE_PREVIEW = TK.Label(self.Wizard,image=self.Figure_TK)
        self.IMAGE_PREVIEW.place(x=10,y=10,width=500,height=500)

        self.Apply_Button = TK.Button(self.Wizard, text='Colormap 생성',command=self.GET_IMAGE)
        self.Apply_Button.place(x=550,y=Y+175, width=200,height=40)
        self.SAVE_Button = TK.Button(self.Wizard, text='Colormap 저장',command=self.Save_as_Image)
        self.SAVE_Button.place(x=525,y=Y+215+125,width=250,height=50)

    def Resize_WINDOW(self,event):
        W, H = self.Wizard.winfo_width(), self.Wizard.winfo_height()
        if self.W==W and self.H==H: return None
        dW, dH = W-800, H-520
        self.W, self.H = W, H
        self.GET_IMAGE(resize_only=True)
        self.IMG_Properties.place_forget()
        for L in range(len(self.LABELs)):
            self.LABELs[L].place_forget()
        self.cmap_combobox.place_forget()
        self.Title_Entry.place_forget()
        self.MIN_Entry.place_forget()
        self.MAX_Entry.place_forget()
        self.IMAGE_PREVIEW.place_forget()
        self.Apply_Button.place_forget()
        self.SAVE_Button.place_forget()
        
        self.IMG_Properties.place(x=525+dW,y=20,width=250)
        self.cmap_combobox.place(x=530+dW,y=110+20,width=250)
        y = [0, 50, 100, 125, 145]
        for L in range(len(self.LABELs)):
            self.LABELs[L].place(x=525+dW, y=110+y[L])
        self.Title_Entry.place(x=530+dW,y=110+70,width=250)
        self.MIN_Entry.place(x=565+dW,y=110+125,width=215)
        self.MAX_Entry.place(x=565+dW,y=110+145,width=215)
        self.Apply_Button.place(x=550+dW,y=110+175, width=200, height=40)
        self.SAVE_Button.place(x=525+dW,y=110+215+125, width=250, height=50)
        self.IMAGE_PREVIEW.place(x=10,y=10, width=500+dW, height=500+dH)

    def Add_Label(self,x,y,width,text=''):
        self.LABELs.append(TK.Label(self.Wizard,text=text,anchor='w'))
        self.LABELs[-1].place(x=x,y=y,width=width)

    def GET_IMAGE(self,resize_only=False):
        if resize_only==False:
            self.THIS = self.IMAGE.COPIED / self.IMAGE.trash_STD
            W,H = self.IMAGE.W0,self.IMAGE.H0
            X,Y = 107,58
            self.Entries[1].set('MIN: %3.10f'%(self.THIS.min()))
            self.Entries[2].set('MAX: %3.10f'%(self.THIS.max()))
            opt = False
            if self.f==None:
                self.f = plt.figure()
                self.VMIN = self.THIS.min()
                self.VMAX = self.THIS.max()
            else:
                try:
                    MIN_VALUE, MAX_VALUE = float(self.MIN_Entry.get()), float(self.MAX_Entry.get())
                    self.VMIN = MIN_VALUE
                    self.VMAX = MAX_VALUE
                    plt.close('all')
                    self.f = plt.figure()
                    opt = True
                except:
                    ERROR('값 오류','올바른 형식의 숫자를 입력해주세요.')
                    return None
            
            plt.imshow(self.THIS,cmap=self.cmap_combobox.get(),vmin=self.VMIN,vmax=self.VMAX)
            plt.colorbar()
            plt.title(self.Title_Entry.get())
            self.f.canvas.draw()
            self.Figure_TK1 = np.array(self.f.canvas.renderer._renderer) #(480, 640, 3)
            self.Figure_TK1 = cv2.cvtColor(self.Figure_TK1, cv2.COLOR_BGRA2BGR)
        
            COLOR = self.Figure_TK1[Y:Y+370, X:X+370] #Colormap 영역 잘라내기
            MASK = self.IMAGE.MASK
            MASK2 = cv2.resize(MASK, (370,370), interpolation=cv2.INTER_AREA)
            GET_PTS = np.where(MASK2==255 )
            COLOR2 = COLOR[GET_PTS]
            COLOR3 = self.IMAGE.Create_RGB_IMAGE(self.IMAGE.COPIED,plz_rtn=True)
            COLOR4 = cv2.resize(COLOR3,(370,370),interpolation=cv2.INTER_AREA)
            COLOR4[GET_PTS] = COLOR2
            self.Figure_TK1[Y:Y+370, X:X+370] = COLOR4
            if self.W!=800 and self.H!=640: self.Figure_TK1 = cv2.resize(self.Figure_TK1,(640+self.W-800, 480+self.H-520) )
            self.Figure_TK2 = Image.fromarray(self.Figure_TK1)
            self.Figure_TK = ImageTk.PhotoImage(self.Figure_TK2)    
            if opt==True: self.IMAGE_PREVIEW.configure(image=self.Figure_TK)
        else:
            self.Figure_TK1_RESIZED = cv2.resize(self.Figure_TK1,(640+self.W-800, 480+self.H-520) )
            self.Figure_TK2 = Image.fromarray(self.Figure_TK1_RESIZED)
            self.Figure_TK = ImageTk.PhotoImage(self.Figure_TK2)    
            self.IMAGE_PREVIEW.configure(image=self.Figure_TK)
        self.IMAGE_SIZE.set('Size: {0} x {1}'.format(640+self.W-800,480+self.H-520))

    def Save_as_Image(self):
        SAVE_fname = filedialog.asksaveasfilename(title='CMAP 저장',filetypes=[('Portable Network Graphics(*.png)','.png')],
                            initialfile=self.Entries[0].get()+'.png')
        if SAVE_fname == '': return None
        else:
            try: self.Figure_TK2.save(SAVE_fname+'.png')
            except: FATAL_ERROR('오류','파일을 저장하는데 실패했습니다!')

    def Grab_MIN_Value(self,event):
        self.Entries[3].set(self.Entries[1].get().split(' ')[-1])
    
    def Grab_MAX_Value(self,event):
        self.Entries[4].set(self.Entries[2].get().split(' ')[-1])

    def destroy(self):
        self.Wizard.destroy()