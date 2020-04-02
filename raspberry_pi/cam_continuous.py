import picamera
from package import camera as cm
import time
import io
import math
import numpy as np
import cv2

if __name__ == "__main__":
    camera = picamera.PiCamera()
    cam = cm.CamAnalysis()
    camera.resolution = (320, 240)
    camera.framerate = 30
    camera.start_preview()
    time.sleep(2)

    stream = io.BytesIO()

    try:

        pt = time.time()
        camera.capture_continuous(stream, 'jpeg', use_video_port=True).__next__()
        stream.seek(0)
        data = np.frombuffer(stream.read(), dtype=np.uint8)
        data = cv2.imdecode(data, 1)
        stream.seek(0)
        stream.truncate()
        print("capture", time.time()-pt)

        pt = time.time()
        cam.morphology_extract(data)
        print("morph", time.time()-pt)

        pt = time.time()
        coord = cam.contour_find()
        print("coord", time.time()-pt)

        #pt = time.time()
        #cam.save_all_outputs()
        #print("save", time.time()-pt)

        if coord is None:
            print("no contour found")
        else:
            conX = ((coord[0] - 160) / 160) / math.sqrt(3)
            rotation = math.degrees(math.atan(-conX))
            print(rotation)

    finally:
        camera.stop_preview()
        camera.close()