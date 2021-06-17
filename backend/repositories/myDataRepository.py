# pylint: skip-file
from .myDatabase import Database
from datetime import date, timedelta,datetime

today = date.today()
tomorrow = date.today() + timedelta(1)
week = date.today() - timedelta(7)
month = date.today() - timedelta(30)
year = date.today() - timedelta(365)


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            data = request.get_json()
        else:
            data = request.form.to_dict()
        return data

    #add different functions here to access your databases
    @staticmethod
    def read_measure():
        sql = "SELECT quantity,measure_time,action,device,Description,majority FROM tbl_measure m LEFT JOIN tbl_devices d ON d.IDdevice = m.device_id ORDER BY measure_time DESC"
        return Database.get_rows(sql)

    @staticmethod
    def read_history():
        sql = "SELECT quantity,measure_time FROM tbl_measure WHERE device_id = 1 AND action = 'REMOVE' ORDER BY measure_time"
        return Database.get_rows(sql)

    @staticmethod
    def read_history_day():
        sql = "SELECT sum(quantity) as `quantity`,count(measure_time) as `number` ,measure_time FROM tbl_measure WHERE device_id = 1 AND action = 'REMOVE' AND measure_time between %s and %s GROUP BY concat(hour(measure_time),minute(measure_time))"
        params = [today, tomorrow]
        #print(Database.get_rows(sql, params))
        return Database.get_rows(sql, params)

    @staticmethod
    def read_history_week():
        sql = "SELECT sum(quantity) as `quantity`,measure_time FROM tbl_measure WHERE device_id = 1 AND action = 'REMOVE' AND measure_time BETWEEN %s AND %s GROUP BY CAST(measure_time AS DATE) ORDER BY measure_time"
        params = [week, tomorrow]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_history_month():
        sql = "SELECT sum(quantity) as `quantity`,measure_time,month(measure_time) as `month` FROM tbl_measure WHERE device_id = 1 AND action = 'REMOVE' AND measure_time BETWEEN %s AND %s GROUP BY month(measure_time) ORDER BY measure_time"
        params = [month, tomorrow]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_history_year():
        sql = "SELECT sum(quantity) as `quantity`,measure_time, year(measure_time) as `year` FROM tbl_measure WHERE device_id = 1 AND action = 'REMOVE' AND measure_time BETWEEN %s AND %s GROUP BY year(measure_time) ORDER BY measure_time"
        params = [year, tomorrow]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_history_date(time):
        sql = "SELECT sum(quantity) as `quantity`,count(measure_time) as `number` ,measure_time FROM tbl_measure WHERE device_id = 1 AND action = 'REMOVE' AND measure_time between %s and %s GROUP BY concat(hour(measure_time),minute(measure_time))"  
        params = [time, (datetime.strptime(time,"%Y-%m-%d")+timedelta(1))]
        #print(Database.get_rows(sql, params))
        return Database.get_rows(sql, params)

    @staticmethod
    def read_fillhistory_day():
        sql = "SELECT quantity,measure_time,majority FROM tbl_measure m LEFT JOIN tbl_devices d ON d.IDdevice = m.device_id WHERE device_id = 1 AND action = 'ADD' AND measure_time between %s and %s ORDER BY measure_time DESC"
        params = [week, tomorrow]

        return Database.get_rows(sql, params)

        
        

    @staticmethod
    def read_feed_average(days):
        sql = "SELECT avg(tbl_measure_by_day.sum_quantity_day) as `avg_quantity_day` FROM(SELECT sum(quantity) as `sum_quantity_day`, cast(measure_time as date) as `measure_time` FROM tbl_measure WHERE device_id = 1 AND action = 'REMOVE' GROUP BY CAST(measure_time AS DATE)) as tbl_measure_by_day"

        return Database.get_one_row(sql)

    @staticmethod
    def read_feed_count_today(days):
        sql = "select count(count_eats) as 'count_eats' from (SELECT count(IDmeasure) as 'count_eats',device_id,measure_time FROM `tbl_measure` where action = 'remove' and day(measure_time)= day(now()) group by concat(hour(measure_time),minute(measure_time))) as tabel group by device_id"

        return Database.get_one_row(sql)

    @staticmethod
    def read_feed_today():
        sql = "SELECT sum(quantity) as 'sum_quantity',device_id,measure_time FROM `tbl_measure` where action = 'remove' and day(measure_time)= day(now()) group by day(measure_time)"

        return Database.get_one_row(sql)

    @staticmethod
    def read_changes():
        sql = "SELECT daily_goal, daily_range, storage, time FROM tbl_settings ORDER BY time DESC"

        return Database.get_rows(sql)

    @staticmethod
    def add_quantity(quantity):
        sql = "INSERT INTO tbl_measure (device_id,quantity,action) VALUES (%s,%s,%s)"
        params = [1, quantity,"ADD"]
        return Database.execute_sql(sql, params)

    @staticmethod
    def add_eaten(quantity):
        sql = "INSERT INTO tbl_measure (device_id,quantity,action) VALUES (%s,%s,%s)"
        params = [1, quantity,"REMOVE"]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_settings(daily_goal, daily_range,storage):
        sql = "UPDATE tbl_settings SET daily_goal = %s, daily_range = %s, storage = %s WHERE IDsettings = (select * from (select idsettings from tbl_settings order by idsettings desc limit 1) as T)"
        params = [daily_goal, daily_range,storage]
        return Database.execute_sql(sql, params)

    @staticmethod
    def read_settings():
        sql = "SELECT daily_goal, daily_range, storage, appname, time FROM tbl_settings WHERE IDsettings = (select idsettings from tbl_settings order by idsettings desc limit 1) ORDER BY time ASC LIMIT 10"

        return Database.get_one_row(sql)

    @staticmethod
    def ldr_read(quantity):
        sql = "INSERT INTO tbl_measure (device_id,quantity,action) VALUES (%s,%s,%s)"
        params = [4, quantity, "CHECK"]
        return Database.execute_sql(sql, params)

    @staticmethod
    def servo_on():
        sql = "INSERT INTO tbl_measure (device_id,quantity,action) VALUES (%s,%s,%s)"
        params = [5, 0, "ON"]
        return Database.execute_sql(sql, params)

    @staticmethod
    def servo_off():
        sql = "INSERT INTO tbl_measure (device_id,quantity,action) VALUES (%s,%s,%s)"
        params = [5, 0, "OFF"]
        return Database.execute_sql(sql, params)

    @staticmethod
    def storage_change(quantity):
        sql = "UPDATE tbl_settings set storage = storage - %s WHERE IDsettings = (select * from (select idsettings from tbl_settings order by idsettings desc limit 1) as T)"
        params = [quantity]
        return Database.execute_sql(sql, params)


