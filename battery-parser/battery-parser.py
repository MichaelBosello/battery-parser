#!/usr/bin/env python3

from threading import Thread
from queue import Queue, Empty

import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

from parser import Parser

class GUI():
    def __init__(self, master):
        self.master = master
        self.btn_open_file = tk.Button(text="Import new data", command=self.open_file)
        self.btn_open_file.pack()

        self.queue = Queue()
        self.tasks = Tasks(self.queue)
        self.master.after(200, self.process_queue)

    def open_file(self):
        filepath = askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not filepath:
            return
        process = Thread(target=self.tasks.process_file, args=(filepath,))
        process.daemon = True
        process.start()

    def show_error(self, message):
        messagebox.showinfo("Error", message)

    def process_queue(self):
        try:
            msg = self.queue.get(0)
        except Empty:
            self.master.after(200, self.process_queue)
            return

        if msg[0] == "error":
            self.show_error(msg[1])

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
                self.parser = None
                self.queue.put(("error", str(e)))

        if self.parser is not None:
            try:
                self.parser.upload_to_db(filepath)
            except Exception as e:
                self.queue.put(("error", str(e)))

root = tk.Tk()
root.title("Battery data manager")
GUI(root)
root.mainloop()