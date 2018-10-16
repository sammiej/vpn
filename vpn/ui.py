# #!/usr/bin/python
# https://tkdocs.com/tutorial/firstexample.html
#
from tkinter import *
from tkinter import ttk
import command as cmd
from util import Message, UMessage, Q, MQ, cont, toggle_auto
from logger import logger
from queue import Empty, Full

screen = {}

def run():
    root = Tk()
    root.title("VPN")

    mainframe = ttk.Frame(root, padding="30 30 100 100")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    port = StringVar()
    IP = StringVar()
    screen["port"] = port
    sharedSecret = StringVar()
    screen["sharedSecret"] = sharedSecret
    dataToSend = StringVar()
    screen["dataToSend"] = dataToSend
    dataReceived = StringVar()
    screen["dataReceived"] = dataReceived

    portEntry = ttk.Entry(mainframe, width=7, textvariable=port)
    IPEntry = ttk.Entry(mainframe, width=24, textvariable=IP)
    sharedSecretEntry = ttk.Entry(mainframe, width=7, textvariable=sharedSecret)
    dataToSendEntry = ttk.Entry(mainframe, width=7, textvariable=dataToSend)
    dataReceivedEntry = ttk.Entry(mainframe, width=7, textvariable=dataReceived)

    IPEntry.grid(column=2, row=3, sticky=(W,E))
    portEntry.grid(column=2, row=2, sticky=(W, E))
    sharedSecretEntry.grid(column=2, row=4, sticky=(W, E))
    dataToSendEntry.grid(column=2, row=5, sticky=(W, E))
    dataReceivedEntry.grid(column=2, row=6, sticky=(W, E))

    ttk.Label(mainframe, text="Port").grid(column=1, row=2, sticky=W)
    ttk.Label(mainframe, text="IP").grid(column=1, row=3, sticky=W)
    ttk.Label(mainframe, text="Shared Secret").grid(column=1, row=4, sticky=W)
    ttk.Label(mainframe, text="Data to Send").grid(column=1, row=5, sticky=W)
    ttk.Label(mainframe, text="Data Received").grid(column=1, row=6, sticky=W)

    scrollbar = Scrollbar(mainframe, orient="vertical")
    scrollbar.grid(column=2,row=7, sticky=(N, S))

    listbox = Text(mainframe, borderwidth=3, width=100, height=20, relief="sunken")
    screen["listbox"] = listbox
    listbox.grid(column=1, row=7,columnspan=3,rowspan=2, sticky=(W, E))

    ttk.Button(mainframe, text="Automatic", command=automaticClick).grid(column=4, row=7, sticky=W)
    ttk.Button(mainframe, text="Continue", command=continueClick).grid(column=4, row=8, sticky=W)

    scrollbar.config(command=listbox.yview)


    # toggle views
    toggleVal = IntVar()
    screen["ip"] = IP
    b = ttk.Button(mainframe)

    def toggle():
        b.forget()
        IPEntry.delete(0, END)
        if(toggleVal.get()==1):
            IPEntry.config(state=NORMAL)
            b.config(text="Connect", command=connectClick)
            b.grid(column=3, row=3)
        elif(toggleVal.get()==2):
            IPEntry.config(state=DISABLED)
            b.config(text="Listen", command=listenClick)
            b.grid(column=3, row=2)

    clientToggle = ttk.Radiobutton(mainframe, text="Client", variable=toggleVal, value=1, command=toggle)
    serverToggle = ttk.Radiobutton(mainframe, text="Server", variable=toggleVal, value=2, command=toggle)

    clientToggle.grid(column=4, row=3, sticky=W)
    serverToggle.grid(column=5, row=3, sticky=W)
    clientToggle.invoke()

    # buttons
    ttk.Button(mainframe, text="Send", command=sendClick).grid(column=3, row=5, sticky=W)

    #padding
    for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

    def lloop():
        try:
            umsg = MQ.get(timeout=0.05)
            if umsg is None:
                # TODO: quit application here?
                pass
            if umsg.mtype == UMessage.DISPLAY:
                screen["listbox"].insert(END, umsg.text)
            if umsg.mtype == UMessage.RECEIVE:
                screen["dataReceived"].set(umsg.text)
            MQ.task_done()
        except Empty:
            pass
        root.after(200, lloop)

    # Listen for events periodically
    lloop()
    root.mainloop()

def continueClick():
    cont()

def automaticClick():
    if toggle_auto():
        logger.info("Communication process is now automatic")
    else:
        logger.info("Communication process is now manual")

def sendClick():
    data = screen["dataToSend"].get()
    if data:
        screen["dataToSend"].set("")
        logger.info("sending: {}".format(data))
        try:
            msg = Message(Message.SEND, data)
            Q.put_nowait(msg)
        except Full:
            logger.error("Network queue is full!")

def connectClick():
    port = screen["port"].get()
    ip = screen["ip"].get()
    if not port:
        port = 8888
    else:
        port = int(port)
    if not ip:
        ip = "127.0.0.1"
    sharedSecret = screen["sharedSecret"].get()
    logger.debug("selected ip: {}, port: {}".format(ip, port))
    c = cmd.ClientConnectCommand(ip, port, sharedSecret)
    c.execute()

def listenClick():
    port = screen["port"].get()
    if not port:
        port = 8888
    else:
        port = int(port)
    sharedSecret = screen["sharedSecret"].get()
    logger.debug("port selected: {}".format(port))
    s = cmd.ServerListenCommand(port, sharedSecret)
    s.execute()
