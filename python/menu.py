import objc, re, os
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper

# poach flux to start
status_images = {'idle':'/Applications/Flux.app/Contents/Resources/flux-icon-mono4.tiff',
              'working':'/Applications/Flux.app/Contents/Resources/flux-icon-mono-inv.tiff',
              'graph': 'pic.png'}

start_time = NSDate.date()

class Timer(NSObject):
  images = {}
  statusbar = None
  state = 'idle'

  def applicationDidFinishLaunching_(self, notification):
    statusbar = NSStatusBar.systemStatusBar()
    self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength) # Create the statusbar item

    for i in status_images.keys(): # Load all images
      self.images[i] = NSImage.alloc().initByReferencingFile_(status_images[i])

    self.statusitem.setImage_(self.images['idle']) # Set initial image

    self.statusitem.setHighlightMode_(1) # Let it highlight upon clicking

    self.statusitem.setToolTip_('Sync Trigger') # Set a tooltip

    self.menu = NSMenu.alloc().init() # Build a very simple menu

    #Let's try with a pic
    #menuitem = NSMenuItem.alloc().init()
    self.menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
    #menuitem.setImage_('pic.png')
    self.menuitem.setImage_(self.images['graph'])

    self.menu.addItem_(self.menuitem)

    # Bind it to the status item
    self.statusitem.setMenu_(self.menu)

    # Get the timer going
    self.timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(start_time, 5.0, self, 'tick:', None, True)
    NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer, NSDefaultRunLoopMode)
    self.timer.fire()

  def sync_(self, notification):
    print "sync"

  def tick_(self, notification):
    if self.state == 'working':
      self.state = 'idle'
    else:
      self.state = 'working'
    self.statusitem.setImage_(self.images[self.state])
    #dealloc(self.graph) #not needed I think
    self.graph = NSImage.alloc().initByReferencingFile_('pic.png')
    self.menuitem.setImage_(self.graph)

    print self.state

if __name__ == "__main__":
  app = NSApplication.sharedApplication()
  delegate = Timer.alloc().init()
  app.setDelegate_(delegate)
  AppHelper.runEventLoop()
