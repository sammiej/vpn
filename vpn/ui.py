# #!/usr/bin/python
# https://tkdocs.com/tutorial/firstexample.html
#
from tkinter import *
from tkinter import ttk

root = Tk()
root.title("VPN")

mainframe = ttk.Frame(root, padding="30 30 100 100")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

port = StringVar()
sharedSecret = StringVar()
datatoSend = StringVar()
dataReceived = StringVar()

portEntry = ttk.Entry(mainframe, width=7, textvariable=port)
sharedSecretEntry = ttk.Entry(mainframe, width=7, textvariable=sharedSecret)
datatoSendEntry = ttk.Entry(mainframe, width=7, textvariable=datatoSend)
dataReceivedEntry = ttk.Entry(mainframe, width=7, textvariable=dataReceived)

portEntry.grid(column=2, row=2, sticky=(W, E))
sharedSecretEntry.grid(column=2, row=4, sticky=(W, E))
datatoSendEntry.grid(column=2, row=5, sticky=(W, E))
dataReceivedEntry.grid(column=2, row=6, sticky=(W, E))

# labels
ttk.Label(mainframe, text="Port").grid(column=1, row=2, sticky=W)
ttk.Label(mainframe, text="IP").grid(column=1, row=3, sticky=W)
ttk.Label(mainframe, text="Shared Secret").grid(column=1, row=4, sticky=W)
ttk.Label(mainframe, text="Data to Send").grid(column=1, row=5, sticky=W)
ttk.Label(mainframe, text="Data Received").grid(column=1, row=6, sticky=W)

# list box
scrollbar = Scrollbar(mainframe, orient="vertical")
scrollbar.grid(column=2,row=7, sticky=(N, S))

listbox = Text(mainframe, borderwidth=3, width = 30, relief="sunken", yscrollcommand=scrollbar.set)
listbox.grid(column=2, row=7, sticky=(W, E))

# scrollbar NOT WORKING
scrollbar['command'] = listbox.yview
ttk.Button(mainframe, text="Continue").grid(column=3, row=7, sticky=W)

scrollbar.config(command=listbox.yview)

listbox.config(yscrollcommand=scrollbar.set)

# toggle views

def clientScreen():
    listenButton.config(text="Listen")

toggleVal = IntVar()
IP = StringVar()
IPEntry = ttk.Entry(mainframe, width=24, textvariable=IP)
IPEntry.grid(column=2, row=3)
b = ttk.Button(mainframe)
def toggle():
    b.forget()
    IPEntry.delete(0, END)
    if(toggleVal.get()==1):
        IPEntry.config(state=NORMAL)
        b.config(text="Connect")
        b.grid(column=3, row=3)
    elif(toggleVal.get()==2):
        IPEntry.config(state=DISABLED)
        b.config(text="Listen")
        b.grid(column=3, row=2)

clientToggle = ttk.Radiobutton(mainframe, text="Client", variable=toggleVal, value=1, command=toggle)
serverToggle = ttk.Radiobutton(mainframe, text="Server", variable=toggleVal, value=2, command=toggle)

clientToggle.grid(column=4, row=3, sticky=W)
serverToggle.grid(column=5, row=3, sticky=W)
clientToggle.invoke()

# buttons
ttk.Button(mainframe, text="Send").grid(column=3, row=5, sticky=W)


#padding
for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

root.mainloop()
