#!/usr/bin/env python3

from threading import Thread
from queue import Queue, Empty

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from parser import Parser

TITLE = "Battery data manager"

class GUI():
    def __init__(self, master):
        self.master = master
        master.minsize(500, 200)
        tabControl = ttk.Notebook(master)
        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        tabControl.add(tab1, text='Upload')
        tabControl.add(tab2, text='View data')
        tabControl.pack(expand=1, fill="both")
        self.btn_info = tk.Button(tab1, text="Software info", command=self.show_info)
        self.btn_open_file = tk.Button(tab1, text="Import new data", command=self.open_file)
        self.upload_label = ttk.Label(tab1, text="waiting for data")

        self.btn_info.grid(column=0, row=0, padx=10, pady=10)
        self.btn_open_file.grid(column=0, row=1, padx=10, pady=30)
        self.upload_label.grid(column=1, row=1, padx=10, pady=30)

        self.queue = Queue()
        self.tasks = Tasks(self.queue)
        self.master.after(200, self.process_queue)

    def open_file(self):
        if self.btn_open_file["text"] != "Stop":
            filepath = askopenfilename(filetypes=[("Text Files", "*.txt")])
            if not filepath:
                return
            self.btn_open_file["text"] = "Stop"
            self.upload_process = Thread(target=self.tasks.process_file, args=(filepath,))
            self.upload_process.daemon = True
            self.upload_process.start()
        else:
            self.upload_process.stop = True
            self.btn_open_file["text"] = "Import new data"
            self.queue.put(("upload-progress", "interrupted"))

    def show_info(self):
        messagebox.showinfo(TITLE, 
        """
        Author: Michael Bosello\n
        LICENSE: Apache License 2.0\n
        No warranties\n\n
        Get one copy at: \nwww.apache.org/licenses/LICENSE-2.0
        """)

    def show_error(self, message):
        messagebox.showinfo("Error", message)
        self.btn_open_file["text"] = "Import new data"

    def show_upload_progress(self, message):
        self.upload_label['text'] = message
        if message == "complete":
            self.btn_open_file["text"] = "Import new data"

    def process_queue(self):
        try:
            msg = self.queue.get(0)
        except Empty:
            self.master.after(200, self.process_queue)
            return

        if msg[0] == "error":
            self.show_error(msg[1])
        if msg[0] == "upload-progress":
            self.show_upload_progress(msg[1])

        self.process_queue()

class Tasks():
    def __init__(self, queue):
        self.queue = queue
        self.parser = None

    def process_file(self, filepath):
        if self.parser is None:
            try:
                self.parser = Parser()
            except Exception as e:
                self.queue.put(("upload-progress", "Error connecting to database"))
                self.parser = None
                self.queue.put(("error", str(e)))

        if self.parser is not None:
            try:
                self.parser.upload_to_db(filepath, self.queue)
            except Exception as e:
                self.queue.put(("error", str(e)))

root = tk.Tk()
root.title(TITLE)
GUI(root)
root.mainloop()