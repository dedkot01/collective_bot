from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import filters
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler

from sqlalchemy.orm import Session

from config import super_admin_id
from models.transaction import Transaction
from models.user import User
from handlers.menu import admin_keyboard
from main import engine
from util import gen_qr_file


CHARACTERISTIC = range(1)

characteristic_keyboard = ReplyKeyboardMarkup([
    ['Сила'],
    ['Ловкость'],
    ['Знание'],
    ['/cancel'],
])


async def request_admin_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id

    request_admin_role_inkeyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Принять', callback_data=user_id),
        ],
    ])

    await context.bot.send_message(
        chat_id=super_admin_id,
        text=f'Пользователь {user_id} запросил права админа',
        reply_markup=request_admin_role_inkeyboard,
    )

    await context.bot.send_message(
        chat_id=user_id,
        text=f'Ваш id - {user_id}.\nПокажите Магистру.',
    )


async def accept_request_admin_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id == super_admin_id:
        query = update.callback_query
        user_id = int(query.data)

        with Session(engine) as session:
            user = User.get_or_reg(user_id, session)
            user.is_admin = True

            session.add(user)
            session.commit()

        await query.answer()

        await query.edit_message_text(text=f"Пользователь {user_id} стал админом")

        await context.bot.send_message(
            chat_id=user_id,
            text='Поздравляем! Вы теперь админ ;)',
            reply_markup=admin_keyboard,
        )


async def choose_characteristic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    with Session(engine) as session:
        user = User.get_or_reg(user_id, session)
        if user.is_admin:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Какую характеристику повысить?',
                reply_markup=characteristic_keyboard,
            )

            return CHARACTERISTIC


async def up_characteristic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    characteristic: str = update.message.text.lower()

    if characteristic in {'сила', 'ловкость', 'знание'}:
        with Session(engine) as session:
            if characteristic == 'сила':
                action = 'up_strength'
            elif characteristic == 'ловкость':
                action = 'up_agility'
            elif characteristic == 'знание':
                action = 'up_knowledge'

            transaction = Transaction(
                action=action,
                amount=1,
                author=str(update.effective_chat.id),
            )
            session.add(transaction)
            session.commit()
            session.refresh(transaction)

        qr_path = gen_qr_file(f't.me/collective_wings_bot?start={transaction.id}')

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=qr_path,
            caption=f'Транзакция повышения характеристики "{characteristic.upper()}": {transaction.amount}',
            reply_markup=admin_keyboard,
        )

        qr_path.unlink(True)

        return ConversationHandler.END
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Ожидается одна из указанных характеристик: Сила, Ловкость или Знание',
            reply_markup=characteristic_keyboard,
        )

        return CHARACTERISTIC


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Главное меню',
        reply_markup=admin_keyboard,
    )

    return ConversationHandler.END


request_admin_role_handler = MessageHandler(filters.Text('Админ'), request_admin_role)
accept_request_admin_role_handler = CallbackQueryHandler(accept_request_admin_role)

up_characteristic_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Text('Повысить хар-ку'), choose_characteristic)],
    states={
        CHARACTERISTIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, up_characteristic)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
