# -*- coding: utf-8 -*-
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import sys

# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')

app = QtGui.QApplication([])

def image(data):
    ## Create window with ImageView widget
    win = QtGui.QMainWindow()
    win.resize(800,800)
    imv = pg.ImageView()
    win.setCentralWidget(imv)
    win.show()
    win.setWindowTitle('testplot')

    imv.setImage(data, levels=(0,0.012))

    ## Start Qt event loop unless running in interactive mode.
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

#TODO always go through entire list, annotate values, even if one list 
#is smaller
class compareWindow(pg.GraphicsWindow):

    def __init__(self, data_list, kwargs_list=None, titles_list: list =[], size=(800,600), *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        l = pg.GraphicsLayout(border=(100,100,100))
        self.setCentralItem(l)
        self.show()
        self.setWindowTitle('combination imp plot')
        self.resize(size[0],size[1])

        self.data_list = data_list
        self.titles_list = titles_list
        
        if (kwargs_list == None):
            self.kwargs_list = [{} for i in data_list]
        else:
            self.kwargs_list = kwargs_list
        
        self.plotCounter = 0
        self.images = []

        
        #array is not a good name FIXME
        for (i, (array,kwargs)) in enumerate(zip(data_list,kwargs_list)):
            
            if not isinstance(kwargs, dict):
                kwargs_list[i] = {}
                kwargs = {}
            
            if not isinstance(array, list):
                data_list[i] = [array]
                array = [array]
                
            vb = l.addViewBox(lockAspect=True)                
            img = pg.ImageItem(array[0], **kwargs)
            vb.addItem(img)
            vb.autoRange()
            self.images.append(img)
        
        #self.setWindowTitle(titles_list[0][2])
        #Fixme
        # if len(titles_list[0]) == len(self.images):
            # #l.nextRow()
            # l2 = l.addLayout(colspan=len(self.images), border=(0,0,0))
            # for i,title in enumerate(titles_list[0]):
                # l2.addLabel(title, col=i, colspan=1)
                # print(i)
    
    def keyPressEvent(self, event):
        self.scene().keyPressEvent(event)
        if (event.key()==QtCore.Qt.Key_Tab): 
            self.nextImage()
        elif (event.key()==QtCore.Qt.Key_C):
            QtGui.QApplication.quit()
        
    def nextImage(self):
        self.plotCounter += 1
        if self.plotCounter > min([len(i) for i in self.data_list])-1:
            self.plotCounter = 0

        #self.setWindowTitle(self.titles_list[self.plotCounter][2])            
        for (img, array, kwargs) in zip(self.images,self.data_list, self.kwargs_list):
            img.setImage(array[self.plotCounter], **kwargs)

def compare(data, titles=[]):

    #TODO do some sanity checks on input
    
    kwargs_list = [
      {"levels": (0,0.01)},
      {"levels": (0,8000)},]
      
    view = compareWindow(data, kwargs_list=kwargs_list, size=(1800,800), titles_list=titles)
    
    ## Start Qt event loop/show the plot
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
