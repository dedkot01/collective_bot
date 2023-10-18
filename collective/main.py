import logging

from telegram.ext import ApplicationBuilder

from sqlalchemy import create_engine

import config as conf
from models import Base

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

engine = create_engine(conf.db_str if conf.db_str is not None else conf.db_conn)

if __name__ == '__main__':
    from handlers import admin, menu

    Base.metadata.create_all(engine)

    application = ApplicationBuilder().token(conf.token).build()

    application.add_handler(menu.start_handler)

    application.add_handler(menu.characteristics_handler)
    application.add_handler(menu.achievements_handler)

    application.add_handler(admin.request_admin_role_handler)
    application.add_handler(admin.accept_request_admin_role_handler)
    application.add_handler(admin.up_characteristic_handler)

    application.run_polling()
