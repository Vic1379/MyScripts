import sys, random, os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

PATH = os.path.dirname(os.path.abspath(__file__))

COLORS = (
'#000000', '#141923', '#414168', '#3a7fa7', '#35e3e3', '#8fd970', '#5ebb49', '#458352', '#dcd37b', '#fffee5',
'#ffd035', '#cc9245', '#a15c3e', '#a42f3b', '#f45b7a', '#c24998', '#81588d', '#bcb0c2', '#ffffff',
)

def bytesToPix(s, x, y, w):
    i = 4*(y*w+x)
    return s[i:i+3]

def chAlias():
    if ui.chbAlias.isChecked(): canvas.alias = True
    else: canvas.alias = False

class QPaletteButton(QtWidgets.QPushButton):
    def __init__(self, color):
        super().__init__()
        self.setFixedSize(QtCore.QSize(25, 25))
        # style = 'border-radius: 5px;'
        self.setStyleSheet('background-color: %s;' % color)

class Canvas(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        global width, height
        pm = QtGui.QPixmap(width, height)
        pm.fill(Qt.white)
        self.setPixmap(pm)
        self.backup, self.state = [pm.toImage()], 1

        self.pen_color, self.pen_size = QtGui.QColor('#000000'), 3
        self.nop, self.diameter = 100, 10
        self.mode, self.alias = 'pen', True

        self.last_x, self.last_y = None, None
        self.begin, self.end = QtCore.QPoint(), QtCore.QPoint()
        self.sh_drawing = False

    def set_pen_color(self, c): self.pen_color = QtGui.QColor(c)
    def set_pen_size(self, n): self.pen_size = n
    def set_mode(self, md): self.mode = md
    def set_spray(self, n, d):
        if n: self.nop = n
        if d: self.diameter = d

    def get_pen(self, painter):
        pen = painter.pen()
        if self.mode == 'spray': pen.setWidth(1)
        elif self.mode =='ers': pen.setWidth(self.pen_size+3)
        else: pen.setWidth(self.pen_size)
        if self.mode == 'ers': pen.setColor(Qt.white)
        else: pen.setColor(self.pen_color)
        if self.alias:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        return pen
    
    def get_fill_points(self, process, tg_col, checked, w, h, painter, s):
        new_points = set()
        for x, y in process:
            for i, j in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                dx, dy = x+i, y+j
                if dx>=0 and dx<w and dy>=0 and dy<h and (dx, dy) not in checked:
                    if bytesToPix(s, dx, dy, w) == tg_col:
                        painter.drawPoint(dx, dy)
                        new_points.add((dx, dy))
                    checked.add((dx, dy))
        return new_points
    
    def add_state(self):
        self.backup = self.backup[:self.state]
        self.backup.append(self.pixmap().toImage())
        self.state += 1
        if len(self.backup) > 10:
            self.backup = self.backup[1:]
            self.state -= 1
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.drawPixmap(QtCore.QPoint(), self.pixmap())
        painter.setPen(self.get_pen(painter))
        if self.sh_drawing:
            if self.mode == 'line':
                painter.drawLine(QtCore.QLine(self.begin, self.end))
            elif self.mode == 'rect':
                painter.drawRect(QtCore.QRect(self.begin, self.end))
            elif self.mode == 'elli':
                painter.drawEllipse(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        if self.mode == 'pen' or self.mode == 'ers':
            painter = QtGui.QPainter(self.pixmap())
            painter.setPen(self.get_pen(painter))
            painter.drawPoint(event.x(), event.y())
        elif self.mode == 'spray':
            painter = QtGui.QPainter(self.pixmap())
            painter.setPen(self.get_pen(painter))
            for _ in range(self.nop):
                dx = random.gauss(0, self.diameter)
                dy = random.gauss(0, self.diameter)
                painter.drawPoint(event.x()+int(dx), event.y()+int(dy))
        elif self.mode == 'fill':
            img = self.pixmap().toImage()
            x, y, w, h = event.x(), event.y(), img.width(), img.height()
            s = img.bits().asstring(4*w*h)
            tg_col = bytesToPix(s, x, y, w)
            checked, process, f = set(), set(), True
            process.add((x, y))
            painter = QtGui.QPainter(self.pixmap())
            painter.setPen(self.pen_color)
            painter.drawPoint(x, y)
            checked.add((x, y))
            while f:
                new_points = self.get_fill_points(process, tg_col, checked, w, h, painter, s)
                if new_points: process = new_points
                else: f = False
        else:
            self.sh_drawing = True
            self.begin, self.end = event.pos(), event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        x, y = event.x(), event.y()
        if self.mode == 'pen' or self.mode == 'ers':
            if self.last_x is None: self.last_x, self.last_y = x, y
            painter = QtGui.QPainter(self.pixmap())
            painter.setPen(self.get_pen(painter))
            painter.drawLine(self.last_x, self.last_y, x, y)
            self.last_x, self.last_y = x, y
        elif self.mode == 'spray':
            painter = QtGui.QPainter(self.pixmap())
            painter.setPen(self.get_pen(painter))
            for _ in range(self.nop):
                dx = random.gauss(0, self.diameter)
                dy = random.gauss(0, self.diameter)
                painter.drawPoint(x+int(dx), y+int(dy))
        else:
            self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if self.mode == 'pen' or self.mode == 'ers' or self.mode == 'spray':
            self.last_x = None
            self.last_y = None
        else:
            painter = QtGui.QPainter(self.pixmap())
            painter.setPen(self.get_pen(painter))
            if self.mode == 'line':
                painter.drawLine(QtCore.QLine(self.begin, self.end))
            elif self.mode == 'rect':
                painter.drawRect(QtCore.QRect(self.begin, self.end))
            elif self.mode == 'elli':
                painter.drawEllipse(QtCore.QRect(self.begin, self.end))
            self.sh_drawing = False
        self.update()
        self.add_state()
    
    def save(self):
        filePath, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Image', 'Desktop',
            'PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*)')
        if filePath: self.pixmap().save(filePath)
    
    def open(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Image', 'Desktop',
            'PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*)')
        if filePath:
            self.pixmap().load(filePath)
            self.backup, self.state = [self.pixmap().toImage()], 1
    
    def undo(self):
        if self.state > 1:
            self.state -= 1
            pm = QtGui.QPixmap.fromImage(self.backup[self.state-1])
            self.setPixmap(pm)
    
    def redo(self):
        if self.state < len(self.backup):
            self.state += 1
            pm = QtGui.QPixmap.fromImage(self.backup[self.state-1])
            self.setPixmap(pm)
    
    def clear(self):
        self.pixmap().fill(Qt.white)
        self.update()
        self.add_state()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 500)
        MainWindow.setMinimumSize(QtCore.QSize(1000, 500))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.btnLine = QtWidgets.QPushButton(self.centralwidget)
        self.btnLine.setGeometry(QtCore.QRect(920, 10, 70, 70))
        self.btnLine.setText("")
        self.btnLine.setIconSize(QtCore.QSize(50, 50))
        self.btnLine.setObjectName("btnLine")
        self.btnCircle = QtWidgets.QPushButton(self.centralwidget)
        self.btnCircle.setGeometry(QtCore.QRect(840, 90, 70, 70))
        self.btnCircle.setText("")
        self.btnCircle.setIconSize(QtCore.QSize(40, 40))
        self.btnCircle.setObjectName("btnCircle")
        self.btnFill = QtWidgets.QPushButton(self.centralwidget)
        self.btnFill.setGeometry(QtCore.QRect(840, 170, 70, 70))
        self.btnFill.setText("")
        self.btnFill.setIconSize(QtCore.QSize(50, 50))
        self.btnFill.setObjectName("btnFill")
        self.btnRectangle = QtWidgets.QPushButton(self.centralwidget)
        self.btnRectangle.setGeometry(QtCore.QRect(920, 90, 70, 70))
        self.btnRectangle.setText("")
        self.btnRectangle.setIconSize(QtCore.QSize(47, 47))
        self.btnRectangle.setObjectName("btnRectangle")
        self.btnPen = QtWidgets.QPushButton(self.centralwidget)
        self.btnPen.setGeometry(QtCore.QRect(840, 10, 70, 70))
        self.btnPen.setText("")
        self.btnPen.setIconSize(QtCore.QSize(50, 50))
        self.btnPen.setObjectName("btnPen")
        self.btnErase = QtWidgets.QPushButton(self.centralwidget)
        self.btnErase.setGeometry(QtCore.QRect(920, 170, 70, 70))
        self.btnErase.setText("")
        self.btnErase.setIconSize(QtCore.QSize(50, 50))
        self.btnErase.setObjectName("btnErase")
        self.btnSpray = QtWidgets.QPushButton(self.centralwidget)
        self.btnSpray.setGeometry(QtCore.QRect(840, 260, 151, 41))
        font = QtGui.QFont()
        font.setFamily("Yu Gothic Medium")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.btnSpray.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../Downloads/9055693_bxs_spray_can_icon (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnSpray.setIcon(icon)
        self.btnSpray.setIconSize(QtCore.QSize(35, 35))
        self.btnSpray.setObjectName("btnSpray")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(860, 250, 118, 3))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(9, 9, 821, 441))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(860, 400, 118, 3))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.chbAlias = QtWidgets.QCheckBox(self.centralwidget)
        self.chbAlias.setGeometry(QtCore.QRect(880, 440, 81, 17))
        font = QtGui.QFont()
        font.setFamily("Yu Gothic Medium")
        font.setBold(False)
        font.setWeight(50)
        self.chbAlias.setFont(font)
        self.chbAlias.setTristate(False)
        self.chbAlias.setObjectName("chbAlias")
        self.spnBoxSize = QtWidgets.QSpinBox(self.centralwidget)
        self.spnBoxSize.setGeometry(QtCore.QRect(930, 410, 42, 22))
        self.spnBoxSize.setMinimum(1)
        self.spnBoxSize.setMaximum(25)
        self.spnBoxSize.setProperty("value", 3)
        self.spnBoxSize.setObjectName("spnBoxSize")
        self.labelPenSize = QtWidgets.QLabel(self.centralwidget)
        self.labelPenSize.setGeometry(QtCore.QRect(850, 410, 71, 20))
        font = QtGui.QFont()
        font.setFamily("Yu Gothic Medium")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelPenSize.setFont(font)
        self.labelPenSize.setObjectName("labelPenSize")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(840, 310, 151, 91))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.vLayoutSliders = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.vLayoutSliders.setContentsMargins(0, 0, 0, 0)
        self.vLayoutSliders.setObjectName("vLayoutSliders")
        self.labelNoP = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Yu Gothic Medium")
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.labelNoP.setFont(font)
        self.labelNoP.setObjectName("labelNoP")
        self.vLayoutSliders.addWidget(self.labelNoP, 0, QtCore.Qt.AlignHCenter)
        self.sliderNoP = QtWidgets.QSlider(self.verticalLayoutWidget_2)
        self.sliderNoP.setMinimum(1)
        self.sliderNoP.setMaximum(500)
        self.sliderNoP.setProperty("value", 100)
        self.sliderNoP.setOrientation(QtCore.Qt.Horizontal)
        self.sliderNoP.setObjectName("sliderNoP")
        self.vLayoutSliders.addWidget(self.sliderNoP)
        self.labelDiameter = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Yu Gothic Medium")
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.labelDiameter.setFont(font)
        self.labelDiameter.setWordWrap(True)
        self.labelDiameter.setObjectName("labelDiameter")
        self.vLayoutSliders.addWidget(self.labelDiameter, 0, QtCore.Qt.AlignHCenter)
        self.sliderDiameter = QtWidgets.QSlider(self.verticalLayoutWidget_2)
        self.sliderDiameter.setMinimum(1)
        self.sliderDiameter.setMaximum(50)
        self.sliderDiameter.setProperty("value", 10)
        self.sliderDiameter.setOrientation(QtCore.Qt.Horizontal)
        self.sliderDiameter.setObjectName("sliderDiameter")
        self.vLayoutSliders.addWidget(self.sliderDiameter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 23))
        font = QtGui.QFont()
        font.setFamily("Yu Gothic UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.menubar.setFont(font)
        self.menubar.setObjectName("menubar")
        self.menuMain = QtWidgets.QMenu(self.menubar)
        self.menuMain.setObjectName("menuMain")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionClear = QtWidgets.QAction(MainWindow)
        self.actionClear.setObjectName("actionClear")
        self.actionUndo = QtWidgets.QAction(MainWindow)
        self.actionUndo.setObjectName("actionUndo")
        self.actionRedo = QtWidgets.QAction(MainWindow)
        self.actionRedo.setObjectName("actionRedo")
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.menuMain.addAction(self.actionOpen)
        self.menuMain.addAction(self.actionSave)
        self.menuMain.addSeparator()
        self.menuMain.addAction(self.actionUndo)
        self.menuMain.addAction(self.actionRedo)
        self.menuMain.addAction(self.actionClear)
        self.menuMain.addSeparator()
        self.menuMain.addAction(self.actionExit)
        self.menubar.addAction(self.menuMain.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btnSpray.setText(_translate("MainWindow", "    Spray"))
        self.chbAlias.setText(_translate("MainWindow", "Antialiasing"))
        self.labelPenSize.setText(_translate("MainWindow", " Pen Size:"))
        self.labelNoP.setText(_translate("MainWindow", "Number of Particles"))
        self.labelDiameter.setText(_translate("MainWindow", "Diameter"))
        self.menuMain.setTitle(_translate("MainWindow", "Menu"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionClear.setText(_translate("MainWindow", "Clear"))
        self.actionUndo.setText(_translate("MainWindow", "Undo"))
        self.actionRedo.setText(_translate("MainWindow", "Redo"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))

app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(window)

i_dir = os.path.join(PATH, 'Icons')
for i_name in os.listdir(i_dir):
    icon, path = QtGui.QIcon(), os.path.join(i_dir, i_name)
    icon.addPixmap(QtGui.QPixmap(path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    if i_name == 'pen.png':
        ui.btnPen.setIcon(icon)
        ui.btnPen.setIconSize(QtCore.QSize(50, 50))
    elif i_name == 'line.png':
        ui.btnLine.setIcon(icon)
        ui.btnLine.setIconSize(QtCore.QSize(50, 50))
    elif i_name == 'circle.png':
        ui.btnCircle.setIcon(icon)
        ui.btnCircle.setIconSize(QtCore.QSize(40, 40))
    elif i_name == 'rectangle.png':
        ui.btnRectangle.setIcon(icon)
        ui.btnRectangle.setIconSize(QtCore.QSize(47, 47))
    elif i_name == 'fill.png':
        ui.btnFill.setIcon(icon)
        ui.btnFill.setIconSize(QtCore.QSize(50, 50))
    elif i_name == 'eraser.png':
        ui.btnErase.setIcon(icon)
        ui.btnErase.setIconSize(QtCore.QSize(50, 50))
    elif i_name == 'spray.png':
        ui.btnSpray.setIcon(icon)
        ui.btnSpray.setIconSize(QtCore.QSize(35, 35))

width = ui.verticalLayoutWidget.size().width()
height = ui.verticalLayoutWidget.size().height()-25
canvas = Canvas()
ui.verticalLayout.addWidget(canvas)

palette = QtWidgets.QHBoxLayout()
for c in COLORS:
    btn = QPaletteButton(c)
    btn.pressed.connect(lambda c=c: canvas.set_pen_color(c))
    palette.addWidget(btn)
palette.setAlignment(Qt.AlignCenter)
ui.verticalLayout.addLayout(palette)

ui.chbAlias.setChecked(True)
ui.chbAlias.stateChanged.connect(chAlias)
ui.spnBoxSize.valueChanged.connect(lambda: canvas.set_pen_size(ui.spnBoxSize.value()))

ui.btnPen.clicked.connect(lambda: canvas.set_mode('pen'))
ui.btnLine.clicked.connect(lambda: canvas.set_mode('line'))
ui.btnCircle.clicked.connect(lambda: canvas.set_mode('elli'))
ui.btnRectangle.clicked.connect(lambda: canvas.set_mode('rect'))
ui.btnFill.clicked.connect(lambda: canvas.set_mode('fill'))
ui.btnErase.clicked.connect(lambda: canvas.set_mode('ers'))
ui.btnSpray.clicked.connect(lambda: canvas.set_mode('spray'))
ui.sliderNoP.valueChanged.connect(lambda: canvas.set_spray(ui.sliderNoP.value(), None))
ui.sliderDiameter.valueChanged.connect(lambda: canvas.set_spray(None, ui.sliderDiameter.value()))

ui.actionOpen.triggered.connect(canvas.open)
ui.actionSave.triggered.connect(canvas.save)
ui.actionUndo.triggered.connect(canvas.undo)
ui.actionRedo.triggered.connect(canvas.redo)
ui.actionClear.triggered.connect(canvas.clear)
ui.actionExit.triggered.connect(QtCore.QCoreApplication.instance().quit)

ui.actionOpen.setShortcut(QtGui.QKeySequence('Ctrl+O'))
ui.actionSave.setShortcut(QtGui.QKeySequence('Ctrl+S'))
ui.actionUndo.setShortcut(QtGui.QKeySequence('Ctrl+Z'))
ui.actionRedo.setShortcut(QtGui.QKeySequence('Ctrl+Y'))
ui.actionClear.setShortcut(QtGui.QKeySequence('Ctrl+Del'))

window.show()
app.exec_()