from pony.orm import Database, Required, Json

from self_settings import DB_CONFIG

db = Database()
db.bind(**DB_CONFIG)


class UserState(db.Entity):
    """Состояние пользователя внутри сценария."""
    user_id = Required(int, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    pause = Required(bool)
    context = Required(Json)


class Booking(db.Entity):
    """Заявка на регистрацию"""
    town_departure = Required(str)
    town_arrival = Required(str)
    date = Required(str)
    quantity_places = Required(str)
    comment = Required(str)
    telephone = Required(str)


db.generate_mapping(create_tables=True)
