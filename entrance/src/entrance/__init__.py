import psycopg2 as pg2

from entrance.entrance import Entrance
from entrance.model import EntranceDB, InOutLogsDB
from entrance.db_settings.config import config
from entrance import settings



db_params = config(filename=settings.db_path)

entrance_db = EntranceDB(db_params)
inout_logs = InOutLogsDB(db_params)




