from configparser import ConfigParser
import mysql.connector

LINE_DELIVERY = 12
LINE_CAPACITY_TEST = 19

LATEST_STORED_QUERY = """SELECT record_id from test_result_trial_end
         where test_name = %s ORDER BY record_id DESC LIMIT 1"""
INSERT_TRIAL_END = """INSERT INTO test_result_trial_end
         (test_name, record_id, time, step_time, line, voltage, current, charging_capacity,
          discharging_capacity, wh_charging, wh_discharging, temperature, cycle_count,
           max_temperature, average_tension) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
INSERT_TRIAL = """INSERT INTO test_result
         (test_name, record_id, time, step_time, line, voltage, current, charging_capacity,
          discharging_capacity, wh_charging, wh_discharging, temperature, cycle_count)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
DELIVERY_QUERY = """SELECT discharging_capacity from test_result_trial_end
         where test_name = %s AND line = %s ORDER BY record_id ASC LIMIT 1"""
FIRST_CAPACITY_QUERY = """SELECT discharging_capacity from test_result_trial_end
         where test_name = %s AND line = %s ORDER BY record_id ASC LIMIT 1"""
ALL_CAPACITY_QUERY = """SELECT cycle_count, discharging_capacity from test_result_trial_end
         where test_name = %s AND line = %s ORDER BY record_id ASC"""


ADD_N = 20

class BatteryDB():
    def __init__(self):
        config = ConfigParser()
        config.read('db.config')
        self.host = config.get('client', 'host')
        self.port = config.getint('client', 'port')
        self.user = config.get('client', 'user')
        self.password = config.get('client', 'password')
        self.database = config.get('client', 'database')

        self.trial_end = []
        self.other_trials = []

        conn, cursor = self.connect()
        cursor.close()
        conn.close()

    def connect(self):
        conn = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    raise_on_warnings=True
                )
        cursor = conn.cursor(prepared=True)
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

    def add_record(self, trial_end_dict, others_trials):
        self.trial_end.append(trial_end_dict)
        self.other_trials.extend(others_trials)
        if len(self.trial_end) >= ADD_N:
            self._upload()

    def flush_add_record(self):
        self._upload()

    def _upload(self):
        conn, cursor = self.connect()
        try:
            cursor.executemany(INSERT_TRIAL, self.other_trials)
            cursor.executemany(INSERT_TRIAL_END, self.trial_end)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        self.trial_end = []
        self.other_trials = []
        cursor.close()
        conn.close()