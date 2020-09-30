import ntpath
import traceback
import threading
import csv

from database import BatteryDB

class BatteryParser():
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
                            try:
                                for _ in range(latest - current_line):
                                    next(f)
                            except Exception as e:
                                traceback.print_exception(type(e), e, e.__traceback__)
                                raise type(e)("File already fully uploaded")
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


    def delivery_SOC(self, test_name):
        try:
            return self.db.get_delivery_capacity(test_name)
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            raise type(e)("Error getting data from server. Details: " + str(e))

    def delivery_SOC_percent(self, test_name):
        try:
            delivery_capacity = self.db.get_delivery_capacity(test_name)
            capacity = self.db.get_first_capacity(test_name)
            if delivery_capacity is None or capacity is None:
                return None
            return delivery_capacity/capacity
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            raise type(e)("Error getting data from server. Details: " + str(e))

    def capacity_tests(self, test_name):
        try:
            return self.db.get_test_capacity(test_name)
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            raise type(e)("Error getting data from server. Details: " + str(e))

    def main_dis_table(self, test_name, frequency):
        try:
            return self.db.get_main_dis_table(test_name, frequency)
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            raise type(e)("Error getting data from server. Details: " + str(e))

    def export_table(self, table, export_file):
        csv_writer = csv.writer(export_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for record in table:
            csv_writer.writerow(record)

    def discharge(self, test_name):
        try:
            return self.db.get_discharge(test_name)
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            raise type(e)("Error getting data from server. Details: " + str(e))

    def temperature(self, test_name):
        try:
            return self.db.get_temperature(test_name)
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            raise type(e)("Error getting data from server. Details: " + str(e))

    def wh(self, test_name):
        try:
            return self.db.get_wh(test_name)
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            raise type(e)("Error getting data from server. Details: " + str(e))

    def high_sampling(self, test_name):
        try:
            hs_up = self.db.get_high_sampling_up(test_name)
            hs_down = self.db.get_high_sampling_down(test_name)
            if hs_up is None or not hs_up or hs_down is None or not hs_down:
                return None
            results = []
            hs_len = min(len(hs_up), len(hs_down))
            for i in range(0, hs_len):
                if hs_up[i][3] == 1:
                    resistence = []
                    capacity = []
                    results.append((resistence, capacity))
                deltaV = hs_up[i][0]-hs_down[i][0]
                deltaI = hs_up[i][1]-hs_down[i][1]
                r = (deltaV/deltaI)*1000
                resistence.append(r)
                capacity.append(hs_down[i][2])
            return results
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            raise type(e)("Error getting data from server. Details: " + str(e))



