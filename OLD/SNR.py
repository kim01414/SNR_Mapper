class MAIN_WINDOW:
    def __init__(self):
        ######MAIN_WINDOW Initialize#####
        self.MODE = [False, False, True, False, False, False] 
        #Zoom, IsZooming, ROI_Visible, ROI_MOVE, ROI_ADD, ROI_ADD2
        self.ROI_SHAPE = 0 #0: Free, 1: Rec, 2: Circle
        self.Drag=False
        self.Drag_index=False
        self.source_path = os.path.dirname(os.path.abspath(__file__))
        self.default_path = os.path.dirname(os.path.abspath(__file__))
        self.MAIN = TK.Tk()
        self.SCREEN_SIZE = [self.MAIN.winfo_screenheight(), self.MAIN.winfo_screenwidth()]
        self.MAIN.geometry('490x105+{0}+{1}'.format(self.SCREEN_SIZE[1]-500,0))
        self.MAIN.resizable(0,0)
        self.MAIN.title('SNR MAPPER')
        self.MAIN.iconbitmap(self.default_path+'\icon.ico')
        self.MAIN.protocol('WM_DELETE_WINDOW',self.shutdown)
        self.ROI_List = None
        self.ROI_List_open = False
        #Global Values
        self.Status = TK.StringVar()
        self.Status.set('SNR MAPPER ver 1.0 / python 3.7.2')
        self.mousePos = TK.StringVar()
        self.mousePos.set('Hello')
        self.opt1, self.opt2, self.opt3 = TK.IntVar(), TK.IntVar(), TK.IntVar()
        self.opt1.set(0)
        self.opt2.set(0)
        self.opt3.set(0)
        self.Intensity = TK.IntVar()
        self.Intensity.set(0)
        self.FILE_NAME_LIST = None
        self.IMAGES = None
        self.Current_FILE = TK.IntVar()
        self.Current_FILE.set(0)
        self.Total_FILE = TK.IntVar()
        self.Total_FILE.set(0)
        self.Threshold_Global = TK.IntVar()
        self.Threshold_Global.set(0)
        self.Clipboard = None
        self.Copied=False
        self.Copied_From=None
        self.Shared_ROI = []
        self.SUB_WINDOWS = []
        self.ICONS = None
        self.Initialize_Widgets()

    #####Widget Initialize#####
    def Initialize_Widgets(self):
        X, Y = 5, 5
        with open(self.source_path+'\\resource.dat','rb') as file: self.ICONS = pickle.load(file)
        for key in self.ICONS:
            OMG = 255
            if key=='FILE_OPEN': OMG=1
            self.ICONS[key] = ImageTk.PhotoImage(Image.fromarray((self.ICONS[key]*OMG).astype(np.uint8)))
        self.Open_FILE_Bttn = TK.Button(self.MAIN, text='이미지 파일 열기',image=self.ICONS['FILE_OPEN'], command=self.OPEN_FILE)
        self.Open_FILE_Bttn.place(x=X, y=Y, width=30, height=30)
        self.Open_FILE_Bttn.bind('<Motion>',lambda x:self.Status.set('DICOM 파일(들)을 불러옵니다.'))

        self.ROI_Visible_Bttn = TK.Button(self.MAIN, text='ROI 표시여부',image=self.ICONS['ROI_VISIBLE'], command=self.ROI_Visible_Set,relief=TK.SUNKEN,state='disabled')
        self.ROI_Visible_Bttn.place(x=X+30, y=Y,width=30, height=30)
        self.ROI_Visible_Bttn.bind('<Motion>',lambda x:self.Status.set('이미지에 ROI 표시여부를 설정합니다.'))

        self.Drag_Bttn = TK.Button(self.MAIN, text='ROI 이동모드',image=self.ICONS['ROI_MOVE'], command=self.Move_Selected_ROI_MODE,state='disabled')
        self.Drag_Bttn.place(x=X+60, y=Y,width=30, height=30)
        self.Drag_Bttn.bind('<Motion>',lambda x:self.Status.set('ROI 이동모드'))

        self.Selection_Bttn = TK.Button(self.MAIN, text='ROI추가(Noise)',image=self.ICONS['ROI_SELECT1_1'], command=self.Set_Noise_ROI_Select_MODE,state='disabled')
        self.Selection_Bttn.place(x=X+90+15, y=Y,width=30, height=30)
        self.Selection_Bttn.bind('<Motion>',lambda x:self.Status.set('Noise ROI 추가모드(자유형)'))

        self.Selection_Bttn2 = TK.Button(self.MAIN, text='ROI추가(Noise)',image=self.ICONS['ROI_SELECT1_2'], command=self.Set_Noise_ROI_Select_MODE2,state='disabled')
        self.Selection_Bttn2.place(x=X+120+15, y=Y,width=30, height=30)
        self.Selection_Bttn2.bind('<Motion>',lambda x:self.Status.set('Noise ROI 추가모드(사각형)'))

        self.Selection_Bttn3 = TK.Button(self.MAIN, text='ROI추가(Noise)',image=self.ICONS['ROI_SELECT1_3'], command=self.Set_Noise_ROI_Select_MODE3,state='disabled')
        self.Selection_Bttn3.place(x=X+150+15, y=Y,width=30, height=30)
        self.Selection_Bttn3.bind('<Motion>',lambda x:self.Status.set('Noise ROI 추가모드(원 형)'))
        self.Selection2_Bttn = TK.Button(self.MAIN, text='ROI추가(Normal)', image=self.ICONS['ROI_SELECT2_1'], command=self.Set_Normal_ROI_Select_MODE,state='disabled')
        self.Selection2_Bttn.place(x=X+180+15+15, y=Y,width=30, height=30)
        self.Selection2_Bttn.bind('<Motion>',lambda x:self.Status.set('Normal ROI 추가모드(자유형)'))\

        self.Selection2_Bttn2 = TK.Button(self.MAIN, text='ROI추가(Normal)',image=self.ICONS['ROI_SELECT2_2'], command=self.Set_Normal_ROI_Select_MODE2,state='disabled')
        self.Selection2_Bttn2.place(x=X+210+15+15, y=Y,width=30, height=30)
        self.Selection2_Bttn2.bind('<Motion>',lambda x:self.Status.set('Normal ROI 추가모드(사각형)'))

        self.Selection2_Bttn3 = TK.Button(self.MAIN, text='ROI추가(Normal)',image=self.ICONS['ROI_SELECT2_3'], command=self.Set_Normal_ROI_Select_MODE3,state='disabled')
        self.Selection2_Bttn3.place(x=X+240+15+15, y=Y,width=30, height=30)
        self.Selection2_Bttn3.bind('<Motion>',lambda x:self.Status.set('Normal ROI 추가모드(원 형)'))

        self.Magic_Selection_Bttn = TK.Button(self.MAIN, text='자동 ROI',image=self.ICONS['ROI_AUTO_SEL'], command=self.Command_Test,state='disabled')
        self.Magic_Selection_Bttn.place(x=X+300+15, y=Y,width=30, height=30)
        self.Magic_Selection_Bttn.bind('<Motion>',lambda x:self.Status.set('프로그램에서 자동으로 ROI를 선별합니다.(아직 구현되지 않음)'))

        self.Image_Info_Bttn = TK.Button(self.MAIN, text='SNR 그래프',image=self.ICONS['MAKE_GRAPH'], command=self.Generate_Graph,state='disabled')
        self.Image_Info_Bttn.place(x=X+330+15, y=Y,width=30, height=30)
        self.Image_Info_Bttn.bind('<Motion>',lambda x:self.Status.set('측정한 값들을 바탕으로 그래프를 생성합니다.'))

        self.MRI_Tag_Bttn = TK.Button(self.MAIN, text='DICOM 태그',image=self.ICONS['MRI_TAGS'], command=addons.nothing,state='disabled')
        self.MRI_Tag_Bttn.place(x=X+360+15, y=Y,width=30, height=30)
        self.MRI_Tag_Bttn.bind('<Motion>',lambda x:self.Status.set('DICOM 태그를 확인합니다.(아직 구현되지 않음)'))

        self.Settings_Bttn = TK.Button(self.MAIN, text='환경설정',image=self.ICONS['SETTINGS'], command=self.Settings_WINDOW,state='normal')
        self.Settings_Bttn.place(x=X+420, y=Y, width=30, height=30) 
        self.Settings_Bttn.bind('<Motion>',lambda x:self.Status.set('환경설정을 엽니다.'))

        self.Info = TK.Button(self.MAIN, text='',image=self.ICONS['INFORMATION'], command=self.About_SNR_MAPPER)
        self.Info.place(x=X+450, y=Y,width=30, height=30)
        self.Info.bind('<Motion>',lambda x:self.Status.set('프로그램 정보를 출력합니다.'))

        self.labelframe1 = TK.LabelFrame(self.MAIN, text='Threshold 설정')
        self.labelframe1.place(x=10, y=Y+35,width=470)

        self.Threshold_Global_label = TK.Label(self.labelframe1, textvariable=self.Threshold_Global)
        self.Threshold_Global_label.pack(side='right')
    
        self.Threshold_set = TK.Scale(self.labelframe1, variable=self.Threshold_Global, command=self.Global_Threshold_Update, orient='horizontal',showvalue=0, to=1000, from_=0,state='disabled')
        self.Threshold_set.pack(expand=True, side='left',fill='x')
        self.Threshold_set.bind('<Motion>',lambda x:self.Status.set('Threshold값을 설정합니다.'))

        self.Statusbar = TK.Label(self.MAIN, bd=1, relief='sunken', anchor='w', textvariable=self.Status)
        self.Statusbar.place(x=0,y=Y+80,width=370)

        self.MousePosbar = TK.Label(self.MAIN,bd=1, relief='sunken', anchor='e', textvariable=self.mousePos)
        self.MousePosbar.place(x=370,y=Y+80,width=80)

        self.Intensitybar = TK.Label(self.MAIN, bd=1, relief='sunken', anchor='e', textvariable=self.Intensity)
        self.Intensitybar.place(x=450,y=Y+80,width=40)

        self.MAIN.bind('<Leave>',lambda x: self.Status.set('IDLE'))
        self.MAIN.mainloop()

    #####Event Handlers#####
    def OPEN_FILE(self,x=None):
        THIS = list(filedialog.askopenfilenames(initialdir=self.default_path, title='DICOM파일 열기'))
        TOTAL = len(THIS)
        if TOTAL!=0:
            self.MODE = [False, False, True, False, False, False]
            self.Selection_Bttn.config(relief=TK.RAISED)
            self.Selection2_Bttn.config(relief=TK.RAISED)
            self.FILE_NAME_LIST = THIS
            self.Total_FILE.set(self.Total_FILE.get()+len(THIS))
            i=len(self.SUB_WINDOWS)
            for FILE_NAME in self.FILE_NAME_LIST:
                try:
                    IMAGE = addons.IMAGE(FILE_NAME) 
                    IMAGE.Apply_Threshold(0,self.MODE[2])
                    self.SUB_WINDOWS.append(WINDOW(self,IMAGE,IMAGE_INDEX=i))
                    i+=1
                except:
                    self.Total_FILE.set(self.Total_FILE.get()-1)
                    addons.FATAL_ERROR('파일 열기 실패','{0}은(는)\nDICOM형식이 아니거나 손상되어 열 수 없습니다.'.format(FILE_NAME))
            self.Selection_Bttn.config(state='normal')
            self.Selection_Bttn2.config(state='normal')
            self.Selection_Bttn3.config(state='normal')
            self.Selection2_Bttn.config(state='normal')
            self.Selection2_Bttn2.config(state='normal')
            self.Selection2_Bttn3.config(state='normal')
            self.Drag_Bttn.config(state='normal')
            self.Image_Info_Bttn.config(state='normal')
            self.ROI_Visible_Bttn.config(state='normal')
            self.Threshold_set.config(from_=0,state='normal')
            #self.Magic_Selection_Bttn.config(state='normal')
            #self.MRI_Tag_Bttn.config(state='normal')
            self.Threshold_Global.set(0)
            temp = THIS[0].split('/')[:-1]
            self.default_path = ''
            for part in temp: self.default_path+=(part+'/')

    def TEST(self,x=None):
        print('HELLO')

    def Set_Free(self,x=None): self.ROI_SHAPE=0
    def Set_Rec(self,x=None): self.ROI_SHAPE=1
    def Set_Circle(self,x=None): self.ROI_SHAPE=2

    def Global_Threshold_Update(self,x=None):
        for i in range(len(self.SUB_WINDOWS)):
            self.SUB_WINDOWS[i].IMAGE.Apply_Threshold(self.Threshold_Global.get())
            self.SUB_WINDOWS[i].Refresh_Image()
        
    def ROI_Visible_Set(self,x=None):
        if self.MODE[2]==True: 
            self.MODE[2] = False
            self.ROI_Visible_Bttn.config(relief=TK.RAISED)
        else: 
            self.MODE[2] = True
            self.ROI_Visible_Bttn.config(relief=TK.SUNKEN)
        for i in range(len(self.SUB_WINDOWS)):
            self.SUB_WINDOWS[i].IMAGE.Apply_Threshold(-1, self.MODE[2], True)
            self.SUB_WINDOWS[i].Screen = cv2.resize(self.SUB_WINDOWS[i].IMAGE.Source_RGB, (self.SUB_WINDOWS[i].w,self.SUB_WINDOWS[i].h),interpolation=cv2.INTER_AREA)
            self.SUB_WINDOWS[i].Screen = self.SUB_WINDOWS[i].IMAGE.Convert_TK_IMAGE( self.SUB_WINDOWS[i].Screen )
            self.SUB_WINDOWS[i].MAIN_SCREEN.config(image=self.SUB_WINDOWS[i].Screen)
    
    def Raise_Bttn(self,b0=True,b1=True,b2=True,b3=True,b4=True,b5=True,b6=True):
        for idx in range(len(self.SUB_WINDOWS)):
            if self.SUB_WINDOWS[idx].IMAGE.ROI_Current_pts!=[]:
                self.SUB_WINDOWS[idx].IMAGE.ROI_Current_pts = []
                self.SUB_WINDOWS[idx].Refresh_Image()
        if b0 == True: self.Drag_Bttn.config(relief=TK.RAISED)
        if b1 == True: self.Selection_Bttn.config(relief=TK.RAISED)
        if b2 == True: self.Selection_Bttn2.config(relief=TK.RAISED)
        if b3 == True: self.Selection_Bttn3.config(relief=TK.RAISED)
        if b4 == True: self.Selection2_Bttn.config(relief=TK.RAISED)
        if b5 == True: self.Selection2_Bttn2.config(relief=TK.RAISED)
        if b6 == True: self.Selection2_Bttn3.config(relief=TK.RAISED)

    def Set_Noise_ROI_Select_MODE(self,x=None):
        #Zoom, IsZooming, ROI_Visible, ROI_MOVE(3), ROI_ADD(4), ROI_ADD2(5)
        self.MODE[5]=False
        self.Raise_Bttn(b1=False)
        if self.MODE[4]==False or (self.MODE[4]==True and self.ROI_SHAPE != 0):
            self.ROI_SHAPE = 0
            self.Selection_Bttn.config(relief=TK.SUNKEN)
            self.Drag_Bttn.config(relief=TK.RAISED)
            self.ROI_MOVE_Cancel()
            self.MODE[3]=False
            self.MODE[4]=True
        else:
            self.Selection_Bttn.config(relief=TK.RAISED)
            self.Move_Selected_ROI_MODE()
            self.MODE[4]=False

    def Set_Noise_ROI_Select_MODE2(self,x=None):
        #Zoom, IsZooming, ROI_Visible, ROI_MOVE(3), ROI_ADD(4), ROI_ADD2(5)
        self.MODE[5]=False
        self.Raise_Bttn(b2=False)
        if self.MODE[4]==False or (self.MODE[4]==True and self.ROI_SHAPE != 1):
            self.ROI_SHAPE = 1
            self.Selection_Bttn2.config(relief=TK.SUNKEN)
            self.Drag_Bttn.config(relief=TK.RAISED)
            self.ROI_MOVE_Cancel()
            self.MODE[3]=False
            self.MODE[4]=True
        else:
            self.Selection_Bttn2.config(relief=TK.RAISED)
            self.Move_Selected_ROI_MODE()
            self.MODE[4]=False

    def Set_Noise_ROI_Select_MODE3(self,x=None):
        #Zoom, IsZooming, ROI_Visible, ROI_MOVE(3), ROI_ADD(4), ROI_ADD2(5)
        self.MODE[5]=False
        self.Raise_Bttn(b3=False)
        if self.MODE[4]==False or (self.MODE[4]==True and self.ROI_SHAPE != 2):
            self.ROI_SHAPE = 2
            self.Selection_Bttn3.config(relief=TK.SUNKEN)
            self.Drag_Bttn.config(relief=TK.RAISED)
            self.ROI_MOVE_Cancel()
            self.MODE[3]=False
            self.MODE[4]=True
        else:
            self.Selection_Bttn3.config(relief=TK.RAISED)
            self.Move_Selected_ROI_MODE()
            self.MODE[4]=False
       
    def Set_Normal_ROI_Select_MODE(self,x=None):
        self.MODE[4]=False
        self.Raise_Bttn(b4=False)
        if self.MODE[5]==False or (self.MODE[5]==True and self.ROI_SHAPE != 0):
            self.ROI_SHAPE = 0
            self.Selection2_Bttn.config(relief=TK.SUNKEN)
            self.Drag_Bttn.config(relief=TK.RAISED)
            self.ROI_MOVE_Cancel()
            self.MODE[3]=False
            self.MODE[5]=True
        else:
            self.Selection2_Bttn.config(relief=TK.RAISED)
            self.Move_Selected_ROI_MODE()
            self.MODE[5]=False

    def Set_Normal_ROI_Select_MODE2(self,x=None):
        self.MODE[4]=False
        self.Raise_Bttn(b5=False)
        if self.MODE[5]==False or (self.MODE[5]==True and self.ROI_SHAPE != 1):
            self.ROI_SHAPE = 1
            self.Selection2_Bttn2.config(relief=TK.SUNKEN)
            self.Drag_Bttn.config(relief=TK.RAISED)
            self.ROI_MOVE_Cancel()
            self.MODE[3]=False
            self.MODE[5]=True
        else:
            self.Selection2_Bttn2.config(relief=TK.RAISED)
            self.Move_Selected_ROI_MODE()
            self.MODE[5]=False

    def Set_Normal_ROI_Select_MODE3(self,x=None):
        self.MODE[4]=False
        self.Raise_Bttn(b6=False)
        if self.MODE[5]==False or (self.MODE[5]==True and self.ROI_SHAPE != 2):
            self.ROI_SHAPE = 2
            self.Selection2_Bttn3.config(relief=TK.SUNKEN)
            self.Drag_Bttn.config(relief=TK.RAISED)
            self.ROI_MOVE_Cancel()
            self.MODE[3]=False
            self.MODE[5]=True
        else:
            self.Selection2_Bttn3.config(relief=TK.RAISED)
            self.Move_Selected_ROI_MODE()
            self.MODE[5]=False

    def Move_Selected_ROI_MODE(self,x=None):
        if self.MODE[3]==False:
            self.MODE[3]=True
            self.MODE[4]=False
            self.MODE[5]=False
            self.Drag_Bttn.config(relief=TK.SUNKEN)
            self.Raise_Bttn(b0=False)
        else:
            self.MODE[3]=False
            self.ROI_MOVE_Cancel()
            self.Drag_Bttn.config(relief=TK.RAISED)

    def ROI_MOVE_Cancel(self,x=None):
        for i in range(len(self.SUB_WINDOWS)):
            if self.SUB_WINDOWS[i].IMAGE.Cur_ROI!=-1:
                self.SUB_WINDOWS[i].IMAGE.Cur_ROI=-1
                self.SUB_WINDOWS[i].Refresh_Image()

    def Generate_Graph(self, x=None):
        global TEST_MODE
        LIST = []
        print('\n==========MEAN_VALUEs==========')
        if TEST_MODE==True: start = time.time()
        for idx in range(len(self.SUB_WINDOWS)):
            self.SUB_WINDOWS[idx].IMAGE.Apply_Threshold(self.Threshold_Global.get(),force=True, refresh_noise=True)
            if 'Normal' in self.SUB_WINDOWS[idx].IMAGE.ROI_TYPEs:
                AREA = self.SUB_WINDOWS[idx].IMAGE.Source_Intensity[np.where(self.SUB_WINDOWS[idx].IMAGE.MASK==255)[:2]]
                AREA2 = AREA / self.SUB_WINDOWS[idx].IMAGE.trash_STD
                MEAN = AREA2.mean()
            else:
                AREA = self.SUB_WINDOWS[idx].IMAGE.Source_Intensity.copy()
                AREA2 = AREA / self.SUB_WINDOWS[idx].IMAGE.trash_STD
                MEAN = AREA2.mean()
            print(MEAN)
            LIST.append(MEAN)
        if TEST_MODE==True: 
            end = time.time()
            print('Elapsed Time:',end-start)
        X = [i for i in range(1,len(self.SUB_WINDOWS)+1)]
        plt.close('all')
        plt.plot(X,LIST)
        plt.xticks(np.arange(1,len(self.SUB_WINDOWS)+1,1))
        plt.grid()
        plt.xlabel('IMAGE #')
        plt.ylabel('SNR MEAN VALUE')
        plt.title('SNR MEAN GRAPH')
        plt.show()

    def Command_Test(self, x=None):
        IMAGE = self.SUB_WINDOWS[0].IMAGE.Source_Intensity
        plt.imshow(addons.IMAGE_PROCESS(IMAGE), cmap='gray')
        plt.show()

    def About_SNR_MAPPER(self,x=None):
        addons.messagebox.showinfo('About','SNR MAPPER ver 1.0\n김윤흥\nKyungpook National University BMRLab\nhttp://bmr.knu.ac.kr\npython 3.7.3')
       
    def Settings_WINDOW(self,x=None):
        self.Setting_WINDOW = TK.Toplevel()
        self.Setting_WINDOW.geometry('300x200+1620+120')
        self.Setting_WINDOW.title('환경설정')
        self.Setting_WINDOW.iconbitmap(self.source_path+'\source\icon.ico')
        self.Setting_WINDOW.resizable(0,0)
        ToolBOX_always_ON_TOP = TK.Checkbutton(self.Setting_WINDOW, text='툴박스를 항상 위에 표시',anchor='w', variable=self.opt1)
        ToolBOX_always_ON_TOP.place(x=25,y=50,width=250)
        Viewer_always_ON_TOP  = TK.Checkbutton(self.Setting_WINDOW, text='이미지 뷰어를 항상 위에 표시',anchor='w', variable=self.opt2)
        Viewer_always_ON_TOP.place(x=25,y=75,width=250)
        ROI_LIST_always_ON_TOP  = TK.Checkbutton(self.Setting_WINDOW, text='ROI 리스트를 항상 위에 표시',anchor='w', variable=self.opt3)
        ROI_LIST_always_ON_TOP.place(x=25,y=100,width=250)
        OK_Bttn = TK.Button(self.Setting_WINDOW,text='확인',command=self.Apply_Settings)
        OK_Bttn.place(x=125,y=150,width=50)
        self.Setting_WINDOW.grab_set()

    def Apply_Settings(self,x=None):
        self.MAIN.attributes('-topmost',self.opt1.get())
        if len(self.SUB_WINDOWS)!=0:
            for i in range(len(self.SUB_WINDOWS)):
                self.SUB_WINDOWS[i].IMAGE_VIEWER.attributes('-topmost',self.opt2.get())
                try: self.SUB_WINDOWS[i].ROI_List.MAIN.attributes('-topmost',self.opt3.get())
                except: pass
        self.Setting_WINDOW.destroy()

    def shutdown(self,x=None):
        self.MAIN.bell()
        answer = addons.question('프로그램 종료','프로그램을 종료할까요?')
        if answer==True:
            self.MAIN.destroy()
            plt.close('all')

class WINDOW:
    def __init__(self, MAIN, IMAGE, IMAGE_INDEX, Always_on_top=False):
        self.MAIN_PROGRAM = MAIN
        self.INDEX = IMAGE_INDEX
        self.IMAGE = IMAGE
        self.MAXIMUM = 0
        self.MINIMUM = math.inf
        self.ROI_Visible = True
        self.ROI_Global = False
        self.ROI_Shared = False
        self.ROI_List = None
        self.ROI_LIST_OPEN = False
        self.X0 = 0
        self.Y0 = 0
        if self.MAXIMUM < self.IMAGE.MAX_INTENSITY: self.MAXIMUM = self.IMAGE.MAX_INTENSITY
        if self.MINIMUM > self.IMAGE.MIN_INTENSITY: self.MINIMUM = self.IMAGE.MIN_INTENSITY
        self.MAIN_PROGRAM.Threshold_set.config(to=self.MAXIMUM)
        self.w = self.IMAGE.shape[1]
        self.h = self.IMAGE.shape[0]
        self.IMAGE_VIEWER = TK.Toplevel()
        self.IMAGE_VIEWER.iconbitmap(self.MAIN_PROGRAM.source_path+'\icon.ico')
        self.IMAGE_VIEWER.title(self.IMAGE.IMAGE_NAME.split('/')[-1])
        self.IMAGE_VIEWER.geometry('%dx%d+%d+%d'%(self.w,self.h,self.INDEX*20,self.INDEX*20))
        self.Drag = None
        self.Dragging = False
        self.IMAGE_VIEWER.bind('<Return>',self.ENTER_KEY_Handler)
        self.IMAGE_VIEWER.bind('<Key>',       self.Key_Handler)
        self.IMAGE_VIEWER.bind('<KeyRelease>',self.Key_Handler2)
        self.IMAGE_VIEWER.protocol('WM_DELETE_WINDOW',self.Destroy_WINDOWS)
        self.Screen = self.IMAGE.Source_RGB_TK
        self.MAIN_SCREEN = TK.Label(self.IMAGE_VIEWER, image=self.Screen,cursor='crosshair')
        self.MAIN_SCREEN.pack(fill=TK.BOTH, expand=TK.YES)
        self.MAIN_SCREEN.bind('<Motion>',self.Mouse_Motion_Handler)
        self.MAIN_SCREEN.bind('<Button-1>',self.Mouse_B1_Handler)
        self.MAIN_SCREEN.bind('<Button-2>',self.Mouse_B2_Handler)
        self.MAIN_SCREEN.bind('<Button-3>',self.Mouse_B3_Handler)
        self.MAIN_SCREEN.bind('<B1-Motion>',self.Mouse_B1_Motion_Handler)
        self.MAIN_SCREEN.bind('<B2-Motion>',self.Mouse_B2_Motion_Handler)
        self.MAIN_SCREEN.bind('<ButtonRelease-1>',self.Mouse_B1_Release_Handler)
        self.MAIN_SCREEN.bind('<ButtonRelease-2>',self.Mouse_B2_Release_Handler)
        self.IMAGE_VIEWER.bind('<Configure>',self.Resize_WINDOW)
        self.menubar =  Menu(self.MAIN_SCREEN, tearoff = 0)
        self.menubar.add_command(label='=====SNR MAPPER=====', command=addons.nothing, state='disabled')
        self.menubar.add_separator()
        self.menubar.add_command(label="ROI 유형 변경", command=self.ROI_TYPE_CHANGE, accelerator='(Q)', state='disabled')
        self.menubar.add_command(label="ROI 복사",command=self.ROI_Copy, accelerator='(W)',state='disabled')
        self.menubar.add_command(label="ROI 삭제",command=self.ROI_REMOVE, accelerator='(E)',state='disabled')
        self.menubar.add_command(label="ROI 붙여넣기",command=self.ROI_PASTE, accelerator='(R)',state='disabled')
        self.menubar.add_command(label="ROI 여기에 붙여넣기",command=self.ROI_PASTE_HERE, accelerator='(T)',state='disabled')
        self.menubar.add_separator()
        self.menubar.add_command(label="ROI 목록 열기", command=self.OPEN_ROI_LIST, accelerator='(D)', state='normal')
        self.menubar.add_command(label="ROI셋 불러오기",command=self.ROI_Load_from_File, accelerator='(L)',state='normal')
        self.menubar.add_command(label="현재 ROI셋 저장", command=self.ROI_Save_as_File, accelerator='(S)', state='disabled')
        self.menubar.add_command(label="ROI 전부 삭제", command=self.ROI_CLEAR, accelerator='(D)', state='disabled')
        self.menubar.add_separator()
        self.menubar.add_command(label="Color Mapping",command=self.Color_Mapping, accelerator='(C)',state='normal')
        self.menubar.bind('Key',self.menubar_handler)

    def Destroy_WINDOWS(self, x=None):
        if len(self.IMAGE.ROI_POINTs)!=0:
            ANSWER = addons.question(self.IMAGE.IMAGE_NAME.split('/')[-1],'저장하지 않은 내용들은 삭제됩니다.\n계속 하시겠습니까?')
            if ANSWER==False: return None
        self.IMAGE_VIEWER.destroy()
        if self.ROI_LIST_OPEN==True: self.ROI_List.destroy()
        del(self.MAIN_PROGRAM.SUB_WINDOWS[self.INDEX])
        for idx in range(0,len(self.MAIN_PROGRAM.SUB_WINDOWS)):
            self.MAIN_PROGRAM.SUB_WINDOWS[idx].INDEX = idx
        self.MAIN_PROGRAM.Total_FILE.set(self.MAIN_PROGRAM.Total_FILE.get()-1)
        if len(self.MAIN_PROGRAM.SUB_WINDOWS)==0:
            self.MAIN_PROGRAM.Selection_Bttn.config(state='disabled')
            self.MAIN_PROGRAM.Selection_Bttn2.config(state='disabled')
            self.MAIN_PROGRAM.Selection_Bttn3.config(state='disabled')
            self.MAIN_PROGRAM.Selection2_Bttn.config(state='disabled')
            self.MAIN_PROGRAM.Selection2_Bttn2.config(state='disabled')
            self.MAIN_PROGRAM.Selection2_Bttn3.config(state='disabled')
            self.MAIN_PROGRAM.Drag_Bttn.config(state='disabled')
            self.MAIN_PROGRAM.Image_Info_Bttn.config(state='disabled')
            self.MAIN_PROGRAM.Magic_Selection_Bttn.config(state='disabled')
            self.MAIN_PROGRAM.MRI_Tag_Bttn.config(state='disabled')
            self.MAIN_PROGRAM.ROI_Visible_Bttn.config(state='disabled')
            self.MAIN_PROGRAM.Threshold_set.config(state='disabled')
            
    def Refresh_Image(self):
        self.IMAGE.Need_Refresh = True
        self.IMAGE.Apply_Threshold(-1, True, True)
        if self.IMAGE.Source_RGB.shape[:2]!=[self.h, self.w]:
            self.Screen = self.IMAGE.Convert_TK_IMAGE( cv2.resize(self.IMAGE.Source_RGB, (self.w,self.h),interpolation=cv2.INTER_AREA) )
        else: self.Screen = self.IMAGE.Convert_TK_IMAGE(self.IMAGE.Source_RGB)
        self.MAIN_SCREEN.config(image=self.Screen)

    def Resize_WINDOW(self,event):
        if self.IMAGE_VIEWER.winfo_width()==self.w and self.IMAGE_VIEWER.winfo_height()==self.h: return None
        self.w , self.h = self.IMAGE_VIEWER.winfo_width(), self.IMAGE_VIEWER.winfo_height()
        self.Refresh_Image()

    def ENTER_KEY_Handler(self, event):
        if len(self.IMAGE.ROI_Current_pts)<3: 
            self.IMAGE.ROI_Current_pts = []
            self.IMAGE.Apply_Threshold(-1, True, True)
            self.Screen = self.IMAGE.Convert_TK_IMAGE( cv2.resize(self.IMAGE.Source_RGB, (self.w,self.h),interpolation=cv2.INTER_AREA) )
            self.MAIN_SCREEN.config(image=self.Screen)
            return None
        if self.MAIN_PROGRAM.MODE[4]==True or self.MAIN_PROGRAM.MODE[5]==True:
            if self.MAIN_PROGRAM.MODE[4]==True:  TYPE = 'Noise'
            else: TYPE = 'Normal'
            if self.ROI_Shared==True: self.MAIN_PROGRAM.Shared_ROI.append(np.array([self.IMAGE.ROI_Current_pts]))
            for i in range(len(self.MAIN_PROGRAM.SUB_WINDOWS)):
                if (self.ROI_Shared==False) and (self.ROI_Global==False and i!=self.INDEX): continue
                if self.ROI_Shared==True: self.MAIN_PROGRAM.SUB_WINDOWS[i].IMAGE.ROI_POINTs.append(self.MAIN_PROGRAM.Shared_ROI[-1])
                else: self.MAIN_PROGRAM.SUB_WINDOWS[i].IMAGE.ROI_POINTs.append(np.array([self.IMAGE.ROI_Current_pts]))

                self.MAIN_PROGRAM.SUB_WINDOWS[i].IMAGE.ROI_TYPEs.append(TYPE)
                self.MAIN_PROGRAM.SUB_WINDOWS[i].Need_Refresh=True
                if i!=self.INDEX: self.MAIN_PROGRAM.SUB_WINDOWS[i].Refresh_Image()
                if self.MAIN_PROGRAM.SUB_WINDOWS[i].ROI_LIST_OPEN==True: self.MAIN_PROGRAM.SUB_WINDOWS[i].ROI_List.Reload_ROIs()
            self.IMAGE.ROI_Current_pts = []
            self.Refresh_Image()
    
    def Key_Handler(self, event): 
        if event.keysym == 'Control_L': self.ROI_Global = True
    def Key_Handler2(self, event): 
        if event.keysym == 'Control_L': self.ROI_Global = False

    def Mouse_Motion_Handler(self, event):
        self.MAIN_SCREEN.config(cursor='crosshair')  
        O_size = self.IMAGE.shape[:2]
        X = int(event.x /self.w * O_size[0])
        Y = int(event.y / self.h * O_size[1])
        try:
            self.MAIN_PROGRAM.mousePos.set('({0}, {1})'.format(X,Y))
            self.MAIN_PROGRAM.Intensity.set(self.IMAGE.Source_Intensity[Y][X])
        except IndexError: pass
        
    def Mouse_B1_Handler(self,event):
        O_size = self.IMAGE.shape[:2]
        self.X = int(event.x / self.w * O_size[0] )
        self.Y = int(event.y / self.h * O_size[1] ) 
        if self.MAIN_PROGRAM.MODE[1]==True: return None
        else:
            if self.MAIN_PROGRAM.MODE[3]==True: #ROI_MOVE
                self.MAIN_PROGRAM.MODE[2] = True #ROI_VISIBLE
                self.MAIN_PROGRAM.ROI_Visible_Bttn.config(relief=TK.SUNKEN)
                for idx in range(len(self.IMAGE.ROI_POINTs)):
                    if self.IMAGE.ROI_POINTs[idx].shape[1]==2:
                        X0, Y0 = self.IMAGE.ROI_POINTs[idx][0][0][0], self.IMAGE.ROI_POINTs[idx][0][0][1]
                        X1, Y1 = self.IMAGE.ROI_POINTs[idx][0][1][0], self.IMAGE.ROI_POINTs[idx][0][1][1]
                        THIS = np.array([[X0,Y0],[X0,Y1],[X1,Y1],[X1,Y0]])
                    else: THIS = self.IMAGE.ROI_POINTs[idx]
                    if cv2.pointPolygonTest(THIS, (self.X, self.Y), True) > 0:
                        self.Drag = True
                        self.Drag_index = idx
                        self.IMAGE.Cur_ROI = idx if self.IMAGE.Cur_ROI!=idx else -1
                        self.Refresh_Image()
                        return None
                self.IMAGE.Cur_ROI = -1
                self.Refresh_Image()
            elif self.MAIN_PROGRAM.MODE[4]==True or self.MAIN_PROGRAM.MODE[5]==True: #ROI_ADD / ROI_ADD2
                self.MAIN_PROGRAM.MODE[2] = True #ROI_VISIBLE
                self.MAIN_PROGRAM.ROI_Visible_Bttn.config(relief=TK.SUNKEN)
                if self.MAIN_PROGRAM.ROI_SHAPE!=0: self.IMAGE.ROI_Current_pts.append((self.X,self.Y))
                                
    def Mouse_B1_Motion_Handler(self, event):
        O_size = self.IMAGE.shape[:2]
        X = int(event.x /self.w * O_size[0])
        Y = int(event.y / self.h * O_size[1])
        try:
            self.MAIN_PROGRAM.mousePos.set('({0}, {1})'.format(X,Y))
            self.MAIN_PROGRAM.Intensity.set(self.IMAGE.Source_Intensity[X][Y])
        except IndexError: pass
        if self.MAIN_PROGRAM.MODE[4]==True or self.MAIN_PROGRAM.MODE[5]==True:
            if self.MAIN_PROGRAM.MODE[4]==True: COLOR = (255,0,0)
            else: COLOR = (0,255,0)
            self.X0, self.Y0 = self.IMAGE.ROI_Current_pts[0][0], self.IMAGE.ROI_Current_pts[0][1]
            self.IMAGE.Create_RGB_IMAGE(self.IMAGE.COPIED)
            if self.MAIN_PROGRAM.ROI_SHAPE==1:
                cv2.rectangle(self.IMAGE.Source_RGB, (self.X0,self.Y0),(X,Y),(255,255,0),1)
            elif self.MAIN_PROGRAM.ROI_SHAPE==2:
                cv2.ellipse(self.IMAGE.Source_RGB, ((self.X0+X)//2,(self.Y0+Y)//2),(abs(X-(self.X0+X)//2),abs(Y-(self.Y0+Y)//2)),0,0,360,(255,255,0),1)
            self.Screen = self.IMAGE.Convert_TK_IMAGE( cv2.resize(self.IMAGE.Source_RGB, (self.w,self.h),interpolation=cv2.INTER_AREA) )
            self.MAIN_SCREEN.config(image=self.Screen)

        elif self.MAIN_PROGRAM.MODE[3]==True and self.Drag==True:
            self.Dragging = True
            self.MAIN_SCREEN.config(cursor='fleur')
            PT = self.IMAGE.ROI_POINTs[self.Drag_index]
            dp = np.array([X-self.X, Y-self.Y])
            self.IMAGE.ROI_POINTs[self.Drag_index] += dp
            self.IMAGE.Cur_ROI = self.Drag_index
            self.Refresh_Image()
            self.X = X
            self.Y = Y
            if self.ROI_LIST_OPEN==True: self.ROI_List.Reload_ROIs()

    def Mouse_B1_Release_Handler(self, event):
        O_size = self.IMAGE.shape[:2]
        X = int(event.x / self.w * O_size[0])
        Y = int(event.y / self.h * O_size[1])
        self.MAIN_SCREEN.config(cursor='crosshair')
        if self.MAIN_PROGRAM.MODE[3]==True and self.Drag==True and self.Dragging==True:
            self.Drag=False
            self.Dragging=False
        elif self.MAIN_PROGRAM.MODE[4]==True or self.MAIN_PROGRAM.MODE[5]==True:
            TYPE = 'Noise' if self.MAIN_PROGRAM.MODE[4]==True else 'Normal'
            if self.MAIN_PROGRAM.ROI_SHAPE==0:
                self.IMAGE.ROI_Current_pts.append((X, Y))
                self.IMAGE.Create_RGB_IMAGE(self.IMAGE.COPIED)
                self.Screen = self.IMAGE.Convert_TK_IMAGE( cv2.resize(self.IMAGE.Source_RGB, (self.w,self.h),interpolation=cv2.INTER_AREA) )
                self.MAIN_SCREEN.config(image=self.Screen)
                return None
            elif self.MAIN_PROGRAM.ROI_SHAPE==1:
                self.IMAGE.ROI_Current_pts.extend([(self.X0,Y),(X,Y),(X,self.Y0)])
                if len(set(self.IMAGE.ROI_Current_pts))!=4:
                    self.IMAGE.ROI_Current_pts = []
                    return None
            else:
                self.IMAGE.ROI_Current_pts.append((X, Y))
                if len(set(self.IMAGE.ROI_Current_pts))!=2:
                    self.IMAGE.ROI_Current_pts = []
                    return None
            if self.ROI_Shared==True: self.MAIN_PROGRAM.Shared_ROI.append(np.array([self.IMAGE.ROI_Current_pts]))
            for i in range(len(self.MAIN_PROGRAM.SUB_WINDOWS)):
                if (self.ROI_Shared==False) and (self.ROI_Global==False and i!=self.INDEX): continue
                if self.ROI_Shared==True: self.MAIN_PROGRAM.SUB_WINDOWS[i].IMAGE.ROI_POINTs.append(self.MAIN_PROGRAM.Shared_ROI[-1])
                else: self.MAIN_PROGRAM.SUB_WINDOWS[i].IMAGE.ROI_POINTs.append(np.array([self.IMAGE.ROI_Current_pts]))

                self.MAIN_PROGRAM.SUB_WINDOWS[i].IMAGE.ROI_TYPEs.append(TYPE)
                self.MAIN_PROGRAM.SUB_WINDOWS[i].Need_Refresh=True
                if i!=self.INDEX: self.MAIN_PROGRAM.SUB_WINDOWS[i].Refresh_Image()
                if self.MAIN_PROGRAM.SUB_WINDOWS[i].ROI_LIST_OPEN==True: self.MAIN_PROGRAM.SUB_WINDOWS[i].ROI_List.Reload_ROIs()
            
            self.IMAGE.ROI_Current_pts, self.MAIN_PROGRAM.ROI_Shared = [], []
            self.Refresh_Image()
    
    def Mouse_B2_Handler(self,event):
        O_size = self.IMAGE.shape[:2]
        X = int(event.x /self.w * O_size[0])
        Y = int(event.y / self.h * O_size[1])
        self.X = X
        self.Y = Y
        self.Drag = True
    
    def Mouse_B2_Motion_Handler(self, event):
        O_size = self.IMAGE.shape[:2]
        X = int(event.x /self.w * O_size[0])
        Y = int(event.y / self.h * O_size[1])
        try:
            self.MAIN_PROGRAM.mousePos.set('({0}, {1})'.format(X,Y))
            self.MAIN_PROGRAM.Intensity.set(self.IMAGE.Source_Intensity[Y][X])
        except IndexError: pass
        if self.MAIN_PROGRAM.MODE[3]==True and self.Drag==True:
            self.MAIN_SCREEN.config(cursor='fleur')
            dp = np.array([X-self.X, Y-self.Y])
            for idx in range(len(self.IMAGE.ROI_POINTs)):
                self.IMAGE.ROI_POINTs[idx] += dp
            self.IMAGE.Need_Refresh=True
            self.IMAGE.Apply_Threshold(-1, True, True)
            self.MAIN_PROGRAM.MODE[2] = True
            self.MAIN_PROGRAM.ROI_Visible_Bttn.config(relief=TK.SUNKEN)
            self.Screen = self.IMAGE.Convert_TK_IMAGE( cv2.resize(self.IMAGE.Source_RGB, (self.w,self.h),interpolation=cv2.INTER_AREA) )
            self.MAIN_SCREEN.config(image=self.Screen)
            self.X = X
            self.Y = Y
            if self.ROI_LIST_OPEN==True:
                self.ROI_List.Reload_ROIs()

    def Mouse_B2_Release_Handler(self, event):
        self.Drag = False
        self.MAIN_SCREEN.config(cursor='crosshair')

    def Mouse_B3_Handler(self, event):
        O_size = self.IMAGE.shape[:2]
        X = int(event.x /self.w * O_size[0])
        Y = int(event.y / self.h * O_size[1])
        self.X, self.Y = X, Y
        self.menubar.entryconfig("ROI 유형 변경",state='disabled')
        self.menubar.entryconfig("ROI 복사",state='disabled')
        self.menubar.entryconfig("ROI 삭제",state='disabled')
        self.menubar.entryconfig("ROI 붙여넣기",state='disabled')
        self.menubar.entryconfig("ROI 여기에 붙여넣기",state='disabled') 
        self.menubar.entryconfig("현재 ROI셋 저장", state='disabled')
        self.menubar.entryconfig("ROI 전부 삭제", state='disabled')
        if len(self.IMAGE.ROI_POINTs)!=0: 
            self.menubar.entryconfig("현재 ROI셋 저장", state='normal')
            self.menubar.entryconfig("ROI 전부 삭제", state='normal')
        if self.MAIN_PROGRAM.Copied==True: 
            if self.INDEX!=self.MAIN_PROGRAM.Copied_From: self.menubar.entryconfig('ROI 붙여넣기', state='normal')
            self.menubar.entryconfig('ROI 여기에 붙여넣기', state='normal')
        for idx in range(len(self.IMAGE.ROI_POINTs)):
            if self.IMAGE.ROI_POINTs[idx].shape[1]==2:
                X0, Y0 = self.IMAGE.ROI_POINTs[idx][0][0][0], self.IMAGE.ROI_POINTs[idx][0][0][1]
                X1, Y1 = self.IMAGE.ROI_POINTs[idx][0][1][0], self.IMAGE.ROI_POINTs[idx][0][1][1]
                THIS = np.array([[X0,Y0],[X0,Y1],[X1,Y1],[X1,Y0]])
            else: THIS = self.IMAGE.ROI_POINTs[idx]
            if cv2.pointPolygonTest(THIS, (self.X,self.Y), True) >0:
                self.menubar.entryconfig('ROI 유형 변경',state='normal')
                self.menubar.entryconfig('ROI 복사', state='normal')
                self.menubar.entryconfig('ROI 삭제', state='normal')
                self.Drag_index = idx
                break
        
        self.menubar.tk_popup(event.x_root, event.y_root, 0)
        self.menubar.grab_release()

    def menubar_handler(self, event):
        print(event.char)
        if event.char == 'q' or event.char=='Q': self.ROI_Copy()
        elif event.char=='w' or event.char=='W': self.RoI_REMOVE()
        elif event.char=='e' or event.char=='E': self.ROI_PASTE()
        elif event.char=='r' or event.char=='R': self.ROI_PASTE_HERE()

    def ROI_Copy(self):
        self.MAIN_PROGRAM.Clipboard = [self.IMAGE.ROI_POINTs[self.Drag_index].copy(), self.IMAGE.ROI_TYPEs[self.Drag_index]]
        self.MAIN_PROGRAM.Copied = True
    
    def ROI_PASTE(self):
        self.IMAGE.ROI_POINTs.append(self.MAIN_PROGRAM.Clipboard[0].copy())
        self.IMAGE.ROI_TYPEs.append(self.MAIN_PROGRAM.Clipboard[1])
        self.IMAGE.Need_Refresh=True
        self.Refresh_Image()
        if self.ROI_LIST_OPEN==True:
            self.ROI_List.Reload_ROIs()

    def ROI_PASTE_HERE(self):
        self.IMAGE.ROI_POINTs.append(self.MAIN_PROGRAM.Clipboard[0].copy()-self.MAIN_PROGRAM.Clipboard[0][0][0]+(self.X,self.Y))
        self.IMAGE.ROI_TYPEs.append(self.MAIN_PROGRAM.Clipboard[1])
        self.IMAGE.Need_Refresh=True
        self.Refresh_Image()
        if self.ROI_LIST_OPEN==True: self.ROI_List.Reload_ROIs()

    def ROI_TYPE_CHANGE(self):
        if self.IMAGE.ROI_TYPEs[self.Drag_index] == 'Normal':
            self.IMAGE.ROI_TYPEs[self.Drag_index]='Noise'
        else: self.IMAGE.ROI_TYPEs[self.Drag_index] = 'Normal'
        self.IMAGE.Need_Refresh=True
        self.Refresh_Image()
        if self.ROI_LIST_OPEN==True:
                self.ROI_List.Reload_ROIs()

    def ROI_REMOVE(self):
        self.IMAGE.ROI_POINTs.pop(self.Drag_index)
        self.IMAGE.ROI_TYPEs.pop(self.Drag_index)
        self.IMAGE.Need_Refresh=True
        self.Refresh_Image()
        if self.ROI_LIST_OPEN==True:
                self.ROI_List.Reload_ROIs()

    def ROI_CLEAR(self):
        self.IMAGE.ROI_POINTs = []
        self.IMAGE.ROI_TYPEs = []
        self.IMAGE.Need_Refresh = True
        self.Refresh_Image()
        if self.ROI_LIST_OPEN==True:
                self.ROI_List.Reload_ROIs()

    def OPEN_ROI_LIST(self):
        if self.ROI_LIST_OPEN == False:
            self.ROI_LIST_OPEN=True
            self.ROI_List = addons.ROI_LIST(self.MAIN_PROGRAM, self, self.IMAGE)

    def ROI_Save_as_File(self):
        ROI_POINTs = self.IMAGE.ROI_POINTs
        ROI_TYPEs = self.IMAGE.ROI_TYPEs
        PICKLE = filedialog.asksaveasfilename(title='ROI셋 저장',filetypes=[('Python Pickle Object File(*.pop)','.pop')],
                            initialfile='ROI_SET_{0}.pop'.format(self.INDEX))
        if PICKLE=='': return None
        try:
            with open(PICKLE, 'wb') as file:
                pickle.dump(ROI_POINTs, file)
                pickle.dump(ROI_TYPEs,file)
            addons.INFO('ROI셋 저장 완료','{0}\nROI셋을 성공적으로 저장하였습니다!'.format(PICKLE))
        except: addons.FATAL_ERROR('ROI셋 저장 실패','ROI셋을 저장하지 못 했습니다!')

    def ROI_Load_from_File(self):
        PICKLE = filedialog.askopenfilename(initialdir=self.MAIN_PROGRAM.default_path, title='ROI셋 불러오기(주의: 현재 ROI셋은 모두 초기화됩니다!)')
        LENGTH = len(self.MAIN_PROGRAM.SUB_WINDOWS)
        if PICKLE=='': return None
        with open(PICKLE, 'rb') as file:
            try:
                ROI_POINTs = pickle.load(file)
                ROI_TYPEs = pickle.load(file)
            except:
                addons.FATAL_ERROR('ROI셋 불러오기 오류!','{0}은 ROI셋 파일이 아니거나 손상된 파일입니다!'.format(PICKLE))
                return None
        if LENGTH!=1: Answer = addons.question(title='ROI셋 전체 반영',what='모든 이미지에 ROI를 반영할까요?')
        else: Answer = False
        if Answer==True:
            for i in range(LENGTH):
                self.MAIN_PROGRAM.SUB_WINDOWS[i].IMAGE.ROI_POINTs = ROI_POINTs
                self.MAIN_PROGRAM.SUB_WINDOWS[i].IMAGE.ROI_TYPEs = ROI_TYPEs
                self.MAIN_PROGRAM.SUB_WINDOWS[i].IMAGE.Need_Refresh = True
                self.MAIN_PROGRAM.SUB_WINDOWS[i].Refresh_Image()
        else:
            self.IMAGE.ROI_POINTs = ROI_POINTs
            self.IMAGE.ROI_TYPEs = ROI_TYPEs
            self.IMAGE.Need_Refresh = True
            self.Refresh_Image()
        if self.ROI_LIST_OPEN==True:
            self.ROI_List.Reload_ROIs()

    def Color_Mapping(self):
        self.IMAGE.Apply_Threshold(-1,force=True, refresh_noise=True)
        self.WIZARD = addons.WIZARD(self.IMAGE)
            
        
############################################################
if __name__ == '__main__':
    import cv2, pydicom, os, math, pickle, time
    import addons
    import tkinter as TK
    import tkinter.ttk as ttk
    import numpy as np
    import matplotlib.pyplot as plt
    from PIL import Image, ImageTk
    from tkinter import filedialog, Tk, ttk, messagebox, Menu

    TEST_MODE = False
    if TEST_MODE==True: print('테스트 모드로 실행 중입니다.')
    MAIN_PROGRAM = MAIN_WINDOW()
############################################################