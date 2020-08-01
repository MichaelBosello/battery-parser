#!/usr/bin/env python3

from threading import Thread
from queue import Queue, Empty

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from parser import Parser

TITLE = "Battery data manager"
WIDTH = 1000
HEIGHT = 600

class GUI():
    def __init__(self, root):
        self.root = root
        root.minsize(WIDTH, HEIGHT)
        tabControl = ttk.Notebook(root)
        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        tab3 = ttk.Frame(tabControl)
        tab4 = ttk.Frame(tabControl)
        tabControl.add(tab1, text='Upload')
        tabControl.add(tab2, text='Capacity')
        tabControl.add(tab3, text='High Sampling')
        tabControl.add(tab4, text='Main Cycle')
        tabControl.pack(expand=True, fill="both")

        frame_tab1 = tk.Frame(tab1)
        self.btn_info = tk.Button(frame_tab1, text="Software info", command=self.show_info)
        self.btn_open_file = tk.Button(frame_tab1, text="Import new data", command=self.open_file)
        self.upload_label = ttk.Label(frame_tab1, text="waiting for data")

        self.btn_info.grid(column=0, row=0, padx=10, pady=10)
        self.btn_open_file.grid(column=0, row=1, padx=10, pady=30)
        self.upload_label.grid(column=1, row=1, padx=10, pady=30)
        frame_tab1.pack(fill=tk.X)

        self.test_name = tk.StringVar()
        frame_name_t2 = tk.Frame(tab2)
        frame_name_t3 = tk.Frame(tab3)
        frame_name_t4 = tk.Frame(tab4)
        test_label_entry_t2 = ttk.Label(frame_name_t2, text="Test name:")
        test_label_entry_t3 = ttk.Label(frame_name_t3, text="Test name:")
        test_label_entry_t4 = ttk.Label(frame_name_t4, text="Test name:")
        test_name_entry_t2 = tk.Entry(frame_name_t2, textvariable=self.test_name, width=40)
        test_name_entry_t3 = tk.Entry(frame_name_t3, textvariable=self.test_name, width=40)
        test_name_entry_t4 = tk.Entry(frame_name_t4, textvariable=self.test_name, width=40)
        test_label_entry_t2.pack(side=tk.LEFT, padx=5, pady=5)
        test_label_entry_t3.pack(side=tk.LEFT, padx=5, pady=5)
        test_label_entry_t4.pack(side=tk.LEFT, padx=5, pady=5)
        test_name_entry_t2.pack(side=tk.LEFT, padx=5, pady=5)
        test_name_entry_t3.pack(side=tk.LEFT, padx=5, pady=5)
        test_name_entry_t4.pack(side=tk.LEFT, padx=5, pady=5)
        frame_name_t2.pack(fill=tk.X)
        frame_name_t3.pack(fill=tk.X)
        frame_name_t4.pack(fill=tk.X)

        self.delivery_soc = tk.StringVar()
        self.percent_delivery_soc = tk.StringVar()
        frame_soc_main = tk.Frame(tab2)
        frame_soc_label = tk.Frame(frame_soc_main)
        frame_soc_entry = tk.Frame(frame_soc_main)
        delivery_soc_entry = tk.Entry(frame_soc_entry, textvariable=self.delivery_soc, state='readonly', width=30)
        percent_delivery_soc_entry = tk.Entry(frame_soc_entry, textvariable=self.percent_delivery_soc, state='readonly', width=30)
        soc_label = ttk.Label(frame_soc_label, text="Delivery SOC:")
        percent_soc_label = ttk.Label(frame_soc_label, text="% delivery SOC:")
        soc_label.pack(anchor = tk.W, padx=5, pady=5)
        delivery_soc_entry.pack(padx=5, pady=5)
        percent_soc_label.pack(padx=5, pady=5)
        percent_delivery_soc_entry.pack(padx=5, pady=5)
        frame_soc_label.pack(side=tk.LEFT)
        frame_soc_entry.pack(side=tk.LEFT)
        self.compute_soc_btn = tk.Button(frame_soc_main, text="Calculate", command=self.delivery_click)
        self.compute_soc_btn.pack(side=tk.LEFT)
        frame_soc_main.pack(fill=tk.X)

        frame_tc = tk.Frame(tab2)
        tc_label = ttk.Label(frame_tc, text="Test Capacity")
        self.show_capacity_btn = tk.Button(frame_tc, text="Show capacity")
        tc_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.show_capacity_btn.pack(side=tk.LEFT, padx=5, pady=5)
        frame_tc.pack(fill=tk.X)

        self.capacity_tree = ttk.Treeview(tab2)
        self.capacity_tree["columns"]=("Cycle","Capacity")
        self.capacity_tree.column("Cycle")
        self.capacity_tree.column("Capacity", width=400)
        self.capacity_tree.heading("Cycle",text="Cycle")
        self.capacity_tree.heading("Capacity", text="Capacity")
        self.capacity_tree['show'] = 'headings'
        self.capacity_tree.pack(expand=True, fill="both")


        frame_t3 = tk.Frame(tab3)
        self.high_sampling_plot_btn = tk.Button(frame_t3, text="Show high sampling plot")
        self.high_sampling_plot_btn.pack(padx=10, pady=16)
        frame_t3.pack(fill=tk.X)


        frame_btn_main = tk.Frame(tab4)
        self.main_plot_btn = tk.Button(frame_btn_main, text="Show main cycle plot")
        self.main_plot_btn.pack(side=tk.LEFT, padx=(20, 5), pady=20)
        self.temperature_plot_btn = tk.Button(frame_btn_main, text="Show temperature plot")
        self.temperature_plot_btn.pack(side=tk.LEFT, padx=(10, 5), pady=20)
        frame_btn_main.pack(fill=tk.X)

        self.test_main_n_cycle = tk.StringVar()
        self.test_main_n_cycle.set("100")
        frame_main = tk.Frame(tab4)
        cycle_label = ttk.Label(frame_main, text="Cycle frequency: ")
        cycle_entry = tk.Entry(frame_main, textvariable=self.test_main_n_cycle, width=10)
        self.main_table_btn = tk.Button(frame_main, text="Show main cycle table")
        cycle_label.pack(side=tk.LEFT, padx=5, pady=5)
        cycle_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.main_table_btn.pack(side=tk.LEFT, padx=(30, 5), pady=5)
        frame_main.pack(fill=tk.X)

        self.main_tree = ttk.Treeview(tab4)
        self.main_tree["columns"]=("Cycle", "Ah", "Average V", "Max Temperature", "Wh")
        self.main_tree.heading("Cycle", text="Cycle")
        self.main_tree.heading("Ah", text="Ah")
        self.main_tree.heading("Average V", text="Average V")
        self.main_tree.heading("Max Temperature", text="Max Temperature")
        self.main_tree.heading("Wh", text="Wh")
        self.main_tree['show'] = 'headings'
        self.main_tree.pack(expand=True, fill="both")


        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws/2) - (WIDTH/2)
        y = (hs/2) - (HEIGHT/2)
        root.geometry('+%d+%d' % (x, y))

        self.queue = Queue()
        self.tasks = Tasks(self.queue)
        self.root.after(200, self.process_queue)

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

    def delivery_click(self):
        self.delivery_soc.set("")
        self.percent_delivery_soc.set("")
        if not self.test_name.get():
            self.show_error("Enter a test name")
        else:
            self.compute_soc_btn['state'] = 'disabled'
            process = Thread(target=self.tasks.delivery_SOC, args=(self.test_name.get(),))
            process.daemon = True
            process_percent = Thread(target=self.tasks.delivery_SOC_percent, args=(self.test_name.get(),))
            process_percent.daemon = True
            process.start()
            process_percent.start()

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
        self.compute_soc_btn['state'] = 'normal'

    def show_upload_progress(self, message):
        self.upload_label['text'] = message
        if message == "complete":
            self.btn_open_file["text"] = "Import new data"

    def show_delivery(self, soc):
        self.delivery_soc.set(str(soc))
        self.compute_soc_btn['state'] = 'normal'

    def show_delivery_percent(self, soc_percent):
        self.percent_delivery_soc.set(str(soc_percent))
        self.compute_soc_btn['state'] = 'normal'

    def process_queue(self):
        try:
            msg = self.queue.get(0)
        except Empty:
            self.root.after(200, self.process_queue)
            return

        if msg[0] == "error":
            self.show_error(msg[1])
        if msg[0] == "upload-progress":
            self.show_upload_progress(msg[1])
        if msg[0] == "delivery_SOC":
            self.show_delivery(msg[1])
        if msg[0] == "delivery_SOC_percent":
            self.show_delivery_percent(msg[1])

        self.process_queue()

class Tasks():
    def __init__(self, queue):
        self.queue = queue
        self.parser = None

    def __build_parser(self):
        if self.parser is None:
            try:
                self.parser = Parser()
            except Exception as e:
                self.queue.put(("upload-progress", "Error connecting to database"))
                self.parser = None
                self.queue.put(("error", str(e)))

    def process_file(self, filepath):
        self.__build_parser()
        if self.parser is not None:
            try:
                self.parser.upload_to_db(filepath, self.queue)
            except Exception as e:
                self.queue.put(("error", str(e)))

    def delivery_SOC(self, test_name):
        self.__build_parser()
        if self.parser is not None:
            try:
                delivery = self.parser.delivery_SOC(test_name)
                if delivery is None:
                    self.queue.put(("error", "No data for " + test_name))
                else:
                    self.queue.put(("delivery_SOC", str(delivery)))
            except Exception as e:
                self.queue.put(("error", str(e)))

    def delivery_SOC_percent(self, test_name):
        self.__build_parser()
        if self.parser is not None:
            try:
                delivery_percent = self.parser.delivery_SOC_percent(test_name)
                if delivery_percent is not None:
                    self.queue.put(("delivery_SOC_percent", str(delivery_percent)))
            except Exception as e:
                self.queue.put(("error", str(e)))

    def capacity_tests(self, test_name):
        self.__build_parser()
        if self.parser is not None:
            try:
                tests = self.parser.capacity_tests(test_name)
                if tests is None or not tests:
                    self.queue.put(("error", "No data for " + test_name))
                else:
                    self.queue.put(("capacity_tests", str(tests)))
            except Exception as e:
                self.queue.put(("error", str(e)))

root = tk.Tk()
root.title(TITLE)
GUI(root)
root.mainloop()