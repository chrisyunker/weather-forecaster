import logging
import os
from app.db import Db

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

DB_NAME = "test.db"

db = Db(DB_NAME)

db.store_temp(1777172400, 75)
db.store_temp(1777172400, 70)
db.store_temp(1777172400, 80)
db.store_temp(1777172400, 76)

# Good test
temps = db.get_temps(1777172400)
print(f"Temps: {temps}")
print()

# Missing epoch test
temps = db.get_temps(1777172401)
print(f"Temps: {temps}")
print()

os.remove(DB_NAME)

