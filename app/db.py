import sqlite3
import logging

class Db:
    def __init__(self, db_name: str):
        self.db_name = db_name
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS temperatures 
                       (epoch INTEGER PRIMARY KEY, low INTEGER, high INTEGER)''')

    def store_temp(self, epoch: int, temperature: int):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Either:
        # 1: Initially store both low and high temps if this is a new epoch
        # 2: Store low temp if lower for epoch
        res = cursor.execute("""
            INSERT INTO temperatures (epoch, low, high)
            VALUES (?, ?, ?)
            ON CONFLICT (epoch)
            DO UPDATE SET
                low = excluded.low
            WHERE excluded.low < low;
         """, (epoch, temperature, temperature))
        conn.commit()
        if res.rowcount > 0:
            logging.info(f"Inserted new low(/high) temp, epoch: {epoch}, temperature: {temperature}")

        # Store high temp if higher for epoch
        res = cursor.execute("""
            UPDATE temperatures
            SET high = ?
            WHERE epoch = ? AND ? > high;
         """, (temperature, epoch, temperature))
        conn.commit()
        if res.rowcount > 0:
            logging.info(f"Inserted new high temp, epoch: {epoch}, temperature: {temperature}")

    def get_temps(self, epoch: int) -> dict | None:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        rows = cursor.execute("SELECT low, high FROM temperatures WHERE epoch = ?", (epoch,))
        res = rows.fetchone()
        if res:
            (low, high) = res
            return {"low": low, "high": high}
        else:
            logging.debug(f"Failed to find temperature for epoch: {epoch}")
            return None

