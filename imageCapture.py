from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal, os, subprocess
from flask import Flask, render_template

app = Flask(__name__)


# Kill gphoto2 process that starts when we connect the camera
def KillProcess():
	p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
	out, err = p.communicate()

	# Search for the line to kill
	for line in out.splitlines():
		if b'gvfsd-gphoto2' in line:
			#Kill the proces
			pid = int(line.splite(None, 1)[0])
			os.kill(pid, signal.SIGKILL)

shot_date = datetime.now().strftime("%Y-%m-%d_")
shot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

picID = "Test"

clearCommand = ["--folder", "/store_00020001/DCIM/100CANON", "-R", "--delete-all-files"]
triggerCommand = ["--trigger-capture"]
downloadCommand = ["--get-all-files"]

folder_name = shot_date + picID
save_location = "/home/admin/gphoto/images/" + folder_name

def CreateSaveFolder():
	try:
		os.makedirs(save_location)
	except:
		print("Failed to create new dir")
	os.chdir(save_location)

def CaptureImages():
	gp(triggerCommand)
	sleep(3)
	print("Downloading Files...")
	gp(downloadCommand)
	gp(clearCommand)

def RenameFiles():
	for filename in os.listdir("."):
		if len(filename) < 13:
			if filename.endswith(".JPG"):
				os.rename(filename, (shot_time + picID + ".JPG"))
				print("Renamed jpg")
			elif filename.endswith(".CR2"):
				os.rename(filename, (shot_time + picID + ".CR2"))
				print("Renamed cr2")

def TakePicture():
	KillProcess()
	gp(clearCommand)
	CreateSaveFolder()
	CaptureImages()
	RenameFiles()
	return "capture done"


# Define Flask stuff
@app.route('/')
def index():
	return render_template('index.html')

#define a route to trigger capturing an image
@app.route('/capture', methods=['POST'])
def capture():
	result = TakePicture()
	return result

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)
