from mysql import connector  # pip install mysql-connector-python
import os


class Database:

    # 1. open connection with class variables for relocation
    @staticmethod
    def __open_connection():
        try:
            db = connector.connect(
                option_files=os.path.abspath(os.path.join(
                    os.path.dirname(__file__), "../config.py")),
                autocommit=False
            )
            if "AttributeError" in(str(type(db))):
                raise Exception("defective database parameters in config")
            cursor = db.cursor(
                dictionary=True, buffered=True)  # lazy loaded
            return db, cursor
        except connector.Error as err:
            if err.errno == connector.errorcode.ER_ACCESS_DENIED_ERROR:
                print("Error: There is no access to the database")
            elif err.errno == connector.errorcode.ER_BAD_DB_ERROR:
                print("Error: Database not found")
            else:
                print(err)
            return

    # 2. Executes READS
    @staticmethod
    def get_rows(sqlQuery, params=None):
        result = None
        db, cursor = Database.__open_connection()
        try:

            cursor.execute(sqlQuery, params)

            result = cursor.fetchall()
            cursor.close()
            if (result is None):
                result = None
                print(ValueError(f"Results are non-existent.[DB Error]"))
            db.close()
        except Exception as error:
            print(error)  # development message
            result = None
        finally:
            return result

    @staticmethod
    def get_one_row(sqlQuery, params=None):
        db, cursor = Database.__open_connection()
        try:
            cursor.execute(sqlQuery, params)
            result = cursor.fetchone()
            cursor.close()
            if (result is None):
                raise ValueError("Results are non-existent.[DB Error]")
        except Exception as error:
            print(error)  # development message
            result = None
        finally:
            db.close()
            return result

    # 3. Executes INSERT, UPDATE, DELETE with PARAMETERS
    @staticmethod
    def execute_sql(sqlQuery, params=None):
        result = None
        db, cursor = Database.__open_connection()
        try:
            cursor.execute(sqlQuery, params)
            db.commit()
            # create confirmed (int of 0)
            result = cursor.lastrowid
            # confirm update, delete (array)
            # result = result if result != 0 else params  # Extra check!!
            if result != 0:  # is an insert, this send the lastrowid back.
                result = result
            else:  # is an update or a delete
                if cursor.rowcount == -1:  # Error is found in SQL
                    raise Exception("Fout in SQL")
                elif cursor.rowcount == 0:  # nothing has changed
                    result = 0
                elif result == "undefined":  # how many rows were changed
                    raise Exception("SQL error")
                else:
                    result = cursor.rowcount
        except connector.Error as error:
            db.rollback()
            result = None
            print(f"Error: Data not saved.{error.msg}")
        finally:
            cursor.close()
            db.close()
            return result
