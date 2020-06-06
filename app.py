import sys
from smpl_np import SMPLModel

import numpy as np
import trimesh

from viewerUI import Ui_SmplViewer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        # GUI
        self.ui = Ui_SmplViewer()
        self.ui.setupUi(self)

        # SMPL object
        self.smpl = SMPLModel('./smpl_data/male_model.pkl')

        # initialize the sliders
        self.poseSliders = []
        self.shapeSliders = []
        for item in self.ui.__dict__:
            if 'horizontalSlider' in item:
                self.poseSliders.append(self.ui.__dict__[item])
            if 'verticalSlider' in item:
                self.shapeSliders.append(self.ui.__dict__[item])

        # set events
        for i in range(len(self.poseSliders)):
            self.poseSliders[i].setMinimum(-8);
            self.poseSliders[i].setMaximum(8);
            self.poseSliders[i].valueChanged[int].connect(self.changevalue)

        for i in range(len(self.shapeSliders)):
            self.shapeSliders[i].setMinimum(0);
            self.shapeSliders[i].setMaximum(10);
            self.shapeSliders[i].valueChanged[int].connect(self.changevalue)

        self.ui.pushButton.clicked.connect(self.pushButton_Click)

    def loadScene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        x, y, width, height = glGetDoublev(GL_VIEWPORT)
        gluPerspective(
            45,  # field of view in degrees
            width / float(height or 1),  # aspect ratio
            .25,  # near clipping plane
            200,  # far clipping plane
        )

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        gluLookAt(1.8, 1.8, 1.8, 0, 0, 0, 0, 1, 0)

    def paintGL(self):

        self.loadScene()
        for face in self.smpl.faces:
            glColor3f(1, 1, 0.4)
            glBegin(GL_TRIANGLES);
            x_0, y_0, z_0 = self.smpl.verts[face[0]]
            x_1, y_1, z_1 = self.smpl.verts[face[1]]
            x_2, y_2, z_2 = self.smpl.verts[face[2]]
            glVertex3f(x_0, y_0, z_0);
            glVertex3f(x_1, y_1, z_1);
            glVertex3f(x_2, y_2, z_2);
            glEnd()

        self.setupRC()

    def setupViewer(self):
        self.ui.openGLWidget.initializeGL()
        self.ui.openGLWidget.paintGL = self.paintGL
        timer = QTimer(self)
        timer.timeout.connect(self.ui.openGLWidget.update)
        timer.start(5)

    def setupRC(self):
        # Light values and coordinates
        ambientLight = [0.4, 0.4, 0.4, 1.0 ]
        diffuseLight = [0.7, 0.7, 0.7, 1.0 ]
        specular = [ 0.9, 0.9, 0.9, 1.0]
        lightPos = [ -0.03, 0.15, 0.1, 1.0]
        specref =  [ 0.6, 0.6, 0.6, 1.0]

        glEnable(GL_DEPTH_TEST)    # Hidden surface removal
        glEnable(GL_CULL_FACE)    # Do not calculate inside of solid object
        glFrontFace(GL_CCW)

        glEnable(GL_LIGHTING)

        # Setup light 0
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambientLight)
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLight)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuseLight)
        glLightfv(GL_LIGHT0, GL_SPECULAR, specular)

        # Position and turn on the light
        glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
        glEnable(GL_LIGHT0)

        # Enable color tracking
        glEnable(GL_COLOR_MATERIAL)

        # Set Material properties to follow glColor values
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

        # All materials hereafter have full specular reflectivity with a moderate shine
        glMaterialfv(GL_FRONT, GL_SPECULAR,specref)
        glMateriali(GL_FRONT,GL_SHININESS,64)

    def changevalue(self, value):
        pose_vals = []
        shape_vals = []
        for i in range(24):
            vector = np.zeros(3)
            vector[0] = 3 * self.poseSliders[3 * i + 0].value() / 8
            vector[1] = 3 * self.poseSliders[3 * i + 1].value() / 8
            vector[2] = 3 * self.poseSliders[3 * i + 2].value() / 8
            pose_vals.append(vector)

        for item in self.shapeSliders:
            shape_vals.append(item.value())

        pose_vals = np.array(pose_vals)
        shape_vals = np.array(shape_vals)
        trans_vals = np.zeros(3)
        self.smpl.set_params(pose = pose_vals, beta = shape_vals, trans = trans_vals)

    # save the model
    def pushButton_Click(self):
        mesh = trimesh.Trimesh(vertices = self.smpl.verts, faces = self.smpl.faces, process = False)
        output_path = self.ui.lineEdit.text()
        mesh.export(output_path)
        print ('Saved to %s' % output_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.setupViewer()
    w.show()
    sys.exit(app.exec_())
