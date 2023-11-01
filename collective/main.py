import logging

from telegram.ext import ApplicationBuilder

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import config as conf
from models import Base
from models.achievement import Achievement

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

engine = create_engine(conf.db_str if conf.db_str is not None else conf.db_conn)

if __name__ == '__main__':
    from handlers import admin, menu

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        if len(Achievement.get_all(session)) == 0:
            a1 = Achievement(1, 'Номер 1', 'Стакан лимонада Буратино / кваса / кисель', 1, 1, 1)
            a2 = Achievement(2, 'Самый сильный', 'Жвачка или гематоген', 3, 0, 0)
            a3 = Achievement(3, 'Самый ловкий', 'Жвачка или гематоген', 0, 3, 0)
            a4 = Achievement(4, 'Самый умный', 'Жвачка или гематоген', 0, 0, 3)
            a5 = Achievement(5, 'Мастер спорта', 'Забугорный напиток (кофе) или бесплатный час', 4, 5, 0)
            a6 = Achievement(6, 'Секретарь', 'Забугорный напиток (кофе) или бесплатный час', 0, 5, 5)
            a7 = Achievement(7, 'Комсомолец', 'Бесплатный день или флаер на компанию ', 6, 6, 6)
            a8 = Achievement(8, 'Гордость партии', 'Бесплатная неделя', 10, 10, 10)

            session.add(a1)
            session.add(a2)
            session.add(a3)
            session.add(a4)
            session.add(a5)
            session.add(a6)
            session.add(a7)
            session.add(a8)
            session.commit()

    application = ApplicationBuilder().token(conf.token).build()

    application.add_handler(menu.start_handler)

    application.add_handler(menu.characteristics_handler)

    application.add_handler(admin.request_admin_role_handler)
    application.add_handler(admin.accept_request_admin_role_handler)
    application.add_handler(admin.up_characteristic_handler)
    application.add_handler(admin.give_achievement_handler)

    application.run_polling()
