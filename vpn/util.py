from queue import Queue
import threading

MQ = Queue() # queue for talking to main thread
Q = Queue() # queue for talking to network thread

_halt = False
_cond = threading.Condition(threading.Lock())
_halt_thread = None
_auto = False

"""
Message that is placed on the queue to be consumed by network threads
"""
class Message(object):
    SEND = 0 # send message over network
    def __init__(self, mtype, text):
        self.mtype = mtype
        self.bytes = text.encode()

"""
Message that is placed on the main queue to be consumed by the main thread
"""
class UMessage(object):
    DISPLAY = 0 # display in log
    RECEIVE = 1 # display in received
    def __init__(self, mtype, text):
        self.mtype = mtype
        self.text = text



"""
Halts the thread at point of calling, can only continue after
being notified by the main thread. Should only be called by one thread.
"""
def halt():
    global _halt_thread
    global _auto
    global _halt
    
    c_thread = threading.current_thread()
    _cond.acquire()
    if not _auto:
        if _halt_thread == None:
            _halt_thread = c_thread
        elif _halt_thread != c_thread:
            _cond.release()
            raise Exception("Halting called by more than 1 thread!")
        _halt = True
        while _halt:
            _cond.wait()
    _cond.release()

"""
Notifies the halted thread to continue execution, should only be
called by the main thread.
"""
def cont():
    global _auto
    global _halt
    
    assert threading.current_thread() == threading.main_thread()    
    _cond.acquire()    
    if not _auto:
        _halt = False
        _cond.notify()
    _cond.release()

"""
Post-Condition:
  return the auto value after calling
"""
def toggle_auto():
    global _auto
    global _halt
    
    assert threading.current_thread() == threading.main_thread()        
    val = False
    _cond.acquire()
    if _auto:
        _auto = False
        val = _auto
    else:
        _auto = True
        _halt = False
        val = _auto
        _cond.notify()
    _cond.release()
    return val
