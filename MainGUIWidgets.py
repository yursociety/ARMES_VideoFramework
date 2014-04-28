import math
import sys
from PyQt4.QtGui import QMainWindow,QFont,QToolTip,QTabWidget,QLabel,QWidget,QLCDNumber,QIcon,QDesktopWidget,QColor,QImage,QPixmap,QPainter
from PyQt4.QtCore import QThread,Qt,pyqtSignal,QString,QObject,QSize,QPoint,QRect

class GUIWidget(QWidget):
	def __init__(self, width,height, parent = None):
		super(GUIWidget, self).__init__(parent)
		self.width = width
		self.height = height
		self.resize(self.width,self.height)

class VideoDisplayWidget(GUIWidget):
	Signal_Camera_Set = pyqtSignal(int)
	def __init__(self, width,height, pipelines, parent = None):
		super(VideoDisplayWidget, self).__init__(width,height,parent)
		self.pipelines = pipelines
		self._cameraIndex = 0
		self.currentVideoStatus = 0
		self.Signal_Camera_Set.connect(self.Slot_Camera_Set)
		self.pixmap = QPixmap()

	def paintEvent(self, event):
		painter = QPainter()
		painter.begin(self)
		painter.drawPixmap(0,0, self.width,self.height, self.pixmap)
		painter.end()

	def Slot_Camera_Set(self, index):
		self._cameraIndex = index

	def Slot_Trigger_New_Frame(self, image, index):
		self.pixmap = image
		self.repaint()

#08.  Compass Widget - OPENCV - Cleaned
# border,background,tick,font,nav points
class CompassWidget(QLabel):
	Signal_Update_Heading = pyqtSignal(int)
	def __init__(self, width, height, compass_tick_spacing, font_size, parent = None):
		super(CompassWidget, self).__init__(parent)
		self.width = width
		self.height = height
		self.resize(self.width, self.height)
		self.compass_tick_spacing = compass_tick_spacing # spacing between each tick
		self.font_size = font_size
		self.font_width = self.font_size
		
		self._compass_mini_tick_length =  int(self.height/8) # length of a small tick
		self._compass_small_tick_length = int(self.height/4) # length of a small tick
		self._compass_large_tick_length = int(self.height/2) # length of a large tick
		self._compass_small_tick_rep = 9 # what a small tick represents
		self._compass_large_tick_rep = 45# what a large tick represents
		self._compass_heading_arrow_height = int(self.height/4)
		self._compass_names = ['N','NE','E','SE','S','SW','W','NW','N']
		#self.ticks_showable = int(self.width/self.compass_tick_spacing) #max number of ticks showable
		self._heading = 0 # heading is counter clockwise
		self.Signal_Update_Heading.connect(self._Slot_Update_Heading)

		self._color_border = QColor(255, 34, 3)
		self._color_tick = QColor(255, 34, 3)
		self._color_background = QColor(180, 180, 180, 120) #Qt.NoBrush
		self._color_font = QColor(255, 34, 3)
		self._font = QFont('Decorative', self.font_size)

	def paintEvent(self, event):
		qp = QPainter()
		qp.begin(self)
		self._drawBorder(event, qp)
		self._drawCompass(event, qp)
		qp.end()

	def _drawBorder(self, event, qp):
		qp.setPen(self._color_border)
		qp.setBrush(self._color_background)
		qp.drawRect(0,0, self.width-1, self.height-1)
		#draw triangle for center heading
		qp.drawLine(self.width/2-self.compass_tick_spacing,self.height, self.width/2,self.height-self._compass_heading_arrow_height)
		qp.drawLine(self.width/2+self.compass_tick_spacing,self.height, self.width/2,self.height-self._compass_heading_arrow_height)
		
	def _drawCompass(self, event, qp):
		self._drawSideTicks(qp, 1, self._heading)
		self._drawSideTicks(qp, -1, self._heading)
		
	def _drawSideTicks(self, qp, incrementor, heading):
		qp.setPen(self._color_tick)
		qp.setBrush(Qt.NoBrush)
		qp.setFont(self._font)
		mid_heading = heading
		current_heading = heading
		drawTicks = True
		while drawTicks: # right side ticks only
			tick_length = self._compass_mini_tick_length
			if current_heading%self._compass_large_tick_rep == 0:
				offset = int((len(self._compass_names[current_heading/self._compass_large_tick_rep])*self.font_width)/2)
				qp.setPen(self._color_font)
				qp.drawText(self.width/2+(current_heading-mid_heading)*self.compass_tick_spacing-offset, self.font_size, self._compass_names[current_heading/self._compass_large_tick_rep])
				tick_length = self._compass_large_tick_length
			elif current_heading%self._compass_small_tick_rep == 0:
				tick_length = self._compass_small_tick_length
			qp.setPen(self._color_tick)
			qp.drawLine(self.width/2+(current_heading-mid_heading)*self.compass_tick_spacing, self.height,
				        self.width/2+(current_heading-mid_heading)*self.compass_tick_spacing, self.height-tick_length)
			current_heading += incrementor # paint next tick
			if not (0 <= self.width/2+(current_heading-mid_heading)*self.compass_tick_spacing and self.width/2+(current_heading-mid_heading)*self.compass_tick_spacing <= self.width):
				drawTicks = False

	# heading is counterclockwise, so flip it
	def _Slot_Update_Heading(self, heading):
		self._heading = heading
		self.update()
		self.repaint()