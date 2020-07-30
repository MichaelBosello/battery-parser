from configparser import ConfigParser
import mysql.connector

LATEST_STORED_QUERY = """SELECT record_id from test_result_trial_end
         where test_name = %s ORDER BY record_id DESC"""
INSERT_TRIAL_END = """INSERT INTO test_result_trial_end
         (test_name, record_id, time, step_time, line, voltage, current, charging_capacity,
          discharging_capacity, wh_charging, wh_discharging, temperature, cycle_count,
           max_temperature, average_tension) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
INSERT_TRIAL = """INSERT INTO test_result
         (test_name, record_id, time, step_time, line, voltage, current, charging_capacity,
          discharging_capacity, wh_charging, wh_discharging, temperature, cycle_count)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

ADD_N = 10

class BatteryDB():
    def __init__(self):
        config = ConfigParser()
        config.read('db.config')
        host = config.get('client', 'host')
        port = config.getint('client', 'port')
        user = config.get('client', 'user')
        password = config.get('client', 'password')
        database = config.get('client', 'database')

        self.conn = mysql.connector.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database,
                    raise_on_warnings=True
                )

        self.cursor = self.conn.cursor(prepared=True)
        self.cursor_w = self.conn.cursor(prepared=True)
        self.trial_end = []
        self.other_trials = []

    def get_latest_stored(self, test_name):
        self.cursor.execute(LATEST_STORED_QUERY, (test_name,))
        return self.cursor.fetchone()

    def add_record(self, trial_end_dict, others_trials):
        self.trial_end.append(trial_end_dict)
        self.other_trials.extend(others_trials)
        if len(self.trial_end) >= ADD_N:
            try:
                self.cursor_w.executemany(INSERT_TRIAL, self.other_trials)
                self.cursor_w.executemany(INSERT_TRIAL_END, self.trial_end)
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                raise e
            self.trial_end = []
            self.other_trials = []

    def flush_add_record(self):
        pass