#
#  PWBC - PyWright Base Code
#
#  This is some base code I use for my projects, since I started developing it for
#  PyWright.
#
#   It doesn't do a whole lot (it's base code, what do you expect?) but it does enough
#   very nice things that can take a lot of time to add to a new project - or they are
#   just forgotten and left out altogether. Or the timestep is implemented in a bad
#   way, etc.
#
#   There are a few main benefits to using this code, at least for me - I'm not sure
#   how useful other people will find it. But the main benefits are:
#       * executable - A prebuilt windows exe with all the deps I will ever need. I can
#                           update code without rebuilding it. I have used py2exe once this
#                           year, and that was to change the name from PyWright to main.
#                           Using py2exe is a pain in the butt. I want to touch it as
#                           infrequently as possible
#       * timestepping - the engine in PWBC has a decent timestep. It runs at a locked
#                           60 seconds, so update functions generally only have to think in
#                           terms of frames rather than the time changed on a frame (although
#                           you have access to that if you need it). You can also alter the
#                           logic framerate so that it is different from the display framerate.
#       * display - the display runs by default at 320x240, and scales to 640x480.
#                           These values can be modified, and scaling of the window to change
#                           the scaled resolution is built in as well. Alt-enter toggles fullscreen.
#       * worlds - I also included a barebones world/sprites system. Worlds display all
#                           the sprites they contain, and you can subclass different worlds for
#                           different modes, such as one world for a menu, and another for
#                           the actual gameplay
#
#   main,.py
#   * Sets up log files - a lastlog.txt that shows printouts from the last run,
#                             - and a loghistory.txt that shows all printouts
#   * When errors happen, if run as a windows exe, output a "nice" dialog box
#               explaining the error
#   * Calls into core/libengine.py to run the actual code
#   * Just define a core/libengine.py with a run() method that takes no arguments
#   * Never change the code in this file, never have to build a new exe
#   * use the same exe for all of your games!
#   * release code patches that exe users can apply - exe and source users treated
#               equally!
#

import sys,os,traceback
android = None
try:
    import android
except:
    #This is really only for py2exe anyway, which I'm not using right now
    import urllib2,webbrowser,__future__,pygame,pygame.font,zipfile,traceback

if android:
    android.init()
    
def is_exe():
    return sys.argv and sys.argv[0].endswith(".exe")

if is_exe():
    from ctypes import c_int, WINFUNCTYPE, windll
    from ctypes.wintypes import HWND, LPCSTR, UINT
    prototype = WINFUNCTYPE(c_int, HWND, LPCSTR, LPCSTR, UINT)
    paramflags = (1, "hwnd", 0), (1, "text", "Hi"), (1, "caption", None), (1, "flags", 0)
    MessageBox = prototype(("MessageBoxA", windll.user32), paramflags)

    def show_popup(text):
        MessageBox(text=text, caption="Program Error")

abspath = os.path.abspath(os.curdir)
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("loghistory.txt", "a")
        self.log.write("This log contains debugging and error messages from all runs.\n")
        self.now = open("lastlog.txt","w")
        self.now.write("This log contains debugging and error messages from the last run.\n")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.now.write(message)
#~ import gc
#~ gc.enable()
#~ gc.set_debug(gc.DEBUG_LEAK)

sys.stderr = sys.stdout = Logger()
sys.path.insert(0,"")
try:
    from core import libengine
    libengine.run()
except:
    if not is_exe():
        raise
    type, value, sys.last_traceback = sys.exc_info()
    lines = traceback.format_exception(type, value,sys.last_traceback)
    print "".join(lines)
    show_popup("Oh no, there's been an error:\nMore detailed info available in lastlog.txt."+"".join(lines))