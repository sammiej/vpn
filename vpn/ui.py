# #!/usr/bin/python
# https://tkdocs.com/tutorial/firstexample.html
#
from tkinter import *
from tkinter import ttk
import command as cmd
from connection import Message, UMessage, Q, MQ
import logging
from queue import Empty


screen = {}

def run():
    root = Tk()
    root.title("VPN")
    
    mainframe = ttk.Frame(root, padding="30 30 100 100")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)
    
    sharedSecret = StringVar()
    screen["sharedSecret"] = sharedSecret
    dataToSend = StringVar()
    screen["dataToSend"] = dataToSend
    dataReceived = StringVar()

    sharedSecretEntry = ttk.Entry(mainframe, width=7, textvariable=sharedSecret)
    dataToSendEntry = ttk.Entry(mainframe, width=7, textvariable=dataToSend)
    dataReceivedEntry = ttk.Entry(mainframe, width=7, textvariable=dataReceived)

    sharedSecretEntry.grid(column=2, row=2, sticky=(W, E))
    dataToSendEntry.grid(column=2, row=3, sticky=(W, E))
    dataReceivedEntry.grid(column=2, row=4, sticky=(W, E))

    # labels
    ttk.Label(mainframe, text="Shared Secret").grid(column=1, row=2, sticky=W)
    ttk.Label(mainframe, text="Data to Send").grid(column=1, row=3, sticky=W)
    ttk.Label(mainframe, text="Data Received").grid(column=1, row=4, sticky=W)
    
    toggleVal = IntVar()
    clientToggle = ttk.Radiobutton(mainframe, text="Client", variable=toggleVal, value=1)
    serverToggle = ttk.Radiobutton(mainframe, text="Server", variable=toggleVal, value=2)

    clientToggle.grid(column=3, row=1, sticky=W)
    serverToggle.grid(column=4, row=1, sticky=W)
    # buttons
    
    ttk.Button(mainframe, text="Continue", command=continueClick).grid(column=2, row=5, sticky=W)

    ttk.Button(mainframe, text="Send", command=sendClick).grid(column=3, row=3, sticky=W)

    #padding
    for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

    def lloop():
        try:
            umsg = MQ.get(timeout=0.2)
            if umsg is None:
                # TODO: quit application here?
                pass
            if umsg.mtype == UMessage.DISPLAY:
                screen["sharedSecret"].set(umsg.text)
            MQ.task_done()
        except Empty:
            pass
        root.after(200, lloop)
        
    # Listen for events periodically    
    lloop()
    root.mainloop()

def continueClick():
    # TODO: currently using shared secret as input and this click is used to listen as server
    print("sharedSecret: {}".format(screen["sharedSecret"].get()))
    screen["sharedSecret"].set("stuff")
    try:
        msg = Message(Message.SEND, "hey!")
        Q.put_nowait(msg)
    except:
        import traceback
        tb = traceback.format_exc()
        print (tb)
        logging.error("Q is full!")
    #s = cmd.ServerListenCommand()
    #s.execute()

def sendClick():
    # TODO: currently using this as a way to connect as client
    print("dataToSend: {}".format(screen["dataToSend"].get()))
    c = cmd.ClientConnectCommand("192.168.1.67", 8888)
    c.execute()
