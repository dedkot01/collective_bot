import telegram
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from sqlalchemy.orm import Session

from models.achievement import Achievement
from models.transaction import Transaction
from models.user import User
from main import engine


menu_keyboard = ReplyKeyboardMarkup([
    ['📊 Характеристики 📊'],
])

admin_keyboard = ReplyKeyboardMarkup([
    ['Повысить хар-ку'],
    ['Подтвердить достижение'],
])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    with Session(engine) as session:
        user = User.get_or_reg(user_id, session)
        if user.is_admin:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    'Добро пожаловать, товарищ! 😃\n'
                    'Вы администратор системы КОЛЛЕКТИВ 😉\n'
                    'Используйте меню📱\n'
                    'Вы можете отмечать заслуги наших товарищей в достижениях и развитии 📜'
                ),
                reply_markup=admin_keyboard,
            )
        else:
            params = context.args
            if len(params) == 0:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        'Добро пожаловать, товарищ! 😃\n'
                        'Я ваш личный помошник в системе КОЛЛЕКТИВ 😉\n'
                        'Используйте меню📱\n'
                        'Для взаимодействия с КОЛЛЕКТИВОМ потребуется считывать QR коды 📜\n'
                        'Развивай свою силу 💪, ловкость 🤸‍♀️ и знания 📚\n'
                        'Достигай высот во славу всего коллектива! 🎖\n'
                        'УРА, ТОВАРИЩ! 🎉'
                    ),
                    reply_markup=menu_keyboard,
                )
            elif len(params) == 1:
                transaction_id = params[0]
                transaction = Transaction.get(transaction_id, session)
                if transaction is None:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text='❌ ОШИБКА! Код не найден',
                        reply_markup=menu_keyboard,
                    )
                elif transaction.user is not None:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text='❌ ОШИБКА! Код уже был использован',
                        reply_markup=menu_keyboard,
                    )
                else:
                    if transaction.action in ['up_strength', 'up_agility', 'up_knowledge']:
                        if transaction.action == 'up_strength':
                            user.strength += transaction.amount
                            msg_for_user = f'Поздравляем, товарищ! Ваша сила 💪 возросла на {transaction.amount}'
                        elif transaction.action == 'up_agility':
                            user.agility += transaction.amount
                            msg_for_user = f'Поздравляем, товарищ! Ваша ловкость 🤸‍♀️ возросла на {transaction.amount}'
                        elif transaction.action == 'up_knowledge':
                            user.knowledge += transaction.amount
                            msg_for_user = f'Поздравляем, товарищ! Ваши знания 📚 выросли на {transaction.amount}'

                        transaction.user = user.id
                        session.commit()

                        await context.bot.send_message(
                            chat_id=user_id,
                            text=msg_for_user,
                            reply_markup=menu_keyboard,
                        )

                        await context.bot.send_message(
                            chat_id=int(transaction.author),
                            text=f'Пользователь {update.effective_user.first_name} активировал код {transaction.id}',
                        )

                        achievements = Achievement.get_all(session)
                        for achievement in achievements:
                            if (
                                (achievement not in user.knowed_achievements)
                                and (user.strength >= achievement.req_strength)
                                and (user.agility >= achievement.req_agility)
                                and (user.knowledge >= achievement.req_knowledge)
                            ):
                                user.knowed_achievements.append(achievement)
                                session.commit()

                                await context.bot.send_message(
                                    chat_id=user_id,
                                    text=(
                                        f'Товарищ! Вы получаете 📜 талон 📜 <b>"{achievement.description}"</b>\n'
                                        f'Вы можете обменять его в баре на {achievement.award}'
                                    ),
                                    parse_mode=telegram.constants.ParseMode.HTML,
                                    reply_markup=menu_keyboard,
                                )
                    elif transaction.action == 'give_ach':
                        achievement = Achievement.get_by_id(session, id_achievement=transaction.amount)
                        if achievement is None:
                            await context.bot.send_message(
                                chat_id=user_id,
                                text='❌ ОШИБКА СИСТЕМЫ! Такого достижения не существует, обратитесь к администратору Коллектива',
                                reply_markup=menu_keyboard,
                            )
                        elif achievement in user.achievements:
                            await context.bot.send_message(
                                chat_id=user_id,
                                text='❌ ОШИБКА! Ранее вы уже получали данное достижение',
                                reply_markup=menu_keyboard,
                            )
                        elif (
                            (user.strength < achievement.req_strength)
                            or (user.agility < achievement.req_agility)
                            or (user.knowledge < achievement.req_knowledge)
                        ):
                            await context.bot.send_message(
                                chat_id=user_id,
                                text=(
                                    '❌ ОШИБКА! Ваших характеристик недостаточно для данного достижение\n'
                                    f'\nТребуется {achievement.req_strength} силы 💪, {achievement.req_agility} ловкости 🤸‍♀️'
                                    f' и {achievement.req_knowledge} знания 📚'
                                    f'\nУ вас {user.strength} силы, {user.agility} ловкости и {user.knowledge} знания'
                                ),
                                reply_markup=menu_keyboard,
                            )
                        else:
                            user.achievements.append(achievement)
                            transaction.user = user.id
                            session.commit()

                            await context.bot.send_message(
                                chat_id=int(transaction.author),
                                text=(
                                    f'Пользователь {update.effective_user.first_name} активировал код {transaction.id}'
                                    f'\n⭐️ Ему полагается награда: {achievement.award}'
                                ),
                            )

                            await context.bot.send_message(
                                chat_id=user_id,
                                text=f'⭐️ Получите вашу награду, товарищ!\n{achievement.award}',
                                reply_markup=menu_keyboard,
                            )


async def characteristics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with Session(engine) as session:
        user: User = User.get_or_reg(update.effective_chat.id, session)
        session.commit()

        if not user.is_admin:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f'Сила 💪: {user.strength}\n'
                    f'Ловкость 🤸‍♀️: {user.agility}\n'
                    f'Знания 📚: {user.knowledge}\n'
                ),
                reply_markup=menu_keyboard,
            )


start_handler = CommandHandler('start', start)
characteristics_handler = MessageHandler(filters.Text('📊 Характеристики 📊'), characteristics)
