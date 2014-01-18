import time
import sys
import numpy as np
import cv2
 
def detect(image):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cascade = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')
    #cascade = cv2.CascadeClassifier('cascades/haarcascade_frontalface_alt.xml')
    #faces = cascade.detectMultiScale(image=gray, scaleFactor=1.3, minNeighbors=3, flags=0, minSize=64, maxSize=400)
    faces = cascade.detectMultiScale(gray, 1.3, 3, 0, 64, 400)
 
    #cv2.imshow('frame', image)
    for (x,y,w,h) in faces:
      print "face found." 
      image = cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
        #roi_gray = gray[y:y+h, x:x+w]
        #roi_color = image[y:y+h, x:x+w]
 
if __name__ == "__main__":
    print "Press ESC to exit ..."
 
    # create windows
    cv2.namedWindow('Camera', cv2.WINDOW_AUTOSIZE)
 
    # create capture device
    device = 0 # assume we want first device
    cap = cv2.VideoCapture(0)
      # check if capture device is OK
    if not cap:
      print "Error opening capture device"
      sys.exit(1)

    while(True):
      # do forever
      # Capture frame-by-frame
      ret, frame = cap.read()
      if frame is None:
        break

      # Our operations on the frame come here

      # Display the resulting frame
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break

      # face detection
      detect(frame)
      cv2.imshow('frame', frame)
 
        # handle events
      k = cv2.waitKey(10)
 
      if k == 0x1b: # ESC
        print 'ESC pressed. Exiting ...'
        break
    cap.release()
    cv2.destroyAllWindows() 
