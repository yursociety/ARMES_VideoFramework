import pygst
pygst.require("0.10")
import gst
import gobject
from PyQt4.QtGui import QPixmap
from PyQt4.QtCore import pyqtSignal,QObject

'''
Struct for holding Signal and Trigger:
Signal  = set video pipeline(index) state. (stop, pause, playing)
Trigger = notify widget that there is new video frame
'''
class SignalSetCamObject(QObject):
	Signal = pyqtSignal(int,int)
	Trigger = pyqtSignal(QPixmap, int)
	def __init__(self, parent = None):
		super(SignalSetCamObject, self).__init__(parent)

'''
Video pipeline sets
'''
class GStreamerPipeline():
	def __init__(self):
		self._pixmaps = []
		self._length = 0
		self.pipelines = []
		self.videoSets = []
		self.START_PORT = 5000
		self.numberCameras = 0
		self.Signal_Camera = SignalSetCamObject()
		self.Signal_Set_Camera().connect(self.Slot_Set_Camera)

	def Signal_Set_Camera(self):
		return self.Signal_Camera.Signal
	def Trigger_New_Frame(self):
		return self.Signal_Camera.Trigger

	def startup(self, num):
		self.numberCameras = num
		for i in range(self.numberCameras):
			self.addPipeline()

	def addPipeline(self):
		port = self.START_PORT+self._length
		strPipeline =  "udpsrc port="+str(port)+" ! application/x-rtp,payload=127 ! rtph264depay ! h264parse ! ffdec_h264 ! queue ! jpegenc ! VideoSink name=\"videosink0\" sync=false"
		self.pipelines.append(gst.parse_launch(strPipeline))
		self.sink = self.pipelines[self._length].get_by_name("videosink0")
		self.sink._index = self._length
		self.sink.getSignal().connect(self.Slot_Trigger_Do_Render)
		self.videoSets.append([self.pipelines[self._length],self.sink,"video"+str(self._length)])
		self._pixmaps.append(QPixmap())
		self._length += 1

	def Slot_Set_Camera(self, index, status):
		self.videoSets[index][0].set_state(status)
		#gst.STATE_NULL, gst.STATE_PAUSED, gst.STATE_READY, gst.STATE_PLAYING

	# sink triggers this, dumps image Buffer into a pixmap
	def Slot_Trigger_Do_Render(self, get_buffer, index):
		data = get_buffer.data
		self._pixmaps[index].loadFromData(data,'JPEG')
		self.Trigger_New_Frame().emit(self._pixmaps[index], index)

'''
Hold onto the jpeg caught by the GStreamer video stream video sink.
'''
class SignalObject(QObject):
	signal = pyqtSignal(gst.Buffer,int)
	def __init__(self, parent = None):
		super(SignalObject, self).__init__(parent)

'''
GStreamer pipeline sink for catching video stream and display on screen.
Catches in do_render and passes the image(jpeg) to whatever binds to _Signal_Buffer.
'''
class VideoSink(gst.BaseSink):
	__gtype_name__ = 'VideoSink'
	__gstdetails__ = ("Video Sink", "Sink/Network",
	"Catch video stream as jpeg frames", "Dennis Liu <dennisliu12@gmail.com>")

	__gsttemplates__ = (
		gst.PadTemplate("sink",
			gst.PAD_SINK,
			gst.PAD_ALWAYS,
			gst.caps_new_any()),
		)
	_index = 0
	_Signal_Buffer = SignalObject()

	def getSignal(self):
		return self._Signal_Buffer.signal

	def do_start(self):
		self.of = open("video.bin", "wb")
		return True

	def do_stop(self):
		self.of.close()
		return True

	def do_set_caps(self, caps):
		self.of.write("%s\n" % caps)
		return True

	def do_render(self, get_buffer): #gst.Buffer
		self._Signal_Buffer.signal.emit(get_buffer, self._index)
		return gst.FLOW_OK

	def do_preroll(self, buf):
		return gst.FLOW_OK

	def do_event(self, ev):
		return gst.FLOW_OK