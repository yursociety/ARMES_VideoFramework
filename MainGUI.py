import gobject
import sys
import socket
import time
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from datetime import datetime
from MainGUIWidgets import * 
from GstUtil import *

class OperatorGUI(QMainWindow):
	Signal_OperatorGUI_Quit = pyqtSignal() #signal to send for closing
	Signal_Compass_Heading = pyqtSignal(float)

	def __init__(self):
		super(OperatorGUI, self).__init__()
		self.setWindowTitle('OperatorGUI')
		self.setToolTip('This is a <b>QWidget</b> widget - GUI Base')
		self.GUISize = QSize(640,500)
		self.resize(self.GUISize.width(),self.GUISize.height())
		center(self)
		self._initUI()

	def _initUI(self):
		# 1. build pipeline
		self.NUMBER_CAMERAS = 1
		self.pipelines = GStreamerPipeline()
		self.pipelines.startup(self.NUMBER_CAMERAS)
		# 2. build widgets
		self.videoDisplayWidget = VideoDisplayWidget(self.GUISize.width(), self.GUISize.height(), self.pipelines, self)
		self.pipelines.Trigger_New_Frame().connect(self.videoDisplayWidget.Slot_Trigger_New_Frame)
		self.compassWidget = CompassWidget(150,30, 5, 15, self)
		# 3. move widgets
		self.videoDisplayWidget.move(0,0)
		self.compassWidget.move(self.GUISize.width()/2, self.GUISize.height()/2)
		# 4. bind widget signals
		self.Signal_Compass_Heading.connect(self.compassWidget._Slot_Update_Heading)
		

	def keyPressEvent(self, e):
		#gst.STATE_NULL, gst.STATE_PAUSED, gst.STATE_READY, gst.STATE_PLAYING
		if e.key() == Qt.Key_Escape: # Esc
			self.close()
		elif e.key() == Qt.Key_F1:
			print('F1:3=Playing')
			self.changeCameraStatus(self.videoDisplayWidget._cameraIndex, gst.STATE_PLAYING)
		elif e.key() == Qt.Key_F2:
			print('F1:3=Pause')
			self.changeCameraStatus(self.videoDisplayWidget._cameraIndex, gst.STATE_PAUSED)
		elif e.key() == Qt.Key_F3:
			print('F1:3=Stop')
			self.changeCameraStatus(self.videoDisplayWidget._cameraIndex, gst.STATE_NULL)

	def changeCameraStatus(self, index, num):
		self.videoDisplayWidget.currentVideoStatus = num
		self.pipelines.Signal_Set_Camera().emit(index, num)

	def closeEvent(self, event):
		#self.screenVideo.streamer.quit()
		event.accept()
		sys.exit()
		
'''
Centers the main window on the screen.
'''
def center(widget):
	qr = widget.frameGeometry()
	cp = QDesktopWidget().availableGeometry().center()
	qr.moveCenter(cp)
	widget.move(qr.topLeft())


def main():
	app = QApplication(sys.argv)	# application object for PyQT
	gui = OperatorGUI()
	gui.show()
	loop = gobject.MainLoop()
	try:
		loop.run()
		app.exec_()
	except KeyboardInterrupt:
		print "Ctrl+C pressed, exitting"
		pass

if __name__ == '__main__':
	ret = gst.element_register(VideoSink, 'VideoSink')
	gobject.threads_init()
	main()