import ntpath
import traceback
import threading

from database import BatteryDB

class Parser():
    def __init__(self):
        try:
            self.db = BatteryDB()
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            raise type(e)("Cannot connect to the server. Details: " + str(e))

    def upload_to_db(self, path, queue):
        queue.put(("upload-progress", "opening file"))
        test_name = ntpath.basename(path)
        test_name = test_name[:test_name.rfind(".")]
        queue.put(("upload-progress", "connecting to database"))
        try:
            latest = self.db.get_latest_stored(test_name)
            if latest is None:
                latest = -1
        except Exception as e:
            queue.put(("upload-progress", "error"))
            traceback.print_exception(type(e), e, e.__traceback__)
            raise type(e)("Error getting data from server. Details: " + str(e))

        try:
            with open(path, errors="ignore") as f:
                columns = ["Time", "DataSet", "Date", "DateTime",
                        "t-Step", "Line", "Command", "U[V]", "I[A]", "Ah-Ch-Set", "Ah-Dis-Set",
                        "Wh-Ch-Set", "Wh-Dis-Set", "T1", "Cyc-Count", "State"]

                max_temperature = -273.15
                tension_sum = 0
                tension_count = 0

                line_state_one = []

                queue.put(("upload-progress", "start parsing file"))
                this_thread = threading.currentThread()
                for line in f:
                    if getattr(this_thread, "stop", False):
                        break
                    if line.startswith("~"):
                        continue
                    else:
                        line_dictionary = {}
                        for index, elem in enumerate(line.split(' ')):
                            line_dictionary[columns[index]] = elem

                        current_line = int(line_dictionary["DataSet"])
                        if current_line < latest:
                            queue.put(("upload-progress", "skipping already uploaded"))
                            for _ in range(latest - current_line):
                                next(f)
                            continue

                        if line_dictionary["Command"] != "Discharge" and line_dictionary["Command"] != "Charge":
                            line_state_one.append((test_name, line_dictionary["DataSet"],
                                        line_dictionary["Time"], line_dictionary["t-Step"],
                                        line_dictionary["Line"], line_dictionary["U[V]"],
                                        line_dictionary["I[A]"], line_dictionary["Ah-Ch-Set"],
                                        line_dictionary["Ah-Dis-Set"], line_dictionary["Wh-Ch-Set"],
                                        line_dictionary["Wh-Dis-Set"], line_dictionary["T1"],
                                        line_dictionary["Cyc-Count"]))
                            continue

                        if int(line_dictionary["State"]) != 2:
                            if float(line_dictionary["T1"]) > max_temperature:
                                max_temperature = float(line_dictionary["T1"])
                            tension_sum += float(line_dictionary["U[V]"])
                            tension_count += 1
                            line_state_one.append((test_name, line_dictionary["DataSet"],
                                        line_dictionary["Time"], line_dictionary["t-Step"],
                                        line_dictionary["Line"], line_dictionary["U[V]"],
                                        line_dictionary["I[A]"], line_dictionary["Ah-Ch-Set"],
                                        line_dictionary["Ah-Dis-Set"], line_dictionary["Wh-Ch-Set"],
                                        line_dictionary["Wh-Dis-Set"], line_dictionary["T1"],
                                        line_dictionary["Cyc-Count"]))
                        else:
                            queue.put(("upload-progress", "processing line " + line_dictionary["DataSet"]))

                            avg_tension = tension_sum/tension_count

                            line_tuple = ((test_name, line_dictionary["DataSet"],
                                        line_dictionary["Time"], line_dictionary["t-Step"],
                                        line_dictionary["Line"], line_dictionary["U[V]"],
                                        line_dictionary["I[A]"], line_dictionary["Ah-Ch-Set"],
                                        line_dictionary["Ah-Dis-Set"], line_dictionary["Wh-Ch-Set"],
                                        line_dictionary["Wh-Dis-Set"], line_dictionary["T1"],
                                        line_dictionary["Cyc-Count"], max_temperature, avg_tension))
                            self.db.add_record(line_tuple, line_state_one)

                            max_temperature = -273.15
                            tension_sum = 0
                            tension_count = 0
                            line_state_one = []
            self.db.flush_add_record()
            queue.put(("upload-progress", "complete"))
        except Exception as e:
            queue.put(("upload-progress", "error"))
            traceback.print_exception(type(e), e, e.__traceback__)
            raise type(e)("Error parsing the provided file. Details: " + str(e))



