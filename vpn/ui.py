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

sharedSecret = StringVar()
datatoSend = StringVar()
dataReceived = StringVar()

sharedSecretEntry = ttk.Entry(mainframe, width=7, textvariable=sharedSecret)
datatoSendEntry = ttk.Entry(mainframe, width=7, textvariable=datatoSend)
dataReceivedEntry = ttk.Entry(mainframe, width=7, textvariable=dataReceived)

sharedSecretEntry.grid(column=2, row=2, sticky=(W, E))
datatoSendEntry.grid(column=2, row=3, sticky=(W, E))
dataReceivedEntry.grid(column=2, row=4, sticky=(W, E))

# labels
ttk.Label(mainframe, text="Shared Secret").grid(column=1, row=2, sticky=W)
ttk.Label(mainframe, text="Data to Send").grid(column=1, row=3, sticky=W)
ttk.Label(mainframe, text="Data Received").grid(column=1, row=4, sticky=W)

# text box
textbox = Text(mainframe, borderwidth=3, width = 30, relief="sunken")
textbox.grid(column=2, row=5, sticky=(W, E))


toggleVal = IntVar()
clientToggle = ttk.Radiobutton(mainframe, text="Client", variable=toggleVal, value=1)
serverToggle = ttk.Radiobutton(mainframe, text="Server", variable=toggleVal, value=2)

clientToggle.grid(column=3, row=1, sticky=W)
serverToggle.grid(column=4, row=1, sticky=W)
# buttons

ttk.Button(mainframe, text="Continue").grid(column=3, row=5, sticky=W)

ttk.Button(mainframe, text="Send").grid(column=3, row=3, sticky=W)

#padding
for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

root.mainloop()
