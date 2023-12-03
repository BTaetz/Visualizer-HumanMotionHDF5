import h5py
from PyQt5.QtWidgets import QApplication, QShortcut, QMainWindow #, QPushButton, QVBoxLayout, QWidget
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
import pyqtgraph.opengl as gl
from pyqtgraph import Transform3D
from utils.customClasses import GLAxisItemOwn, SegmentItem
import numpy as np
import pyqtgraph as pg
from utils.trafos import quaternion_matrix4x4
from collections import deque
import sys

class Plots2D():

    def __init__(self, segName, components):
        self.vis2D = {}
        self.windowWidth = 300  # width of the window displaying the curve
        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        self.ID = segName
        self.pl = []
        self.curves = {}
        self.nPlotLines = 3
        self.vis2D = pg.GraphicsLayoutWidget(title="Data - " + segName)
        self.vis2D.resize(600, 300)
        self.vis2D.setWindowTitle('Data - ' + segName)
        self.components = components
        self.dataLines = {}

        for p, key in enumerate(self.components):
            # plotting references for component p
            self.pl.append(self.vis2D.addPlot(title=key, pen='y'))
            self.dataLines[key] = []
            # array with deque for each coordinate line of each component that will be filled with new data
            for l in range(self.nPlotLines):
                self.dataLines[key].append(deque(np.zeros(self.windowWidth)))  # create array that will contain the relevant time series
            self.curves[key] = []
            # plot references that receive the data from the deque
            self.curves[key].append(self.pl[p].plot(pen=(255, 0, 0), name="Red curve", width=2.))
            self.curves[key].append(self.pl[p].plot(pen=(0, 255, 0), name="Green curve", width=2.))
            self.curves[key].append(self.pl[p].plot(pen=(0, 0, 255), name="Blue curve", width=2.))


class Viewer():
    def __init__(self, visDataSeg2D = []):
        self.app = QApplication([])
        #pg.setConfigOption('background', 'w')
        self.view = gl.GLViewWidget()
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self.view)
        quit_shortcut.activated.connect(self.quit_application)
        #self.view.setBackgroundColor('w')
        # create floor
        self.grid = gl.GLGridItem()
        self.view.addItem(self.grid)
        # create global origin
        self.origin = GLAxisItemOwn(size=QtGui.QVector3D(0.5,0.5,0.5))
        self.view.addItem(self.origin)
        self.skels = []
        self.dataDicts = []
        self.plots2D = {}
        self.dict2D = visDataSeg2D
        for segName in visDataSeg2D:
            self.plots2D[segName] = Plots2D(segName, ['acc_i', 'gyr_i', 'mag_i'])

        self.app.setApplicationDisplayName("Quit with Ctrl+q")
    #def __exit__(self):
    #    self.app.quit()
    #    sys.exit(self.app.exec_())

    def quit_application(self):
        # This method will be called when the shortcut is activated
        QApplication.quit()

    def start(self):
        self.app.exec_()
        self.view.show()



    def getOrigin(self):
        return self.origin

    def setSkeleton(self, skel):
        self.skels.append(skel)
        for n in range(len(skel.segs)):
            if self.skels[-1].setSegs:
                self.view.addItem(self.skels[-1].segs[n])

            if self.skels[-1].setIMUs:
                self.view.addItem(self.skels[-1].imus[n])

    def update(self):
        for skel, aData in zip(self.skels, self.dataDicts):
            if (self.t < aData["nFrames"]):
                skel.update(aData, self.t)
                #print("Skel: " + skel.Id + " Timestep: " + str(self.t) + " of total: " + str(aData["nFrames"]))
            else:
                self.t = 0 # repeat

            # visualize 2D data if segments are selected!
            if ((self.t < aData["nFrames"]) and (len(self.dict2D) > 0)):
                for segName in self.plots2D.keys():
                    segIdxGl = list(skel.segNames).index(segName)
                    for (cIdx, comp) in enumerate(self.plots2D[segName].components):
                        # fill new data into queues for each coordinate of the component
                        for l in range(self.plots2D[segName].nPlotLines):
                            self.plots2D[segName].dataLines[comp][l].append(aData[segName + "_" + comp][self.t, l])
                            self.plots2D[segName].dataLines[comp][l].popleft()
                            self.plots2D[segName].curves[comp][l].setData(np.asarray(self.plots2D[segName].dataLines[comp][l]))
                            self.plots2D[segName].curves[comp][l].setPos(self.t,0)
                    self.plots2D[segName].vis2D.show()

        self.view.show()
        self.t += 1
        QtCore.QTimer.singleShot(1, self.update)

    def animate(self, list_aDicts):
        self.t = 0
        self.dataDicts = list_aDicts
        self.update()
        self.start()

class emptyClass:
    pass

class DrawSkeleton():
    def __init__(self, viewer, skelDict, colorVec = [0,1, 1, 1.0], origin=[], nameId = "NoName", setIMUs = True, setSegs = True):
        self.segNames = skelDict["segNames"]
        self.jointNames = skelDict["listJointNamesAndConnPtIdx"]
        self.segs = [emptyClass() for i in range(len(skelDict["segNames"]))]
        self.imus = [emptyClass() for i in range(len(skelDict["segNames"]))]
        self.Trafos = [Transform3D() for i in range(len(skelDict["segNames"]))]
        self.Id = nameId
        self.setIMUs = setIMUs
        self.setSegs = setSegs
        self.viewer = viewer
        self.points = np.random.rand(len(self.jointNames), 3)
        self.scatter = gl.GLScatterPlotItem(pos=self.points, size=0.05,color=[1.0,0.0,0.0,1.0], pxMode=False)
        self.viewer.view.addItem(self.scatter)

        for (n, segName) in enumerate(skelDict["segNames"]):
            #listPoints = []#skelDict[segName + "_pSeg_s"]
            listPoints = []
            if self.setSegs:
                #if ("Foot" in segName):
                #    listPoints = skelDict[segName + "_pSeg_s"]
                self.segs[n] = SegmentItem(colorVec=colorVec, size=QtGui.QVector3D(0.1,0.1,0.1), listEndPts=listPoints)
                self.segs[n].setParent(origin)

            if self.setIMUs:
                self.imus[n] = GLAxisItemOwn(size=QtGui.QVector3D(0.05, 0.05, 0.05))
                self.imus[n].setParent(origin)

    def update(self, dataDict, t):
        for (n, segName) in enumerate(self.segNames):
            #self.segs[n].setTransform(np.expand_dims(dataDict[segName + "_TrafoSeg"][:, t], axis=0))
            if self.setSegs:
                self.segs[n].setTransform(QtGui.QMatrix4x4(dataDict[segName + "_TrafoSeg"][:, t]))

            if self.setIMUs:
                self.imus[n].setTransform(QtGui.QMatrix4x4(dataDict[segName + "_TrafoIMU"][:, t]))

            # update joint positions
            self.scatter.setData(pos=np.array(dataDict["j_n"][t, :]).reshape(len(self.jointNames), 3), size=0.05, color=[1.0,0.0,0.0,1.0], pxMode=False)

class HDF5Vis():
    def __init__(self, args):
        self.args = args
        self.dataDict = {}
        self.skelDict = {}
        # init viewer
        self.viewer = Viewer(visDataSeg2D=self.args.showIMUData)

        # load skeleton and data to dicts
        self.loadData()

        # create draw skeletons
        self.skel = DrawSkeleton(self.viewer, self.skelDict, colorVec=[0, 1, 1, 1.0], origin=self.viewer.getOrigin(), nameId="DefaultSkel", setIMUs= not self.args.doNotshowIMUs, setSegs= not self.args.doNotshowSegs)
        self.viewer.setSkeleton(self.skel)

    def compute4x4TrafoMatrix(self, quatStr, posStr, trafoLabel):
        # compute 4x4 transformation matrix from pose data
        for segName in self.skelDict["segNames"]:
            self.dataDict[segName + trafoLabel] = np.zeros((16, self.dataDict["nFrames"]))
            segIdx = list(self.skelDict["segNames"]).index(segName)
            for t in range(self.dataDict["nFrames"]):
                T = quaternion_matrix4x4(self.dataDict[quatStr][t, segIdx*4:(segIdx+1)*4])
                T[0:3, 3] = self.dataDict[posStr][t, segIdx*3:(segIdx+1)*3]
                self.dataDict[segName + trafoLabel][:, t] = np.asarray(T.reshape(16))

    def loadData(self):

        try:
            self.f = h5py.File(self.args.hdf5File, 'r')
        except:
            raise Exception("Could not open file: " + self.args.hdf5File)
            return

        # load skeleton data
        self.skelDict["segNames"] = self.f["/skeleton"].attrs["listSegNames"]
        self.skelDict["listJointNamesAndConnPtIdx"] = self.f["/skeleton"].attrs["listJointNamesAndConnPtIdx"]

        for segName in self.skelDict["segNames"]:
            self.skelDict[segName + "_i_s"] = self.f["skeleton/segment_" + segName + "/i_s"]
            self.skelDict[segName + "_pSeg_s"] = self.f["skeleton/segment_" + segName + "/pSeg_s"]
            self.skelDict[segName + "_quat_si"] = self.f["skeleton/segment_" + segName + "/quat_si"]

        # pose sequences
        self.dataDict["j_n"] = np.asarray(self.f["/data/j_n"])  # joint position sequence of all joints in nativation frame N
        self.dataDict["s_n"] = np.asarray(self.f["/data/s_n"])  # segment position sequence of all segments in nativation frame N
        self.dataDict["quat_ns"] = np.asarray(self.f["/data/quat_ns"]) # orientation sequence (quaternion) for all segments in
                                                            # nativation frame N

        self.dataDict["nFrames"] = self.dataDict["quat_ns"].shape[0]

        # compute 4x4 transformation matrix from pose data
        self.compute4x4TrafoMatrix(quatStr ="quat_ns", posStr ="s_n", trafoLabel ="_TrafoSeg")

        # imu pose sequences
        if (not self.args.doNotshowIMUs):
            self.dataDict["i_n"] = np.asarray(self.f["/data/i_n"]) # imu positions sequence of all imus in natigation frame
            self.dataDict["quat_ni"] = np.asarray(self.f["/data/quat_ni"]) # orientation sequence of all imus in navigation frame
            self.compute4x4TrafoMatrix(quatStr="quat_ni", posStr="i_n", trafoLabel="_TrafoIMU")

        # imu data for selected segments
        for segName in self.args.showIMUData:
            if (segName in self.skelDict["segNames"]):
                imuIdx = list(self.skelDict["segNames"]).index(segName)
                self.dataDict[segName + "_acc_i"] = np.asarray(self.f["/data/acc_i"][:, imuIdx*3:(imuIdx+1)*3])
                self.dataDict[segName + "_gyr_i"] = np.asarray(self.f["/data/gyr_i"][:, imuIdx*3:(imuIdx+1)*3])
                self.dataDict[segName + "_mag_i"] = np.asarray(self.f["/data/mag_i"][:, imuIdx*3:(imuIdx+1)*3])

        self.f.close()

    def animateSkel(self):

        # go through sequence and update skeleton
        self.viewer.animate([self.dataDict])

