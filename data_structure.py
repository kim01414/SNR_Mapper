import pydicom as pyd
import nibabel as nib
import numpy as np, seaborn as sns
import cv2, os
import warnings
from skimage.draw import polygon, ellipse
import matplotlib.pyplot as plt 
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont

#warnings.filterwarnings("error")
PLOT_COLOR =  ['red' ,'blue','orange','green','purple','brown',
               'pink','gray','olive' ,'cyan' ,'navy'  ,'khaki',
               'lightblue','gold','violet', 'khaki', 'turquoise', 'thistle']

class IMAGES:
    def __init__(self):
        self.IMGs = None
        self.FILE_TYPE = None
        self.Name = 'TITLE'
        self.FILE_PATH = []
        self.IMGs_Display = []
        self.ROI_Intensities = {} 
        for i in range(len(PLOT_COLOR)): self.ROI_Intensities[i] = []
    
    def DICOM_IMPORTER(self, PATH):
        try:
            if 'nptmp' not in PATH: 
                FILE = pyd.dcmread(PATH)
                self.IMGs = FILE.pixel_array.copy();    
            else: self.IMGs = np.load(PATH)
            W,H = self.IMGs.shape[0], self.IMGs.shape[1]
            if W!=H:
                diff = abs(W-H)
                if W>H: 
                    self.IMGs = np.hstack([self.IMGs, np.zeros((W,diff//2)).astype(self.IMGs.dtype)])
                    self.IMGs = np.hstack([np.zeros((W,diff//2)).astype(self.IMGs.dtype), self.IMGs])
                else  : 
                    self.IMGs = np.vstack([self.IMGs, np.zeros((diff//2,H)).astype(self.IMGs.dtype)])
                    self.IMGs = np.vstack([np.zeros((diff//2,H)).astype(self.IMGs.dtype),self.IMGs])
            self.IMGs = np.expand_dims(self.IMGs, axis=-1)
            self.FILE_TYPE = 'DICOM'
            self.FILE_PATH.append(PATH)
            return True
        except: 
            messagebox.showerror('오류!','{0}은\n 정상적인 이미지 파일이 아닙니다!'.format(PATH))
            return False

    def CNR_MAPPING(self, ROIs):
        self.MASK = np.zeros_like(self.IMGs)
        self.Backgrounds = []; self.Reference = []; self.Values = []
        for ROI in ROIs:
            if ROI.ROI_TYPE_src == 1  : self.Backgrounds.extend(self.IMGs[np.where(ROI.MASK==1)])
            elif ROI.ROI_TYPE_src == 2: self.Reference.extend(self.IMGs[np.where(ROI.MASK==1)])
            else                      : 
                self.Values.extend(self.IMGs[np.where(ROI.MASK==1)])
                self.MASK[np.where(ROI.MASK==1)] = 1
        self.Values = np.array(self.Values)
        cmap = sns.color_palette('gnuplot', int(self.Values.max()-self.Values.min()+1), as_cmap=False)
        MAP = np.dstack([self.IMGs, self.IMGs, self.IMGs])
        BCK = np.array(self.Backgrounds).std()
        SNR = self.IMGs / BCK
        coords = np.where(self.MASK==1)
        Y, X = coords[0], coords[1]
        REF =  np.array(self.Reference).mean() / BCK
        CNR = SNR - REF
        
        for y,x in zip(Y,X):
            INT = MAP[y,x,0] - self.Values.min()
            print(type(INT),INT.dtype)
            CNR[y,x,:] = [cmap[INT]*CNR[y,x,0],cmap[INT]*CNR[y,x,0],cmap[INT]*CNR[y,x,0]]        
        
        return CNR

    def Convert_DISPLAY(self, index=-1):
        for idx in range(0 if index==-1 else index, self.IMGs.shape[-1] if index==-1 else index+1):
            src = (self.IMGs[:,:,idx] / self.IMGs[:,:,idx].max() * 255).astype(np.uint8)
            display = ImageTk.PhotoImage( Image.fromarray( cv2.resize(src,(650,650),interpolation=cv2.INTER_AREA) ) )
            if index==-1: self.IMGs_Display.append(display)
            else: self.IMGs_Display[index] = display

    def Measure_ROI(self, Index):
        for i in range(self.IMGs.shape[-1]):
            THIS = self.IMGs[:,:,i]
            THIS = THIS[np.where(self.ROI_array[:,:,Index])==1].mean()
            self.ROI_Intensities[Index].append(THIS)

    def Delete_ROI(self, Index):
        self.ROIs.ROI_Using[Index] = False
        self.ROIs.ROI_array[:,:,Index] = np.zeros((self.HEIGHT,self.WIDTH))
        self.ROIs.ROI_for_TK[Index] = []
        self.ROI_Intensities[Index] = []

class ROI:
    def __init__(self, shape, type_src):
        self.HEIGHT, self.WIDTH = shape[0], shape[1]
        self.MASK = np.zeros((self.HEIGHT, self.WIDTH)).astype(np.uint8)
        self.Intensities = []
        self.ROI_TYPE_src = type_src #1: Background, 2: Reference, 3: Material
    
    def Make_ROI(self, TYPE, ROI_X, ROI_Y, ROI_for_TK, TK_INDEX): 
        self.ROI_TYPE = TYPE
        self.TK_INDEX = TK_INDEX
        self.ROI_X, self.ROI_Y = ROI_X, ROI_Y
        self.ROI_X2, self.ROI_Y2 = (ROI_X / 650 * self.WIDTH).astype(np.uint32), (ROI_Y / 650 * self.HEIGHT).astype(np.uint32)
        self.ROI_for_TK = ROI_for_TK
        if TYPE == 'ROI_CIRCLE':
            CENTER_X, CENTER_Y =  int((self.ROI_X2[0]+self.ROI_X2[1])//2), int((self.ROI_Y2[0]+self.ROI_Y2[1])//2)
            X, Y = ellipse(CENTER_X, CENTER_Y, abs(self.ROI_X2[0]-CENTER_X), abs(self.ROI_Y2[0]-CENTER_Y) )
        else: X, Y = polygon(self.ROI_X2,self.ROI_Y2)
        self.Draw_ROI(X, Y)

    def Measure_ROI(self, src): 
        self.Intensities = []
        try:
            THIS = src
            if len(THIS[self.MASK==1])==0: raise ValueError
            self.Intensities = THIS[self.MASK==1]
            return True
        except: 
            print('Invalid ROI was ignored...')
            return False
        
    def Draw_ROI(self, X, Y):
        for i in range(len(X)):
            if X[i]<self.WIDTH and Y[i]<self.HEIGHT: self.MASK[Y[i],X[i]] = 1

    def MOVE_ROI(self, dx, dy, Done=False):
        if Done==True: self.ROI_X2, self.ROI_Y2  = [], []
        if self.ROI_TYPE=='ROI_CIRCLE':
            self.ROI_for_TK[0], self.ROI_for_TK[2] = self.ROI_for_TK[0]+dx, self.ROI_for_TK[2]+dx
            self.ROI_for_TK[1], self.ROI_for_TK[3] = self.ROI_for_TK[1]+dy, self.ROI_for_TK[3]+dy
            if Done: 
                self.ROI_X2 = np.array([self.ROI_for_TK[0], self.ROI_for_TK[2]]) / 650 * self.WIDTH
                self.ROI_Y2 = np.array([self.ROI_for_TK[1], self.ROI_for_TK[3]]) / 650 * self.HEIGHT
                CENTER_X, CENTER_Y =  int((self.ROI_X2[0]+self.ROI_X2[1])//2), int((self.ROI_Y2[0]+self.ROI_Y2[1])//2)
                X, Y = ellipse(CENTER_X, CENTER_Y, abs(self.ROI_X2[0]-CENTER_X), abs(self.ROI_Y2[0]-CENTER_Y) )
        else:
            for i in range(len(self.ROI_for_TK)):
                self.ROI_for_TK[i] += dx if i%2==0 else dy
                if i%2==0 and Done: self.ROI_X2.append(int(self.ROI_for_TK[i]/650*self.WIDTH))
                elif i%2!=0 and Done: self.ROI_Y2.append(int(self.ROI_for_TK[i]/650*self.HEIGHT))
            if Done==True:
                self.ROI_X2,self.ROI_Y2 = np.array(self.ROI_X2),np.array(self.ROI_Y2) 
                X, Y = polygon(self.ROI_X2,self.ROI_Y2)       
        if Done:self.MASK = np.zeros((self.HEIGHT, self.WIDTH)).astype(np.uint8); self.Draw_ROI(X, Y)#self.MASK[Y,X] = 1

    def EDIT_ROI(self, cp, dx, dy, Done=False):
        self.ROI_X2, self.ROI_Y2  = [], []
        if self.ROI_TYPE=='ROI_CIRCLE':
            self.ROI_for_TK = np.array([self.ROI_for_TK[0] + (dx if cp==1 else 0), 
                                        self.ROI_for_TK[1] + (dy if cp==0 else 0), 
                                        self.ROI_for_TK[2] + (dx if cp==3 else 0), 
                                        self.ROI_for_TK[3] + (dy if cp==2 else 0)])
            if Done:
                self.ROI_X2 = np.array([self.ROI_for_TK[0], self.ROI_for_TK[2]]) / 650 * self.WIDTH
                self.ROI_Y2 = np.array([self.ROI_for_TK[1], self.ROI_for_TK[3]]) / 650 * self.HEIGHT
                CENTER_X, CENTER_Y =  int((self.ROI_X2[0]+self.ROI_X2[1])//2), int((self.ROI_Y2[0]+self.ROI_Y2[1])//2)
                X, Y = ellipse(CENTER_X, CENTER_Y, abs(self.ROI_X2[0]-CENTER_X), abs(self.ROI_Y2[0]-CENTER_Y) )
        elif self.ROI_TYPE=='ROI_RECT':
            X1, Y1, X2, Y2 = (self.ROI_for_TK[0] + (dx if (cp==0 or cp==1) else 0), 
                              self.ROI_for_TK[1] + (dy if (cp==0 or cp==3) else 0), 
                              self.ROI_for_TK[4] + (dx if (cp==2 or cp==3) else 0), 
                              self.ROI_for_TK[5] + (dy if (cp==1 or cp==2) else 0))
            self.ROI_for_TK = np.array([X1,Y1,X1,Y2,X2,Y2,X2,Y1])
            for i in range(len(self.ROI_for_TK)):
                if i%2==0 and Done: self.ROI_X2.append(int(self.ROI_for_TK[i]/650*self.WIDTH))
                elif i%2!=0 and Done: self.ROI_Y2.append(int(self.ROI_for_TK[i]/650*self.HEIGHT))
            if Done==True:
                self.ROI_X2,self.ROI_Y2 = np.array(self.ROI_X2),np.array(self.ROI_Y2) 
                X, Y = polygon(self.ROI_X2,self.ROI_Y2)       
        elif self.ROI_TYPE=='ROI_POLY':
            self.ROI_for_TK[ cp*2 ] += dx
            self.ROI_for_TK[cp*2+1] += dy
            for i in range(len(self.ROI_for_TK)):
                if i%2==0 and Done: self.ROI_X2.append(int(self.ROI_for_TK[i]/650*self.WIDTH))
                elif i%2!=0 and Done: self.ROI_Y2.append(int(self.ROI_for_TK[i]/650*self.HEIGHT))
            if Done==True:
                self.ROI_X2,self.ROI_Y2 = np.array(self.ROI_X2),np.array(self.ROI_Y2) 
                X, Y = polygon(self.ROI_X2,self.ROI_Y2)   
        if Done: self.MASK = np.zeros((self.HEIGHT, self.WIDTH)).astype(np.uint8); self.Draw_ROI(X, Y)#self.MASK[Y,X] = 1
    
    def SAVE_ROI(self):
        return [self.ROI_X if type(self.ROI_X)==type(list) else self.ROI_X.tolist(), #ROI_X
                self.ROI_Y if type(self.ROI_Y)==type(list) else self.ROI_Y.tolist(), #ROI_Y
               self.ROI_for_TK, self.ROI_TYPE, self.ROI_TYPE_src]                    #ROI_TK, ROI_Shape, ROI_TYPE