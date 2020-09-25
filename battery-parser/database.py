from configparser import ConfigParser
import mysql.connector
import pathlib
import os

LINE_DELIVERY = 12
LINE_CAPACITY_TEST = 19
MAIN_CYCLE_DISCHARGE = 40
HIGH_SAMPLING_UP = 29
HIGH_SAMPLING_DOWN = 30

LATEST_STORED_QUERY = """SELECT record_id from test_result_trial_end
         where test_name = %s ORDER BY record_id DESC LIMIT 1"""
INSERT_TRIAL_END = """INSERT INTO test_result_trial_end
         (test_name, record_id, time, step_time, line, voltage, current, charging_capacity,
          discharging_capacity, wh_charging, wh_discharging, temperature, cycle_count,
           max_temperature, average_tension) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
INSERT_TRIAL = """INSERT INTO test_result
         (test_name, record_id, time, step_time, line, voltage, current, charging_capacity,
          discharging_capacity, wh_charging, wh_discharging, temperature, cycle_count)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
DELIVERY_QUERY = """SELECT discharging_capacity from test_result_trial_end
         where test_name = %s AND line = %s ORDER BY record_id ASC LIMIT 1"""
FIRST_CAPACITY_QUERY = """SELECT discharging_capacity from test_result_trial_end
         where test_name = %s AND line = %s ORDER BY record_id ASC LIMIT 1"""
ALL_CAPACITY_QUERY = """SELECT cycle_count, discharging_capacity from test_result_trial_end
         where test_name = %s AND line = %s ORDER BY record_id ASC"""
ALL_DIS_MAIN_QUERY = """SELECT discharging_capacity, average_tension, max_temperature, wh_discharging from test_result_trial_end
         where test_name = %s AND line = %s AND (cycle_count MOD %s) = 0 ORDER BY record_id ASC"""
DIS_CAPACITY_QUERY = """SELECT discharging_capacity from test_result_trial_end
         where test_name = %s AND line = %s ORDER BY record_id ASC"""
TEMPERATURE_QUERY = """SELECT max_temperature from test_result_trial_end
         where test_name = %s AND line = %s ORDER BY record_id ASC"""
WH_QUERY = """SELECT wh_discharging from test_result_trial_end
         where test_name = %s AND line = %s ORDER BY record_id ASC"""
HIGH_SAMPLING_QUERY = """SELECT voltage, current, discharging_capacity, cycle_count from test_result_trial_end
         where test_name = %s AND line = %s ORDER BY record_id ASC"""

ADD_N = 10000

class BatteryDB():
    def __init__(self):
        config = ConfigParser()
        config.read(self.resource_path('db.config'))
        self.host = config.get('client', 'host')
        self.port = config.getint('client', 'port')
        self.user = config.get('client', 'user')
        self.password = config.get('client', 'password')
        self.database = config.get('client', 'database')

        self.trial_end = []
        self.other_trials = []

        self.upload_conn, self.upload_cursor = self.connect()

    def resource_path(self, relative_path):
        base_path = pathlib.Path(__file__).parent.absolute()
        return os.path.join(base_path, relative_path)

    def connect(self):
        conn = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    raise_on_warnings=True
                )
        cursor = conn.cursor()
        return conn, cursor

    def get_latest_stored(self, test_name):
        conn, cursor = self.connect()
        cursor.execute(LATEST_STORED_QUERY, (test_name,))
        latest = cursor.fetchone()
        if latest is not None:
            latest = latest[0]
        cursor.close()
        conn.close()
        return latest

    def get_delivery_capacity(self, test_name):
        conn, cursor = self.connect()
        cursor.execute(DELIVERY_QUERY, (test_name, LINE_DELIVERY))
        capacity = cursor.fetchone()
        if capacity is not None:
            capacity = capacity[0]
        cursor.close()
        conn.close()
        return capacity

    def get_first_capacity(self, test_name):
        conn, cursor = self.connect()
        cursor.execute(FIRST_CAPACITY_QUERY, (test_name, LINE_CAPACITY_TEST))
        capacity = cursor.fetchone()
        if capacity is not None:
            capacity = capacity[0]
        cursor.close()
        conn.close()
        return capacity

    def get_test_capacity(self, test_name):
        conn, cursor = self.connect()
        cursor.execute(ALL_CAPACITY_QUERY, (test_name, LINE_CAPACITY_TEST))
        capacity = cursor.fetchall()
        cursor.close()
        conn.close()
        return capacity

    def get_main_dis_table(self, test_name, frequency):
        conn, cursor = self.connect()
        cursor.execute(ALL_DIS_MAIN_QUERY, (test_name, MAIN_CYCLE_DISCHARGE, frequency))
        table = cursor.fetchall()
        cursor.close()
        conn.close()
        return table

    def get_discharge(self, test_name):
        conn, cursor = self.connect()
        cursor.execute(DIS_CAPACITY_QUERY, (test_name, MAIN_CYCLE_DISCHARGE))
        discharge = cursor.fetchall()
        cursor.close()
        conn.close()
        return discharge

    def get_temperature(self, test_name):
        conn, cursor = self.connect()
        cursor.execute(TEMPERATURE_QUERY, (test_name, MAIN_CYCLE_DISCHARGE))
        temperature = cursor.fetchall()
        cursor.close()
        conn.close()
        return temperature

    def get_wh(self, test_name):
        conn, cursor = self.connect()
        cursor.execute(WH_QUERY, (test_name, MAIN_CYCLE_DISCHARGE))
        wh = cursor.fetchall()
        cursor.close()
        conn.close()
        return wh

    def get_high_sampling_up(self, test_name):
        conn, cursor = self.connect()
        cursor.execute(HIGH_SAMPLING_QUERY, (test_name, HIGH_SAMPLING_UP))
        hs = cursor.fetchall()
        cursor.close()
        conn.close()
        return hs

    def get_high_sampling_down(self, test_name):
        conn, cursor = self.connect()
        cursor.execute(HIGH_SAMPLING_QUERY, (test_name, HIGH_SAMPLING_DOWN))
        hs = cursor.fetchall()
        cursor.close()
        conn.close()
        return hs

    def add_record(self, trial_end_dict, others_trials):
        self.trial_end.append(trial_end_dict)
        self.other_trials.extend(others_trials)
        if len(self.trial_end) + len(self.other_trials) >= ADD_N:
            self._upload()

    def flush_add_record(self):
        self._upload()

    def _upload(self):
        try:
            self.upload_cursor.executemany(INSERT_TRIAL, self.other_trials)
            self.upload_cursor.executemany(INSERT_TRIAL_END, self.trial_end)
            self.upload_conn.commit()
        except Exception as e:
            self.upload_conn.rollback()
            raise e
        self.trial_end = []
        self.other_trials = []
