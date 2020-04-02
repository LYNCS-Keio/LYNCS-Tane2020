from package import camera
from package import capture
import time
import math

rotation = 0

def update_rotation_with_cam():
    global rotation
    while UPDATE_CAMERA == True:
        pt = time.time()
        stream = cap.cap()
        captime = time.time() - pt
        
        pt = time.time()
        cam.morphology_extract(stream)
        morphtime = time.time() - pt
        
        pt = time.time()
        coord = cam.contour_find()
        coordtime = time.time() - pt
        
        pt = time.time()
        cam.save_all_outputs()
        savetime = time.time() - pt

        if coord is None:
            print('{:.2f}'.format(captime),
            '{:.2f}'.format(morphtime),
            '{:.2f}'.format(coordtime),
            '{:.2f}'.format(savetime),
            '{:.2f}'.format(0))
        else:
            conX = ((coord[0] - 160) / 160) / math.sqrt(3)
            rotation = math.degrees(math.atan(-conX))
            print('{:.2f}'.format(captime),
            '{:.2f}'.format(morphtime),
            '{:.2f}'.format(coordtime),
            '{:.2f}'.format(savetime),
            '{:.2f}'.format(rotation))

if __name__ == "__main__":
    cap = capture.capture()
    cam = camera.CamAnalysis()
    UPDATE_CAMERA = True

    update_rotation_with_cam()