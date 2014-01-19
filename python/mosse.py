#!/usr/bin/env python

'''
MOSSE tracking sample

This sample implements correlation-based tracking approach, described in [1].

Usage:
  mosse.py [--pause] [<video source>]

  --pause  -  Start with playback paused at the first video frame.
              Useful for tracking target selection.

  Draw rectangles around objects with a mouse to track them.

Keys:
  SPACE    - pause video
  c        - clear targets

[1] David S. Bolme et al. "Visual Object Tracking using Adaptive Correlation Filters"
    http://www.cs.colostate.edu/~bolme/publications/Bolme2010Tracking.pdf
'''

import numpy as np
import cv2
from common import draw_str, RectSelector, clock
import video
import matplotlib.pyplot as plt
import matplotlib.cm as cm

MHI_DURATION = 0.5
DEFAULT_THRESHOLD = 32
MAX_TIME_DELTA = 0.25
MIN_TIME_DELTA = 0.05
NUM_MEASURES = 100
MA = 30
RECENT_MA = 10

class Temple:
    def __init__(self, frame):
        self.h , self.w = frame.shape[:2]
        self.prev_frame = frame.copy()
        self.motion_history = np.zeros((self.h, self.w), np.float32)
        self.real_diff = None

    def update(self, frame):
        frame_diff = cv2.absdiff(frame, self.prev_frame)
        real_diff = frame - self.prev_frame
        self.real_diff = cv2.cvtColor(real_diff,  cv2.COLOR_BGR2GRAY)
        gray_diff = cv2.cvtColor(frame_diff, cv2.COLOR_BGR2GRAY)
        thrs = 40 #cv2.getTrackbarPos('threshold', 'motempl')
        ret, motion_mask = cv2.threshold(gray_diff, thrs, 1, cv2.THRESH_BINARY)
        timestamp = clock()
        cv2.updateMotionHistory(motion_mask, self.motion_history, timestamp, MHI_DURATION)

        self.vis = np.uint8(np.clip((self.motion_history-(timestamp-MHI_DURATION)) / MHI_DURATION, 0, 1)*255)
        self.vis = cv2.cvtColor(self.vis, cv2.COLOR_GRAY2BGR)
        #self.process_motions()
        self.prev_frame = frame.copy()

    def process_motions(self, seg_bounds):
        mg_mask, mg_orient = cv2.calcMotionGradient( self.motion_history, MAX_TIME_DELTA, MIN_TIME_DELTA, apertureSize=5 )
        seg_mask, seg_bounds = cv2.segmentMotion(self.motion_history, timestamp, MAX_TIME_DELTA)
        for i, rect in enumerate([(0, 0, self.w, self.h)] + list(seg_bounds)):
            x, y, rw, rh = rect
            area = rw*rh
            if area < 64**2:
                continue
            silh_roi   = motion_mask   [y:y+rh,x:x+rw]
            orient_roi = mg_orient     [y:y+rh,x:x+rw]
            mask_roi   = mg_mask       [y:y+rh,x:x+rw]
            mhi_roi    = self.motion_history[y:y+rh,x:x+rw]
            if cv2.norm(silh_roi, cv2.NORM_L1) < area*0.05:
                continue
            angle = cv2.calcGlobalOrientation(orient_roi, mask_roi, mhi_roi, timestamp, MHI_DURATION)
            color = ((255, 0, 0), (0, 0, 255))[i == 0]
            draw_motion_comp(self.vis, rect, angle, color)


 
class App:
    def __init__(self, video_src, paused = False):
        self.cap = video.create_capture(video_src)
        _, self.frame = self.cap.read()
        cv2.imshow('frame', self.frame)
        h , w = self.frame.shape[:2]
        self.roiw = w/3.0
        self.roih = h/3.0
        self.roix, self.roiy = (w/2.0, h - self.roih/2.0)
        print "roix is" + str(self.roix)
        print "roiy is" + str(self.roiy)
        print "roiw is" + str(self.roiw)
        print "roih is" + str(self.roih)

        self.trackers = []
        self.paused = paused
        self.temple = None
        self.frames_read  = 0

        self.filtered = np.zeros((2, NUM_MEASURES))

        self.readings = np.zeros(MA)
        self.sum_readings = 0

        self.recent_readings = np.zeros(RECENT_MA)
        self.recent_sum = 0

        self.temple = Temple(self.frame)

    def run(self):
        while True:
            if not self.paused:
                ret, self.frame = self.cap.read()
                self.frames_read = self.frames_read + 1
                if not ret:
                    break
                frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

                if self.temple:
                    final = self.frame.copy()
                    reading_no = self.frames_read % NUM_MEASURES
                    #print "Reading number " + str(reading_no)
                    self.temple.update(self.frame)
                    #cv2.imshow('frame', self.trackers[0].pos)
                    x = self.roix
                    y = self.roiy
                    h = self.roih
                    w = self.roiw

                    y_offset= int(h/2)
                    x_offset= int(w/2)
                    final[y-y_offset:y+y_offset, x-x_offset:x+x_offset] = self.temple.vis[y-y_offset:y+y_offset, x-x_offset:x+x_offset]
                    sumDiff = cv2.sumElems(self.temple.real_diff[y-y_offset:y+y_offset, x-x_offset:x+x_offset])[0]
                    if sumDiff == 0:
                      continue

                    reading = sumDiff/(w*h+1)

                    # For 'speed' we just subtract the value we're overwriting and then add the new one. The others don't change:

                    #Moving average:
                    ma_no = self.frames_read % MA
                    self.sum_readings = self.sum_readings - self.readings[ma_no] + reading
                    self.readings[ma_no] = reading

                    
                    #short ma
                    recent_ma_no = self.frames_read % RECENT_MA
                    self.recent_sum = self.recent_sum - self.recent_readings[recent_ma_no] + reading
                    self.recent_readings[recent_ma_no] = reading

                    #print self.readings
                    self.filtered[0][reading_no] = clock()
                    self.filtered[1][reading_no] = self.recent_sum/RECENT_MA - self.sum_readings/MA #Remove long term noise

                    self.frame = final.copy()
                    if reading_no == NUM_MEASURES-1: #When we've read a whole array in, flush it to a graph
                      t = scipy.linspace(filtered[0][0],0.1995,filtered[0][NUM_MEASURES-1])

                      FFT = abs(scipy.fft(self.readings))
                      freqs = scipy.fftpack.fftfreq(readings.size, 0.1995)

                      pylab.subplot(211)
                      plt.plot(self.filtered[0], self.filtered[1])
                      pylab.subplot(212)
                      pylab.plot(freqs,20*scipy.log10(FFT),'x')
                      pylab.show()
                      print "Saving pic.png"
                      plt.clf()
                      #plt.plot(self.filtered[0], self.filtered[1])
                      plt.xlabel('time (s)')
                      plt.ylabel('Movement')
                      #grid(True)
                      plt.savefig("pic.png")
                cv2.imshow('frame', self.frame)


            ch = cv2.waitKey(10)
            if ch == 27:
                break
            if ch == ord(' '):
                self.paused = not self.paused

if __name__ == '__main__':
    print __doc__
    import sys, getopt
    opts, args = getopt.getopt(sys.argv[1:], '', ['pause'])
    opts = dict(opts)
    try: video_src = args[0]
    except: video_src = '0'

    App(video_src, paused = '--pause' in opts).run()
