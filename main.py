import os, cv2, pickle, copy
import data_structure, sub_windows
import nibabel as nib, pydicom
import matplotlib, matplotlib.pyplot as plt
import tkinter as TK
import numpy as np
import PIL, matplotlib
from matplotlib import style
from PIL import Image, ImageTk
from glob import glob
from tkinter import filedialog, messagebox, Menu
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
try: 
    from bruker2nifti.converter import Bruker2Nifti; import bruker2nifti as brk
except: os.system('pip install bruker2nifti')
finally: 
    from bruker2nifti.converter import Bruker2Nifti; import bruker2nifti as brk

__version__ = '2020-07-05'
__TITLE__ = "XNR"

def nothing(x=None): pass

class MAIN_PROGRAM:
    def __init__(self, ROOT):
        self.ROOT = ROOT
        self.WINDOW = TK.Tk()        
        self.TITLE_BAR = 25
        self.IMAGE_BTTN_X, self.IMAGE_BTTN_Y = 670, 455
        self.BTN_HEIGHT,self.BTN_WIDTH = 35, 65
        self.WINDOW.config(bg='#1E1E1E',highlightbackground='white')
        self.My_Screen = [self.WINDOW.winfo_screenwidth(), self.WINDOW.winfo_screenheight()]
        self.WINDOW.geometry('1300x745+{0}+{1}'.format(self.My_Screen[0]//2-1300//2, 0))#self.My_Screen[1]//2-992//2))
        self.WINDOW.resizable(0,0)
        self.WINDOW.title(__TITLE__)    
        self.Variable_Initializer()
        self.TT = 255
        #######UI#######
        self.Canvas_Initializer()
        self.MENU_Initializer()
        self.Graph_Initializer()
        self.intialized=True
        
        #self.BTTN1  = TK.Button(self.WINDOW, text="Marker" ,command=self.BTTN1_Command, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN2  = TK.Button(self.WINDOW, text="ROI 자유형",command=lambda: self.BTTN_Command(_mode=2), state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN3  = TK.Button(self.WINDOW, text="ROI 다각형",command=lambda: self.BTTN_Command(_mode=3), state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN4  = TK.Button(self.WINDOW, text="ROI 사각형",command=lambda: self.BTTN_Command(_mode=4), state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN5  = TK.Button(self.WINDOW, text="ROI 원  형",command=lambda: self.BTTN_Command(_mode=5), state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN6  = TK.Button(self.WINDOW, text="ROI 편  집",command=lambda: self.BTTN_Command(_mode=6), state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        #self.BTTN7  = TK.Button(self.WINDOW, text="ROI AUTO",command=self.BTTN7_Command, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN8  = TK.Button(self.WINDOW, text="ROI 열  기",command=self.BTTN8_Command, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN9  = TK.Button(self.WINDOW, text="ROI 저  장",command=self.BTTN9_Command, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN10 = TK.Button(self.WINDOW, text="ROI 초기화",command=self.BTTN10_Command, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        
        #self.BTTN1.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*0),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN2.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*1),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN3.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*2),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN4.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*3),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN5.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*4),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN6.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*5),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        #self.BTTN7.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*5),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN8.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*6),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN9.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*7),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        
        self.BTTN10.place(x=self.IMAGE_BTTN_X+(self.BTN_WIDTH*8),y=self.IMAGE_BTTN_Y+self.TITLE_BAR,width=self.BTN_WIDTH,height=self.BTN_HEIGHT)        

        self.OPTION_FRAME1 = TK.LabelFrame(self.WINDOW, text="ROI Type", bg='#1E1E1E', fg='#FFFFFF')
        self.OPTION_FRAME1.place(x=670, y=self.TITLE_BAR+460+self.BTN_HEIGHT, width=200, height=198) #540+TITLE_BAR
        self.ROI_TYPE_BTTN1 = TK.Radiobutton(self.OPTION_FRAME1, text='Background' , value=1, variable=self.ROI_TYPE_Var, command=None, state='disabled', bg='#1E1E1E', fg='#FFFFFF',selectcolor='#1E1E1E')
        self.ROI_TYPE_BTTN1.place(x=10, y=15)
        self.ROI_TYPE_BTTN2 = TK.Radiobutton(self.OPTION_FRAME1, text='Reference'  , value=2, variable=self.ROI_TYPE_Var, command=None, state='disabled', bg='#1E1E1E', fg='#FFFFFF',selectcolor='#1E1E1E')
        self.ROI_TYPE_BTTN2.place(x=10, y=55)            
        self.ROI_TYPE_BTTN3 = TK.Radiobutton(self.OPTION_FRAME1, text='Material'   , value=3, variable=self.ROI_TYPE_Var, command=None, state='disabled', bg='#1E1E1E', fg='#FFFFFF',selectcolor='#1E1E1E')
        self.ROI_TYPE_BTTN3.place(x=10, y=95)

        self.OPTION_FRAME2 = TK.LabelFrame(self.WINDOW, text="Value Display", bg='#1E1E1E', fg='#FFFFFF')
        self.OPTION_FRAME2.place(x=880, y=self.TITLE_BAR+460+self.BTN_HEIGHT, width=200, height=198)
        self.MAP_SELECT_BTTN1 = TK.Radiobutton(self.OPTION_FRAME2, text='RAW Intensity', value=0, variable=self.IMG_Mode, command=self.DISPLAY_GRAPH, state='disabled', bg='#1E1E1E', fg='#FFFFFF',selectcolor='#1E1E1E')
        self.MAP_SELECT_BTTN1.place(x=10, y=15)
        self.MAP_SELECT_BTTN2 = TK.Radiobutton(self.OPTION_FRAME2, text='SNR'          , value=1, variable=self.IMG_Mode, command=self.DISPLAY_GRAPH, state='disabled', bg='#1E1E1E', fg='#FFFFFF',selectcolor='#1E1E1E')
        self.MAP_SELECT_BTTN2.place(x=10, y=55)            
        self.MAP_SELECT_BTTN3 = TK.Radiobutton(self.OPTION_FRAME2, text='CNR'          , value=2, variable=self.IMG_Mode, command=self.DISPLAY_GRAPH, state='disabled', bg='#1E1E1E', fg='#FFFFFF',selectcolor='#1E1E1E')
        self.MAP_SELECT_BTTN3.place(x=10, y=95)

        self.VALUE_SELECT = TK.Checkbutton(self.OPTION_FRAME2, text="Standard Deviation", command=lambda: self.DISPLAY_GRAPH(toggle=True), state='disabled', 
                                                                variable=self.STD_VIEW, bg='#1E1E1E', fg='#FFFFFF',selectcolor='#1E1E1E')
        self.VALUE_SELECT.place(x=10,y=135,width=180,height=30)      

        self.OPTION_FRAME3 = TK.LabelFrame(self.WINDOW, text="Function Set #2", bg='#1E1E1E', fg='#FFFFFF')
        self.OPTION_FRAME3.place(x=1090, y=self.TITLE_BAR+460+self.BTN_HEIGHT, width=200, height=198)
        self.BTTN11 = TK.Button(self.OPTION_FRAME3, text="SNR map", command=self.BTTN11_Command, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN12 = TK.Button(self.OPTION_FRAME3, text="CNR map", command=self.BTTN12_Command, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN13 = TK.Button(self.OPTION_FRAME3, text="RAW Signal map", command=self.BTTN13_Command, state='disabled', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.BTTN14 = TK.Button(self.OPTION_FRAME3, text="FILE List", command=self.BTTN14_Command, state='normal', bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')

        self.BTTN11.place(x=10,y=15,width=180,height=30)        
        self.BTTN12.place(x=10,y=55,width=180,height=30)        
        self.BTTN13.place(x=10,y=95,width=180,height=30)        
        self.BTTN14.place(x=10,y=135,width=180,height=30)        
        
        self.CWD = TK.Label(self.WINDOW, bd=1, relief='sunken', anchor='w', textvariable=self.Current_Working_File, bg='#007ACD', fg='#FFFFFF')
        self.CWD.place(x=0,y=700+self.TITLE_BAR,width=1090)
        
        self.CUR_MOUSE_POS = TK.Label(self.WINDOW, bd=1, relief='sunken', anchor='e', textvariable=self.Location, bg='#007ACD', fg='#FFFFFF')
        self.CUR_MOUSE_POS.place(x=1090+0,y=700+self.TITLE_BAR,width=210)
        self.WINDOW.protocol('WM_DELETE_WINDOW',self.GOODBYE)
        self.WINDOW.mainloop()

    def GOODBYE(self):  
        if ( messagebox.askyesno('종료','프로그램을 정말 종료하시겠습니까?') ): 
            for temp in glob(self.ROOT+'/temp/*nptmp.npy'): os.remove(temp)
            self.WINDOW.quit()

    def Variable_Initializer(self):
        self.MOUSE_MODE = 0 #0: Nothing, 1: Point, 2: ROI_Free_shape, 3: ROI_Poly, 4: ROI_Rect, 5: Circle
        self.Drawing, self.MOUSE_IN = False, False
        self.IMG_X, self.IMG_Y = 0, 0
        self.Canvas_X, self.Canvas_Y = 0, 0
        self.Marker_Intensities = None
        self.ROI_LIST = []; self.COPIED = None
        self.ROI_Selected = -1
        self.ROI_MOVING = False
        self.IMG_Mode = TK.IntVar()
        self.LINES, self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], [], []
        self.CONTROL_POINTS = []
        self.Edit_CP, self.CP = False ,None
        self.ROI_TYPE_Var = TK.IntVar(); self.ROI_TYPE_Var.set(3) ;self.Outlines = {1:'red', 2:'blue', 3:'green'}
        self.Location = TK.StringVar(); self.Location.set("(0, 0)")
        self.Current_Working_File = TK.StringVar(); self.Current_Working_File.set("Nothing")
        self.Status = TK.StringVar(); self.Status.set("IDLE")
        self.FILE_LIST_WINDOW = False
        self.Current_File = TK.IntVar(); self.Current_File.set(0)
        self.Total_File = TK.IntVar(); self.Total_File.set(0)
        self.IMAGEs = None
        self.WHOLE_LIST = []
        self.intialized=False
        self.STD_VIEW = TK.IntVar()

    def Canvas_Initializer(self):
        self.DICOM_CANVAS = TK.Canvas(self.WINDOW, width=650, height=650, bg='black',cursor='crosshair')
        self.DICOM_CANVAS.place(x=10,y=10+self.TITLE_BAR, width=650,height=650)
        self.DICOM_IMAGE = self.DICOM_CANVAS.create_image(0,0,anchor=TK.NW, image=ImageTk.PhotoImage(Image.fromarray(np.zeros([650,650]))))

    def Graph_Initializer(self):
        self.SI_FRAME = TK.Frame(self.WINDOW)
        self.SI_FRAME.place(x=670,y=10+self.TITLE_BAR,width=620,height=400)
        self.SI_FIG = plt.figure(0,figsize=(15,15))
        self.SI_FIG.suptitle("Welcome to {0}".format(__TITLE__))

        self.SI_AX = self.SI_FIG.add_subplot(111)
        self.SI_AX.set_title("Intensity Monitor"); plt.grid(b=None)
        self.SI_AX.bar(['a','b','c','d'],[1,2,3,4]); 
        self.SI_CANVAS = FigureCanvasTkAgg(self.SI_FIG, master=self.SI_FRAME)
        self.SI_CANVAS.get_tk_widget().pack(fill='both')
        self.SI_CANVAS.draw()
        toolbarFrame = TK.Frame(master=self.WINDOW)
        toolbarFrame.place(x=670,y=410+self.TITLE_BAR,width=620)
        toolbar = NavigationToolbar2Tk(self.SI_CANVAS, toolbarFrame)

    def MENU_Initializer(self):
        self.MENU1 = TK.Button(self.WINDOW, text="파일",command=self.MENU_FILE_POPUP , bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.MENU1.place(x=10,y=10,width=50,height=20)

        self.STATUS = TK.Label(self.WINDOW, bd=1, relief='sunken', anchor='w', textvariable=self.Status, bg='#007ACD', fg='#FFFFFF')
        self.STATUS.place(x=70,y=10,width=950)

        self.MENU1.bind('<Any-Enter>',lambda x: self.MENU1.config(bg='#094771')); self.MENU1.bind('<Any-Leave>',lambda x: self.MENU1.config(bg='#3C3C3C'))
        self.MENU_FILE = Menu(self.WINDOW, tearoff=0)
        self.MENU_FILE.add_command(label="DICOM  열기", command=self.FILE_OPEN_DICOMS)
        self.MENU_FILE.add_command(label="NiFTI  열기", command=self.FILE_OPEN_NIFTI)
        self.MENU_FILE.add_separator()
        self.MENU_FILE.add_command(label="BRUKER 변환", command=self.FILE_OPEN_BRUKER)
        self.MENU_FILE.add_separator()
        self.MENU_FILE.add_command(label="종료",command=self.GOODBYE)

        self.MENU3 = TK.Button(self.WINDOW, text="?",command=self.About_Program , bg='#3C3C3C', fg='#FFFFFF', activebackground='#094771', highlightcolor='#094771')
        self.MENU3.place(x=1260,y=10,width=30,height=20)
        self.MENU3.bind('<Any-Enter>',lambda x: self.MENU3.config(bg='#094771')); self.MENU3.bind('<Any-Leave>',lambda x: self.MENU3.config(bg='#3C3C3C'))

        self.RIGHT_CLK_MENU =  Menu(self.DICOM_CANVAS, tearoff = 0)
        self.RIGHT_CLK_MENU.add_command(label='====={0}====='.format(__TITLE__), command=nothing, state='disabled')
        self.RIGHT_CLK_MENU.add_separator()
        self.RIGHT_CLK_MENU.add_command(label="ROI 삭제", command=self.Remove_ROI, state='disabled')
        self.RIGHT_CLK_MENU.add_separator()
        self.RIGHT_CLK_MENU.add_command(label="Set as reference",  command=lambda: self.Set_ROI_As(to=2), state='disabled')
        self.RIGHT_CLK_MENU.add_command(label="Set as material",   command=lambda: self.Set_ROI_As(to=3), state='disabled')
        self.RIGHT_CLK_MENU.add_command(label="Set as background", command=lambda: self.Set_ROI_As(to=1), state='disabled')

    def BIND_Initializer(self):
        self.DICOM_CANVAS.bind('<Motion>',self.MOUSE_MOTION_HANDLER)
        self.DICOM_CANVAS.bind('<Button-1>',self.MOUSE_B1_CLICK_HANDLER)
        self.DICOM_CANVAS.bind('<Button-3>',self.MOUSE_B3_CLICK_HANDLER)
        self.DICOM_CANVAS.bind('<B1-Motion>',self.MOUSE_B1_DRAG_HANDLER)
        self.DICOM_CANVAS.bind('<ButtonRelease-1>',self.MOUSE_B1_RELEASE_HANDLER)
        #self.BTTN1.bind('<Button-3>',lambda x: self.SI_MARKER_PROCESSING(remove=True))

    def MENU_FILE_POPUP(self):
        self.MENU_FILE.tk_popup(self.WINDOW.winfo_x()+63, self.WINDOW.winfo_y()+70, 0)
        self.MENU_FILE.grab_release()

    def FILE_OPEN_DICOMS(self, override=None, override2=[]):
        if len(override2)==0:
            if override is None: FILE_LIST = filedialog.askopenfilenames(initialdir=os.getcwd(),title='DICOM 파일 열기')
            else: FILE_LIST = [override]
            FILE_LIST = sorted(FILE_LIST)
        else: FILE_LIST = sorted(override2, key=lambda x: int(x.split('_')[-1].split('.')[0]))
        if len(FILE_LIST)!=0:
            plt.figure(0)
            TRY = data_structure.IMAGES(); TRY.DICOM_IMPORTER(FILE_LIST[0])
            if len(FILE_LIST)>1 and self.FILE_LIST_WINDOW==False:
                self.BTTN14_Command(); self.FILE_LIST_WINDOW=True
                
            os.chdir(os.path.dirname(FILE_LIST[0]))
            self.Current_File.set(0); self.Total_File.set(0)
            self.IMAGEs = TRY; self.FILE_OPENED()
            if override is None:
                for FILE in FILE_LIST:
                    if self.FILE_LIST_WINDOW: self.WHOLE_LIST = self.LIST_WINDOW.Add_List(FILE)
                    else: self.WHOLE_LIST.append(FILE)

    def FILE_OPEN_NIFTI(self):
        PATH = filedialog.askopenfilename(initialdir=os.getcwd(),title='NiFTI 파일 열기')
        if PATH!='':
            PATH = PATH.replace('\\','/')
            READ = nib.load(PATH).get_fdata()
            if len(READ.shape)!=3:
                print(READ.shape)
                messagebox.showerror('ERROR','Single volume만 지원합니다!')
            else: 
                os.chdir(os.path.dirname(PATH))
                self.Current_File.set(0); self.Total_File.set(0)
                LIST = []
                ROOT = self.ROOT+'/temp'
                for i in range(READ.shape[-1]): 
                    np.save(ROOT+'/'+PATH.split('/')[-1]+f'_{i}.nptmp', np.rot90( READ[:,:,i] ))
                    LIST.append(ROOT+'/'+PATH.split('/')[-1]+f'_{i}.nptmp.npy')
                self.FILE_OPEN_DICOMS(override2=LIST)

    def FILE_OPEN_BRUKER(self):
        print('Warning! Experimental trial!')
        FOLDER = filedialog.askdirectory(title='변환활 bruker 폴더 경로를 지정하세요.', initialdir=os.getcwd())
        if FOLDER=='' : return None
        os.chdir(FOLDER)
        FOLDER2 = filedialog.askdirectory(title='Output 폴더 경로를 지정하세요.', initialdir=os.getcwd())
        os.chdir(FOLDER2)
        if FOLDER2=='': return None
        try: 
            self.FILE_OPEN_BRUKER_CHILD(FOLDER, FOLDER2)
            messagebox.showinfo('변환 완료', f'{FOLDER2}에 NifTI 파일로 변환이 완료되었습니다!')
            return None
        except OSError: messagebox.showerror('ERROR',f'파일 변환 실패! Bruker경로를 다시 확인하세요.\n{FOLDER}')

    def FILE_OPEN_BRUKER_CHILD(self, FOLDER, FOLDER2):
        bru = Bruker2Nifti(FOLDER, FOLDER2)
        bru.verbose = 2; bru.correct_slope = False; bru.get_acqp = False; bru.get_method = False; bru.get_reco = False
        bru.nifti_version = 1; bru.qform_code = 1; bru.sform_code = 2; bru.save_human_readable = True; bru.save_b0_if_dwi = True
        bru.convert()
                
    def FILE_OPENED(self):
        self.BIND_Initializer()
        self.IMAGEs.Convert_DISPLAY()
        self.Select_Image(Index=self.Current_File.get())
        for i in range(len(self.ROI_LIST)):
            self.ROI_LIST[i].HEIGHT, self.ROI_LIST[i].WIDTH = self.IMAGEs.IMGs.shape[:2]
            self.ROI_LIST[i].MASK = np.zeros((self.ROI_LIST[i].HEIGHT, self.ROI_LIST[i].WIDTH)).astype(np.uint8)
            self.ROI_LIST[i].Make_ROI(self.ROI_LIST[i].ROI_TYPE,self.ROI_LIST[i].ROI_X, self.ROI_LIST[i].ROI_Y, self.ROI_LIST[i].ROI_for_TK, self.ROI_LIST[i].TK_INDEX)
        self.DISPLAY_GRAPH()
        if self.MOUSE_MODE==6: self.Set_Mouse_Mode()
        self.ROI_TYPE_BTTN1.config(state='normal')
        self.ROI_TYPE_BTTN2.config(state='normal')
        self.ROI_TYPE_BTTN3.config(state='normal')
        #self.BTTN1.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #SI_Marker
        self.BTTN2.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_FREE
        self.BTTN3.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_POLY
        self.BTTN4.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_CIRCLE
        self.BTTN5.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_RECT
        self.BTTN6.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_EDIT
        self.BTTN8.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_OPEN
        self.BTTN13.config( state='normal', relief=TK.RAISED, bg='#3C3C3C')
        
    def Select_Image(self, Index):
        self.DICOM_CANVAS.itemconfig(self.DICOM_IMAGE, image=self.IMAGEs.IMGs_Display[Index])
        if self.IMAGEs.FILE_TYPE=='DICOM': self.Current_Working_File.set(self.IMAGEs.FILE_PATH[self.Current_File.get()])
        elif self.IMAGEs.FILE_TYPE=='NIFTI': self.Current_Working_File.set(self.IMAGEs.FILE_PATH[0])
    
    def Set_Mouse_Mode(self,mode=0):
        self.MOUSE_MODE = mode if self.MOUSE_MODE!=mode else 0
        #self.BTTN1.config(relief=TK.SUNKEN if self.MOUSE_MODE==1 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==1 else '#3C3C3C')
        self.BTTN2.config(relief=TK.SUNKEN if self.MOUSE_MODE==2 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==2 else '#3C3C3C') #ROI_FREE
        self.BTTN3.config(relief=TK.SUNKEN if self.MOUSE_MODE==3 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==3 else '#3C3C3C') #ROI_POLY
        self.BTTN4.config(relief=TK.SUNKEN if self.MOUSE_MODE==4 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==4 else '#3C3C3C') #ROI_CIRCLE
        self.BTTN5.config(relief=TK.SUNKEN if self.MOUSE_MODE==5 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==5 else '#3C3C3C') #ROI_RECT
        self.BTTN6.config(relief=TK.SUNKEN if self.MOUSE_MODE==6 else TK.RAISED, bg='#094771' if self.MOUSE_MODE==6 else '#3C3C3C') #ROI_MOVE 

    def BTTN1_Command(self):
        print('WTF')
        ##from matplotlib.widgets import PolygonSelector
        #self.TT+=2
        #fig = plt.figure(self.TT)
        #ax = fig.add_subplot(111)
        #plt.ion()
        #plt.show()
        ##self.ps = PolygonSelector(ax, self.on_select)

    def BTTN_Command(self, _mode):      #BUTTON 2~6
        self.CURRENT_LINE = None
        self.Set_Mouse_Mode(mode=_mode)
        self.Remove_Control_Point()
        if self.Drawing==True:
            self.Drawing = False
            self.DICOM_CANVAS.delete(*self.LINES); self.DICOM_CANVAS.delete(self.END_POINT)
            del(self.ROI_LIST[-1])
        self.LINES, self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], [], []
        self.DISPLAY_GRAPH()

    def BTTN7_Command(self):
        self.Threshold_Settings = sub_windows.Thresholder(self,self.IMAGEs.IMGs[:,:,self.Current_File.get()])
        self.WINDOW.wait_window(self.Threshold_Settings.MAIN)
            
    def BTTN8_Command(self):
        FILE = filedialog.askopenfilename(initialdir=os.getcwd(), title='ROI 열기',filetypes=[("ROI files","*.roi")])
        if FILE!='':
            os.chdir(os.path.dirname(FILE))
            with open(FILE,"rb") as f: DATA = pickle.load(f)
            if (True if len(self.ROI_LIST)==0 else messagebox.askyesno('주의!','기존 ROI는 제거됩니다.\n계속하시겠습니까?')):
                self.ROI_Selected=-1; self.Remove_ROI()
                for idx in range(len(DATA)):
                    THIS = DATA[idx] #ROI_X, ROI_Y, ROI_TK, ROI_Shape, ROI_TYPE
                    self.ROI_LIST.append(data_structure.ROI(self.IMAGEs.IMGs.shape[:2], type_src=THIS[-1]))
                    
                    if THIS[3]=='ROI_CIRCLE': self.CURRENT_LINE = self.DICOM_CANVAS.create_oval(   *THIS[2],fill='',width=2,outline=self.Outlines[THIS[-1]])
                    else:                     self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(*THIS[2],fill='',width=2,outline=self.Outlines[THIS[-1]])  
                    self.ROI_LIST[-1].Make_ROI(THIS[3],np.array(THIS[0]), np.array(THIS[1]), np.array(THIS[2]), self.CURRENT_LINE)
                    self.BTTN9.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_SAVE
                    self.BTTN10.config( state='normal', relief=TK.RAISED, bg='#3C3C3C') #ROI_CLEAR
                GO = 0
                for i in range(len(self.ROI_LIST)):
                    if self.ROI_LIST[i].ROI_TYPE_src == 1: GO = 1
            
            self.BTTN11.config(state= 'disabled' if GO==0 else 'normal')
            self.BTTN12.config(state= 'disabled' if GO==0 else 'normal')
            self.MAP_SELECT_BTTN2.config(state= 'disabled' if GO==0 else 'normal')
            self.MAP_SELECT_BTTN3.config(state= 'disabled' if GO==0 else 'normal')
            self.VALUE_SELECT.config(state= 'disabled' if GO==0 else 'normal')
            self.DISPLAY_GRAPH()

    def BTTN9_Command(self): #ROI SAVE
        if len(self.ROI_LIST)!=0:
            FILE = filedialog.asksaveasfilename(initialdir=os.getcwd(), title='ROI 저장',initialfile='ROI.roi',filetypes=[("ROI files","*.roi")])
            if FILE!='':
                os.chdir(os.path.dirname(FILE))
                DATA = []
                for idx in range(len(self.ROI_LIST)): DATA.append(self.ROI_LIST[idx].SAVE_ROI())
                with open(FILE,'wb') as f: pickle.dump(DATA, f)

    def BTTN10_Command(self): #ROI_REMOVE
        if messagebox.askyesno('주의!','ROI가 모두 제거됩니다.\n계속하시겠습니까?'):
            self.ROI_Selected=-1; self.Remove_ROI()
            self.DISPLAY_GRAPH()

    def BTTN11_Command(self): #BUILD SNR MAP
        self.Build_SNR_MAP()
        self.TT+=2
        sub_windows.MAP_VIEWER(self.WINDOW, self.SNR_MAP, fig_index=self.TT, win_title=self.Current_Working_File.get(), title='SNR map')

    def BTTN12_Command(self): #BUILD CNR MAP
        self.TT+=2
        self.Build_SNR_MAP()
        self.Ref = []
        for i in range(len(self.ROI_LIST)):
            if self.ROI_LIST[i].ROI_TYPE_src == 2:
                Ref = self.SNR_MAP[:,:]
                self.Ref.extend(Ref[np.where(self.ROI_LIST[i].MASK!=0)])
                break
        self.CNR_MAP = self.SNR_MAP - np.array(self.Ref).mean()
        sub_windows.MAP_VIEWER(self.WINDOW, self.CNR_MAP, fig_index=self.TT, win_title=self.Current_Working_File.get(), title='CNR map')

    def BTTN13_Command(self): 
        self.TT+=2
        sub_windows.MAP_VIEWER(self.WINDOW, self.IMAGEs.IMGs, fig_index=self.TT, win_title=self.Current_Working_File.get(), title='Raw intensity map')

    def BTTN14_Command(self):
        if self.FILE_LIST_WINDOW==False:
            self.LIST_WINDOW = sub_windows.LIST_VIEWER(master=self)
            self.FILE_LIST_WINDOW = True
            for i in range(len(self.WHOLE_LIST)):
                self.LIST_WINDOW.Add_List(self.WHOLE_LIST[i])

    def Build_SNR_MAP(self):
        self.BACKGROUND = []
        for i in range(len(self.ROI_LIST)):
            if self.ROI_LIST[i].ROI_TYPE_src == 1:
                BCK = self.IMAGEs.IMGs[:,:,self.Current_File.get()]
                self.BACKGROUND.extend(BCK[np.where(self.ROI_LIST[i].MASK!=0)])
        self.SNR_MAP = self.IMAGEs.IMGs[:,:,0].copy() / ( np.array(self.BACKGROUND).std() if len(self.BACKGROUND)!=0 else self.IMAGEs.IMGs[:,:,self.Current_File.get()].std() )

    def GET_IMAGE_POSITION(self, x, y):
        O_size = self.IMAGEs.IMGs.shape[:2]
        return int(x / 650 * O_size[0]), int(y / 650 * O_size[1])
    
    def MOUSE_MOTION_HANDLER(self,event):
        self.Canvas_X, self.Canvas_Y = event.x, event.y
        self.IMG_X, self.IMG_Y = self.GET_IMAGE_POSITION(event.x, event.y)
        self.Location.set('( %3d, %3d ), %3.2f'%(self.IMG_X, self.IMG_Y,self.IMAGEs.IMGs[self.IMG_Y, self.IMG_X,self.Current_File.get()]))
        if self.MOUSE_MODE==3: #ROI_Poly
            if self.Drawing==True:
                self.DICOM_CANVAS.coords(self.LINES[-1], *self.START_POINT, self.Canvas_X, self.Canvas_Y)
                THIS = self.DICOM_CANVAS.find_enclosed(self.Canvas_X-8,self.Canvas_Y-8,self.Canvas_X+8,self.Canvas_Y+8)
                if len(THIS)!=0 and THIS[0]==self.END_POINT: self.MOUSE_IN = True
                else: self.MOUSE_IN = False 
        elif self.MOUSE_MODE==6: #ROI_EDIT
            if self.ROI_Selected!=-1:
                try:
                    TEMP = self.DICOM_CANVAS.find_enclosed(self.Canvas_X-10,self.Canvas_Y-10, self.Canvas_X+10, self.Canvas_Y+10)
                    if TEMP[0] in self.CONTROL_POINTS: 
                        self.DICOM_CANVAS.config(cursor='hand1')
                        self.Edit_CP = TEMP[0]
                        self.CP = self.CONTROL_POINTS.index(self.Edit_CP)
                        return None
                except: self.Edit_CP, self.CP = False, None
            if self.Drawing==False and self.ROI_MOVING==False:
                for idx in range(len(self.ROI_LIST)):
                    if self.ROI_LIST[idx].MASK[self.IMG_Y][self.IMG_X]==1:
                        self.DICOM_CANVAS.config(cursor='hand2')
                        self.ROI_Selected = idx
                        return None
                self.ROI_Selected = -1
                self.DICOM_CANVAS.config(cursor='crosshair')
                    
    def MOUSE_B1_CLICK_HANDLER(self, event):
        self.Canvas_X, self.Canvas_Y = event.x, event.y
        self.IMG_X, self.IMG_Y = self.GET_IMAGE_POSITION(event.x, event.y)
        if   self.MOUSE_MODE==1: self.SI_MARKER_PROCESSING() #1: Point
        elif self.MOUSE_MODE>1 and self.MOUSE_MODE<6:
            if self.MOUSE_MODE!=3: #Not ROI_Poly
                self.ROI_LIST.append(data_structure.ROI(self.IMAGEs.IMGs.shape[:2], type_src=self.ROI_TYPE_Var.get()))
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.Drawing = True
                if self.MOUSE_MODE==2: #2: ROI_Free_shape
                    self.LINES, self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], [], []
                    self.LINES.append( self.DICOM_CANVAS.create_polygon(self.Canvas_X,self.Canvas_Y,fill='',width=2,outline='yellow') )
                    self.ROI_POINTS.extend([self.Canvas_X,self.Canvas_Y]); self.ROI_POINTS_X.append(self.Canvas_X); self.ROI_POINTS_Y.append(self.Canvas_Y)
                elif self.MOUSE_MODE==4: #4: ROI_Rect
                    self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(self.Canvas_X,self.Canvas_Y,self.Canvas_X,self.Canvas_Y+1,self.Canvas_X+1, self.Canvas_Y+1,self.Canvas_X+1,self.Canvas_Y,fill='',width=2,outline='yellow')                                                                
                elif self.MOUSE_MODE==5: #5: Circle
                    self.CURRENT_LINE = self.DICOM_CANVAS.create_oval(self.Canvas_X,self.Canvas_Y,self.Canvas_X+1,self.Canvas_Y+1,fill='',width=2,outline='yellow')
            elif self.MOUSE_MODE==3: #ROI_Poly
                if self.MOUSE_IN==True: return None
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                if self.Drawing==False:
                    self.ROI_LIST.append(data_structure.ROI(self.IMAGEs.IMGs.shape[:2], type_src=self.ROI_TYPE_Var.get()))
                    self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], []
                    self.END_POINT = self.DICOM_CANVAS.create_oval(self.Canvas_X-3,self.Canvas_Y-3,self.Canvas_X+3, self.Canvas_Y+3, fill='white',width=2,outline='yellow')
                    self.Drawing = True
                self.ROI_POINTS.extend([self.Canvas_X,self.Canvas_Y]); self.ROI_POINTS_X.append(self.Canvas_X); self.ROI_POINTS_Y.append(self.Canvas_Y)
                self.LINES.append( self.DICOM_CANVAS.create_polygon(*self.START_POINT,self.Canvas_X+1,self.Canvas_Y+1, width=2,outline='yellow') )
        elif self.MOUSE_MODE==6: #6: ROI_EDIT
            self.Remove_Control_Point()
            self.START_POINT = (self.Canvas_X, self.Canvas_Y)
            if self.ROI_Selected!=-1: 
                self.Draw_Control_Point(self.ROI_Selected)
                self.Status.set("ROI #{} selected".format(self.ROI_Selected+1))
            else: 
                self.Edit_CP, self.CP = False, None
                self.Status.set("IDLE")
        else: pass

    def MOUSE_B1_DRAG_HANDLER(self, event):
        self.Canvas_X, self.Canvas_Y = event.x, event.y
        if self.MOUSE_MODE>1 and self.MOUSE_MODE<6:
            if self.MOUSE_MODE==2: #2: ROI_Free_shape
                self.LINES.append( self.DICOM_CANVAS.create_polygon(self.Canvas_X,self.Canvas_Y,fill='',width=2,outline='yellow') )
                self.ROI_POINTS.extend([self.Canvas_X,self.Canvas_Y]); self.ROI_POINTS_X.append(self.Canvas_X); self.ROI_POINTS_Y.append(self.Canvas_Y)
            elif self.MOUSE_MODE==4: #4: ROI_Rect
                self.DICOM_CANVAS.coords(self.CURRENT_LINE,*self.START_POINT, self.START_POINT[0], self.Canvas_Y, self.Canvas_X, self.Canvas_Y, self.Canvas_X, self.START_POINT[1])                                                                           
            elif self.MOUSE_MODE==5: #5: Circle
                self.DICOM_CANVAS.coords(self.CURRENT_LINE,*self.START_POINT,self.Canvas_X, self.Canvas_Y)
        elif self.MOUSE_MODE==6: #6: ROI_EDIT
            if self.Edit_CP:
                dx, dy = self.Canvas_X - self.START_POINT[0], self.Canvas_Y - self.START_POINT[1]
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.ROI_LIST[self.ROI_Selected].EDIT_ROI(self.CP, dx, dy)
                self.DICOM_CANVAS.coords(self.Edit_CP,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].TK_INDEX,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.Draw_Control_Point(self.ROI_Selected)
            elif self.ROI_Selected!=-1:
                self.ROI_MOVING = True
                dx, dy = self.Canvas_X - self.START_POINT[0], self.Canvas_Y - self.START_POINT[1]
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.ROI_LIST[self.ROI_Selected].MOVE_ROI(dx,dy,False)
                self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].TK_INDEX,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.Draw_Control_Point(self.ROI_Selected)
        else: pass

    def MOUSE_B1_RELEASE_HANDLER(self, event):
        self.Canvas_X, self.Canvas_Y = event.x, event.y
        if self.MOUSE_MODE>1 and self.MOUSE_MODE<6:
            if   self.MOUSE_MODE==2: #2: ROI_Free_shape
                self.DICOM_CANVAS.delete(*self.LINES)
                self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(*self.ROI_POINTS,fill='',width=2,outline=self.Outlines[self.ROI_TYPE_Var.get()])
                self.ROI_LIST[-1].Make_ROI('ROI_FREE',np.array(self.ROI_POINTS_X), np.array(self.ROI_POINTS_Y), self.ROI_POINTS, self.CURRENT_LINE)
                self.DISPLAY_GRAPH()
                self.Drawing = False
            elif self.MOUSE_MODE==3: #3: ROI_Poly
                if self.MOUSE_IN==True:
                    self.DICOM_CANVAS.delete(self.END_POINT); self.DICOM_CANVAS.delete(*self.LINES)
                    self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(*self.ROI_POINTS, *self.ROI_POINTS[:2], fill='',width=2,outline=self.Outlines[self.ROI_TYPE_Var.get()])
                    self.Drawing,self.MOUSE_IN = False, False
                    self.ROI_LIST[-1].Make_ROI('ROI_POLY',np.array(self.ROI_POINTS_X), np.array(self.ROI_POINTS_Y), self.ROI_POINTS, self.CURRENT_LINE)
                    self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs)
                    self.DISPLAY_GRAPH()
                else: return None
            elif self.MOUSE_MODE==4: #4: ROI_Rect
                X,Y, X2,Y2  = self.START_POINT[0], self.START_POINT[1], self.Canvas_X, self.Canvas_Y
                ROI_X, ROI_Y = np.array([X,X,X2,X2]), np.array([Y,Y2,Y2,Y])
                ROI_POINTS = np.array([X,Y,X,Y2,X2,Y2,X2,Y])
                self.Drawing = False
                if abs(X-X2)>3 and abs(Y-Y2)>3:
                    self.DICOM_CANVAS.itemconfig(self.CURRENT_LINE,width=2,outline=self.Outlines[self.ROI_TYPE_Var.get()])
                    self.ROI_LIST[-1].Make_ROI('ROI_RECT',ROI_X, ROI_Y, ROI_POINTS, self.CURRENT_LINE)
                    self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs)
                    self.DISPLAY_GRAPH()
                else:
                    self.DICOM_CANVAS.delete(self.CURRENT_LINE)
                    del(self.ROI_LIST[-1])
            elif self.MOUSE_MODE==5: #5: Circle
                X,Y,X2,Y2 = self.START_POINT[0], self.START_POINT[1], self.Canvas_X, self.Canvas_Y
                ROI_X, ROI_Y = np.array([X,X2]), np.array([Y,Y2])
                ROI_POINTS = np.array([X,Y,X2,Y2])
                self.Drawing = False
                if abs(X-X2)>3 and abs(Y-Y2)>3:
                    self.DICOM_CANVAS.itemconfig(self.CURRENT_LINE,width=2,outline=self.Outlines[self.ROI_TYPE_Var.get()])
                    self.ROI_LIST[-1].Make_ROI('ROI_CIRCLE',ROI_X, ROI_Y, ROI_POINTS, self.CURRENT_LINE)
                    self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs)
                    self.DISPLAY_GRAPH()
                else:
                    self.DICOM_CANVAS.delete(self.CURRENT_LINE)
                    del(self.ROI_LIST[-1])
        elif self.MOUSE_MODE==6: #6: ROI_EDIT
            if self.Edit_CP:
                dx, dy = self.Canvas_X - self.START_POINT[0], self.Canvas_Y - self.START_POINT[1]
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.ROI_LIST[self.ROI_Selected].EDIT_ROI(self.CP, dx, dy, True)
                self.DICOM_CANVAS.coords(self.Edit_CP,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].TK_INDEX,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.Draw_Control_Point(self.ROI_Selected)
                self.Edit_CP, self.CP = False, None
                self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs)
            elif self.ROI_MOVING==True:
                dx, dy = self.Canvas_X - self.START_POINT[0], self.Canvas_Y - self.START_POINT[1]
                self.START_POINT = (self.Canvas_X, self.Canvas_Y)
                self.ROI_LIST[self.ROI_Selected].MOVE_ROI(dx,dy,True)
                self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].TK_INDEX,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
                self.ROI_MOVING=False
                self.ROI_LIST[-1].Measure_ROI(self.IMAGEs.IMGs)
                self.ROI_Selected = -1
            self.DISPLAY_GRAPH(index=self.ROI_Selected)
        else: pass
        self.LINES, self.ROI_POINTS, self.ROI_POINTS_X, self.ROI_POINTS_Y = [], [], [], []
        self.CURRENT_LINE = None
        self.MAP_SELECT_BTTN1.config(state= 'normal' if len(self.ROI_LIST)!=0 else 'disabled')
        self.VALUE_SELECT.config(state= 'normal' if len(self.ROI_LIST)!=0 else 'disabled')
        GO = 1
        for i in range(len(self.ROI_LIST)):
            if self.ROI_LIST[i].ROI_TYPE_src == 1:
                GO = 1; break
        self.MAP_SELECT_BTTN2.config(state= 'disabled' if GO==0 else 'normal')
        self.MAP_SELECT_BTTN3.config(state= 'disabled' if GO==0 else 'normal')
        self.BTTN11.config(state= 'disabled' if GO==0 else 'normal')
        self.BTTN12.config(state= 'disabled' if GO==0 else 'normal')

    def MOUSE_B3_CLICK_HANDLER(self, event):
        self.Canvas_X, self.Canvas_Y = event.x, event.y
        #if self.MOUSE_MODE!=0:
        #    self.DICOM_CANVAS.delete(self.CURRENT_LINE)
        #    del(self.ROI_LIST[-1])

        self.RIGHT_CLK_MENU.entryconfig("ROI 삭제",state='normal' if self.ROI_Selected!=-1 else 'disabled')
        #self.RIGHT_CLK_MENU.entryconfig("ROI 복사"         , state='normal' if self.ROI_Selected!=-1 else 'disabled')
        #self.RIGHT_CLK_MENU.entryconfig("ROI 붙여넣기"     , state='normal' if self.COPIED!=None else 'disabled')
        self.RIGHT_CLK_MENU.entryconfig("Set as reference"  , state='normal' if self.ROI_Selected!=-1 else 'disabled')
        self.RIGHT_CLK_MENU.entryconfig("Set as material"   , state='normal' if self.ROI_Selected!=-1 else 'disabled')
        self.RIGHT_CLK_MENU.entryconfig("Set as background" , state='normal' if self.ROI_Selected!=-1 else 'disabled')
        self.RIGHT_CLK_MENU.tk_popup(event.x_root+80, event.y_root, 0)
        self.RIGHT_CLK_MENU.grab_release()

    def SI_MARKER_PROCESSING(self, event=None, remove=False):
        try:
            self.DICOM_CANVAS.delete(self.DICOM_CANVAS_CROSS1)
            self.DICOM_CANVAS.delete(self.DICOM_CANVAS_CROSS2)
            self.DICOM_CANVAS.delete(self.DICOM_CANVAS_TEXT0)
            self.DICOM_CANVAS.delete(self.DICOM_MARKER_INTENSITY1)
            self.DICOM_CANVAS.delete(self.DICOM_MARKER_NUMS)
        except: pass
        finally:
            #if remove==True: self.Marker_Intensities=None; self.DISPLAY_GRAPH() ; return None
            self.Marker_Intensities = self.IMAGEs.IMGs[self.IMG_Y, self.IMG_X, :]
            #self.DISPLAY_GRAPH(marker_only=True)    
            self.DICOM_CANVAS_CROSS1=self.DICOM_CANVAS.create_line(self.Canvas_X-10, self.Canvas_Y, self.Canvas_X+10, self.Canvas_Y, fill='red')
            self.DICOM_CANVAS_CROSS2=self.DICOM_CANVAS.create_line(self.Canvas_X, self.Canvas_Y-10, self.Canvas_X, self.Canvas_Y+10, fill='red')
            self.DICOM_MARKER_NUMS = self.DICOM_CANVAS.create_text(10,20,font='Arial 10 bold',text='+', fill='red')
            self.DICOM_CANVAS_TEXT0 =self.DICOM_CANVAS.create_text(50,20,fill='white',font="Arial 10",text='({0}, {1})'.format(self.IMG_X,self.IMG_Y))    
            self.DICOM_MARKER_INTENSITY1 = self.DICOM_CANVAS.create_text(140,20,font='Arial 10', text='%3d'%(self.IMAGEs.IMGs[self.IMG_Y, self.IMG_X, self.Current_File.get()]), fill='white')

    def DISPLAY_GRAPH(self, index=-1,toggle=False):
        self.Values = []; self.Colors = []; self.ROI_NAMEs = []; self.Reference = []; self.Backgrounds = []
        self.Build_SNR_MAP()
        self.SI_AX.clear()#; self.SI_AX2.clear()

        if self.IMG_Mode.get()==0: #RAW IMAGE
            self.SI_AX.set_title('Raw Intensity')
            for i, ROI in enumerate(self.ROI_LIST):
                self.Colors.append( 'r' if self.ROI_LIST[i].ROI_TYPE_src == 1 else ('b' if self.ROI_LIST[i].ROI_TYPE_src==2 else 'g') )
                #1: Background, 2: Reference, 3: Material
                self.ROI_LIST[i].Measure_ROI(self.IMAGEs.IMGs)
                self.Values.append( self.ROI_LIST[i].Intensities.mean() if self.STD_VIEW.get()==0 else self.ROI_LIST[i].Intensities.std()) #MEAN_VALUE or STD_VALUE
                print('ROI #{0}'.format(i+1),self.ROI_LIST[i].Intensities.std() )
                self.ROI_NAMEs.append('ROI #{0}'.format(i+1))

        elif self.IMG_Mode.get()!=0: #NOT RAW IMAGE
            idx = 1
            for i, ROI in enumerate(self.ROI_LIST): #SEARCH FOR ROIs
                self.ROI_LIST[i].Measure_ROI(self.IMAGEs.IMGs) #Measuring roi information
                if   self.ROI_LIST[i].ROI_TYPE_src == 1: self.Backgrounds.extend(ROI.Intensities) # IF ROI is background roi, 
                else:
                    if self.IMG_Mode.get()==1: #SNR
                        self.Values.append(self.ROI_LIST[i].Intensities.mean());  
                        self.Colors.append( 'b' if self.ROI_LIST[i].ROI_TYPE_src==2 else 'g' )#1: Background, 2: Reference, 3: Material
                        self.ROI_NAMEs.append('#{0}'.format(i+1))
                    
                    else: #CNR
                        if self.ROI_LIST[i].ROI_TYPE_src == 2: self.Reference = self.ROI_LIST[i].Intensities.mean()
                        else:
                            self.Values.append(self.ROI_LIST[i].Intensities.mean())
                            self.ROI_NAMEs.append('#{0}'.format(i+1)); self.Colors.append( 'g' )
            try:
                self.SI_AX.set_title('SNR')                
                Std_value = np.array(self.Backgrounds).std()
                self.Values = np.array(self.Values)/Std_value
                if self.IMG_Mode.get()==2: 
                    self.Values -= self.Reference/Std_value
                    self.SI_AX.set_title('CNR')
            except: pass

        plt.clf()
        self.SI_FIG = plt.figure(0,figsize=(15,15))
        self.SI_AX = self.SI_FIG.add_subplot(111)
        self.SI_AX.set_title("Intensity Monitor"); plt.grid(b=None)
        self.SI_AX.barh(self.ROI_NAMEs,self.Values,color=self.Colors)

        try: plt.ylim(xmin=min(self.Values)//2)
        except: pass
        for X,Y in zip(self.ROI_NAMEs, self.Values):
            self.SI_AX.text(Y*1.01,X,'%3.4f'%(Y))

        #self.SI_AX2 = self.SI_FIG.add_subplot(212)
        #self.SI_AX2.set_title("SNR Map")
        #self.SI_AX_IM = self.SI_AX2.imshow(self.SNR_MAP,cmap='jet'); plt.grid(None)
        #self.SI_FIG.colorbar(self.SI_AX_IM, ax=self.SI_AX2)
        self.SI_CANVAS.draw()
        self.BTTN9.config(  state='normal' if len(self.ROI_LIST)!=0 else 'disabled', relief=TK.RAISED, bg='#3C3C3C') #ROI_SAVE
        self.BTTN10.config( state='normal' if len(self.ROI_LIST)!=0 else 'disabled', relief=TK.RAISED, bg='#3C3C3C') #ROI_CLEAR
        
    def Draw_Control_Point(self, index):
        try: self.DICOM_CANVAS.delete(*self.CONTROL_POINTS)
        except: pass
        self.CONTROL_POINTS = []
        if self.ROI_LIST[index].ROI_TYPE!='ROI_FREE':
            if self.ROI_LIST[index].ROI_TYPE=='ROI_POLY':
                for idx in range(0,len(self.ROI_LIST[index].ROI_for_TK), 2):
                    X1,Y1 = self.ROI_LIST[index].ROI_for_TK[idx],self.ROI_LIST[index].ROI_for_TK[idx+1]
                    self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X1-1,Y1-1,X1-1,Y1+1,X1+1,Y1+1,X1+1,Y1-1,fill='white',outline='white', width=2))
            elif self.ROI_LIST[index].ROI_TYPE=='ROI_RECT':
                X1,Y1,X2,Y2 = self.ROI_LIST[index].ROI_for_TK[0],self.ROI_LIST[index].ROI_for_TK[1],self.ROI_LIST[index].ROI_for_TK[4],self.ROI_LIST[index].ROI_for_TK[5]
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X1-1,Y1-1,X1-1,Y1+1,X1+1,Y1+1,X1+1,Y1-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X1-1,Y2-1,X1-1,Y2+1,X1+1,Y2+1,X1+1,Y2-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X2-1,Y2-1,X2-1,Y2+1,X2+1,Y2+1,X2+1,Y2-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X2-1,Y1-1,X2-1,Y1+1,X2+1,Y1+1,X2+1,Y1-1,fill='white',outline='white', width=2))
            elif self.ROI_LIST[index].ROI_TYPE=='ROI_CIRCLE': 
                X1, X2 = self.ROI_LIST[index].ROI_for_TK[0], self.ROI_LIST[index].ROI_for_TK[2]
                X3     = (X1+X2)//2
                Y1, Y2 = self.ROI_LIST[index].ROI_for_TK[1], self.ROI_LIST[index].ROI_for_TK[3]
                Y3     = (Y1+Y2)//2
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X3-1,Y1-1,X3-1,Y1+1,X3+1,Y1+1,X3+1,Y1-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X1-1,Y3-1,X1-1,Y3+1,X1+1,Y3+1,X1+1,Y3-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X3-1,Y2-1,X3-1,Y2+1,X3+1,Y2+1,X3+1,Y2-1,fill='white',outline='white', width=2))
                self.CONTROL_POINTS.append(self.DICOM_CANVAS.create_polygon(X2-1,Y3-1,X2-1,Y3+1,X2+1,Y3+1,X2+1,Y3-1,fill='white',outline='white', width=2))
    
    def Remove_Control_Point(self):
        try: 
            self.DICOM_CANVAS.delete(*self.CONTROL_POINTS)
            self.CONTROL_POINTS = []
        except: pass

    def Remove_ROI(self):
        try: self.DICOM_CANVAS.delete(*self.CONTROL_POINTS)
        except: pass
        
        for idx in range(len(self.ROI_LIST)-1 if self.ROI_Selected==-1 else self.ROI_Selected, -1 if self.ROI_Selected==-1 else self.ROI_Selected-1, -1):
            try: 
                self.DICOM_CANVAS.delete(self.ROI_LIST[idx].TK_INDEX)
                del(self.ROI_LIST[idx])
            except: pass
        
        GO = 0
        for i in range(len(self.ROI_LIST)):
            if self.ROI_LIST[i].ROI_TYPE_src == 1: GO = 1
        self.BTTN11.config(state= 'disabled' if GO==0 else 'normal')
        self.BTTN12.config(state= 'disabled' if GO==0 else 'normal')   
        self.MAP_SELECT_BTTN2.config(state= 'disabled' if GO==0 else 'normal')
        self.MAP_SELECT_BTTN3.config(state= 'disabled' if GO==0 else 'normal')
        self.ROI_Selected=-1; self.Status.set('IDLE')
        self.DISPLAY_GRAPH()

    def Copy_ROI(self): 
        self.COPIED = [copy.copy( self.ROI_LIST[self.ROI_Selected] ), self.ROI_LIST[self.ROI_Selected].ROI_TYPE]
        
    def Paste_ROI(self):
        self.ROI_LIST.append(self.COPIED[0])
        dx, dy = self.Canvas_X - self.ROI_LIST[-1].ROI_X[0], self.Canvas_Y - self.ROI_LIST[-1].ROI_Y[1]

        if self.COPIED[1]=='ROI_CIRCLE':
            self.CURRENT_LINE = self.DICOM_CANVAS.create_oval(self.Canvas_X,self.Canvas_Y,self.Canvas_X+1,self.Canvas_Y+1,fill='',width=2,outline=self.Outlines[self.ROI_TYPE_Var.get()])
        else:
            self.CURRENT_LINE = self.DICOM_CANVAS.create_polygon(self.Canvas_X, self.Canvas_Y,fill='',width=2,outline=self.Outlines[self.ROI_TYPE_Var.get()])

        self.ROI_LIST[-1].TK_INDEX = self.CURRENT_LINE
        self.ROI_LIST[-1].MOVE_ROI(dx,dy)
        self.ROI_Selected = len(self.ROI_LIST)-1
        self.DICOM_CANVAS.coords(self.ROI_LIST[self.ROI_Selected].TK_INDEX,*self.ROI_LIST[self.ROI_Selected].ROI_for_TK)
        GO = 0
        for i in range(len(self.ROI_LIST)):
            if self.ROI_LIST[i].ROI_TYPE_src == 1: GO = 1
        self.BTTN11.config(state= 'disabled' if GO==0 else 'normal')
        self.BTTN12.config(state= 'disabled' if GO==0 else 'normal')   
        self.MAP_SELECT_BTTN2.config(state= 'disabled' if GO==0 else 'normal')
        self.MAP_SELECT_BTTN3.config(state= 'disabled' if GO==0 else 'normal')
        self.ROI_Selected=-1; self.Status.set('IDLE')
        self.DISPLAY_GRAPH()

    def Set_ROI_As(self, to=2):
        if   to==1: color='red'   #background
        elif to==2: 
            color='blue'  #reference
            for i in range(len(self.ROI_LIST)):
                if self.ROI_LIST[i].ROI_TYPE_src==2: 
                    self.ROI_LIST[i].ROI_TYPE_src = 3; self.DICOM_CANVAS.itemconfig(self.ROI_LIST[i].TK_INDEX, width=2,outline='green'); break
        elif to==3: color='green' #material
        self.ROI_LIST[self.ROI_Selected].ROI_TYPE_src = to
        GO = 0
        for i in range(len(self.ROI_LIST)):
            if self.ROI_LIST[i].ROI_TYPE_src == 1: GO = 1
                        
        self.BTTN11.config(state= 'disabled' if GO==0 else 'normal')
        self.BTTN12.config(state= 'disabled' if GO==0 else 'normal')
        self.MAP_SELECT_BTTN2.config(state= 'disabled' if GO==0 else 'normal')
        self.MAP_SELECT_BTTN3.config(state= 'disabled' if GO==0 else 'normal')
        self.DISPLAY_GRAPH()
        self.DICOM_CANVAS.itemconfig(self.ROI_LIST[self.ROI_Selected].TK_INDEX, width=2,outline=color)

    def About_Program(self):
        messagebox.showinfo('About',"""
        {0}
        Ver: {1}\n
        Developed by Kim Yun Heung
        (techman011@gmail.com)
        KNU BMRLab (http://bmr.knu.ac.kr)\n
            --Main modules--
        Pydicom, OpenCV, matplotlib, scipy, numpy, SimpleITK\n
        """.format(__TITLE__,__version__))

if __name__ == "__main__":
    ROOT = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')
    print("Starting {0}...".format(__TITLE__))
    matplotlib.use('TkAgg')
    style.use('bmh')
    print('================================')
    print('Pydicom:',pydicom.__version__)
    print('OpenCV:', cv2.__version__)
    print('Nibabel:', nib.__version__)
    print('Matplotlib:', matplotlib.__version__)
    print('PIL:', PIL.__version__)
    print('Bruker2Nifti', brk.__version__)

    MAIN_WINDOW = MAIN_PROGRAM(ROOT)



