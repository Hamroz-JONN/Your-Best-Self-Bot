#!/usr/bin/env python

import datetime

import requests
from bs4 import BeautifulSoup as BS

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, User
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler

import urllib.parse
import sqlite3

RUNNING_LOCAL = False

TOKEN = "yourBotTokenHere"
DB_TABLE_PATH = '/Users/anton/Desktop/my best self bot/database.db' if RUNNING_LOCAL else '/computer-online-server/yourbestself_bot/database2.db'

superusers = [123234425] # telegram ids of superusers (developers)
moderators = [12345356] + superusers # telegram ids of moderators (people monitoring goals)

all_goal_types = {'Жим, Турник, шишту хез':'Mashk1', 
                  'Рохгарди, дав, йога':'Mashk2', 
                  'Футбол, Воллейбол, Теннис':'Mashk3', 
                  'Дилхох машки дустдошта':'Mashk4',
                  'Китобхони, Подкаст гуш кардан':'Intel1',
                  'Забономузӣ':'Intel2',
                  'Нақшаи ҳарруза/ҳафтаина/моҳона/солона':'Intel3',
                  'Мантиқ ва нигоҳи назари танқидӣ':'Intel4',
                  'Фарҳанги идоравӣ':'Social1',
                  'Театр, кино, тарабхона':'Social2',
                  'Риояи қонуни ҶМ':'Social3',
                  'Зиракии сиёсӣ':'Social4',
                  'Камхурӣ':'Spirit1',
                  'Тозагии муҳити зист':'Spirit2',
                  'Хоксорӣ ва хушмуомилагӣ':'Spirit3',
                  'Дигар арзишҳо':'Spirit4',
}

mod_keyboard = [
    ['Натичаҳо']
]

menu_keyboard = [
    ['Ҷисмонӣ', 'Интеллектуалӣ'],
    ['Арзишӣ', 'Сотсиалӣ'],
    ['Натичаҳо']
]

phy_keyboard = [['Жим, Турник, шишту хез', 'Рохгарди, дав, йога'],
                ['Футбол, Воллейбол, Теннис', 'Дилхох машки дустдошта'],
                ]
intel_keyboard = [['Китобхони, Подкаст гуш кардан', 'Забономузӣ'],
                ['Нақшаи ҳарруза/ҳафтаина/моҳона/солона', 'Мантиқ ва нигоҳи назари танқидӣ'],
                ]
social_keyboard = [['Фарҳанги идоравӣ', 'Театр, кино, тарабхона'],
                ['Риояи қонуни ҶМ', 'Зиракии сиёсӣ'],
                ]
spirit_keyboard = [['Камхурӣ', 'Тозагии муҳити зист'],
                ['Хоксорӣ ва хушмуомилагӣ', 'Дигар арзишҳо'],
                ]

def isLegal(update:Update, context:ContextTypes.DEFAULT_TYPE):
    return not update.message.chat.type.__contains__('group')

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
        for idx, value in enumerate(row))

async def alter_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args == None or context.args.__len__() != 2 or update.message.from_user.id not in moderators:
        return
    id = int(context.args[0])
    goal = context.args[1]
    goal = all_goal_types[goal]

    conn = sqlite3.connect(f'{DB_TABLE_PATH}')
    curs=conn.cursor()
    
    if update.message.text.__contains__('undone'):
        curs.execute(f"update goals set {goal} = 1 where id = {id};")
    elif update.message.text.__contains__('done'):
        curs.execute(f"update goals set {goal} = 2 where id = {id};")
    elif update.message.text.__contains__('del'):
        curs.execute(f"update goals set {goal} = 0 where id = {id};")
    conn.commit()

    await update.message.reply_text("Статус цели обновлен!")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not isLegal(update, context):
        return
    
    user_id = update.message.from_user.id

    full_name = update.message.from_user.full_name

    conn = sqlite3.connect(f'{DB_TABLE_PATH}')
    curs=conn.cursor()
    curs.execute(f"select exists(select 1 from goals where id = {user_id});") 
    (isin, ) = curs.fetchone()
    if (not isin):
        curs.execute(f"INSERT OR IGNORE INTO goals values({user_id}, 0, 0, 0, 0, '{full_name}', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)")
        conn.commit() 

    if user_id in moderators and 0:
        await update.message.reply_text("Добро пожаловать, модератор...", reply_markup=ReplyKeyboardMarkup(mod_keyboard))
    else:
        await update.message.reply_text("Добро пожаловать, пожалуйста, поставьте себе цель с помощью кнопок ниже...", reply_markup=ReplyKeyboardMarkup(menu_keyboard))

async def goal_menu_physical(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not isLegal(update, context):
        return
    await update.message.reply_text("Выберите одно из физических упражнений, приведенных ниже, в качестве своей цели. Если хотите отправить прогресс, выберите для какого упражнения.", reply_markup=ReplyKeyboardMarkup(phy_keyboard))

async def goal_menu_intel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not isLegal(update, context):
        return
    await update.message.reply_text("Выберите одно из приведенных ниже интеллектуальных упражнений в качестве своей цели. Если хотите отправить прогресс, выберите для какого упражнения.", reply_markup=ReplyKeyboardMarkup(intel_keyboard))

async def goal_menu_spirit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not isLegal(update, context):
        return
    await update.message.reply_text("Выберите одно из приведенных ниже духовных упражнений в качестве своей цели. Если хотите отправить прогресс, выберите для какого упражнения.", reply_markup=ReplyKeyboardMarkup(spirit_keyboard))

async def goal_menu_social(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not isLegal(update, context):
        return
    await update.message.reply_text("Выберите одно из приведенных ниже социальных упражнений в качестве своей цели. Если хотите отправить прогресс, выберите для какого упражнения.", reply_markup=ReplyKeyboardMarkup(social_keyboard))

async def set_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not isLegal(update, context):
        return
    raw_goal = update.message.text
    user_id = update.message.from_user.id

    if raw_goal not in all_goal_types:
        await update.message.reply_text('Инхел машк нест', reply_markup=ReplyKeyboardMarkup(menu_keyboard))
        return
    goal = all_goal_types[raw_goal]

    print(raw_goal, '->' , goal)
        
    conn = sqlite3.connect(f'{DB_TABLE_PATH}')
    curs=conn.cursor()

    # 0 -> havent set the goal
    # 1 -> progressing towards the goal
    # 2 -> completed the goal
    curs.execute(f"select {goal} from goals where id = {user_id}")
    (status,) = curs.fetchone()
    if status == 1:
        context.user_data['submitting-goal'] = goal
        await update.message.reply_text(f'Пришлите фотографию своего продвижения к цели: {raw_goal}', reply_markup=ReplyKeyboardRemove())
        return
    elif status == 2:
        await update.message.reply_text(f'Вы уже достигли этой цели!')
        return
    
    curs.execute(f"update goals set {goal} = 1 where id = {user_id};")
    conn.commit() 
    await update.message.reply_text('Ваша цель принята!', reply_markup=ReplyKeyboardMarkup(menu_keyboard))

async def results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not isLegal(update, context):
        return
    user_id = update.message.from_user.id
    is_mod = user_id in moderators

    conn = sqlite3.connect(f'{DB_TABLE_PATH}')
    conn.row_factory = make_dicts
    curs=conn.cursor()
    curs.execute(f"select * from goals;")
    all_goals=curs.fetchall()

    resp = "Results\n\n"

    for usr in all_goals:
        # username = await context.bot.getChatMember(update.message.chat_id, usr['id'])
        # username = username.user.username
        curs.execute(f"select full_name from goals where id = {usr['id']}")
        username = curs.fetchone()
        username = username['full_name']

        resp += f"{username}"
        resp += f" ({usr['id']})\n" if is_mod else '\n'

        for tj_act, act in all_goal_types.items():
            curs.execute(f"select {act} from goals where id = {usr['id']}")
            stat = curs.fetchone()
            stat = stat[act]
            if stat == 1:
                resp += f"  🔘{tj_act}\n"
            elif stat == 2:
                resp += f"  ✅{tj_act}\n"
        resp +=  "\n"

    await update.message.reply_text(resp)

async def accept_goal_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not isLegal(update, context):
        return
    
    conn = sqlite3.connect(f'{DB_TABLE_PATH}') 
    curs=conn.cursor()

    user_id = update.message.from_user.id
    curs.execute(f"select full_name from goals where id = {user_id}")
    (username,) = curs.fetchone()
    photos = update.message.photo

    if not photos:
        await update.message.reply_text("Фото не найдено", reply_markup=ReplyKeyboardMarkup(menu_keyboard))
        return 
    if 'submitting-goal' not in context.user_data:
        await update.message.reply_text("Выберите цель для которого вы хотите отправить свой прогресс", reply_markup=ReplyKeyboardMarkup(menu_keyboard))
        return 
        
    largest_photo = photos[-1]
    file_id = largest_photo.file_id

    for mod_id in moderators:
        await context.bot.send_photo(chat_id=mod_id, photo=file_id,
            caption=f"{username} продвинулся к своей цели: {context.user_data['submitting-goal']}"
        )
    context.user_data.clear()
    await update.message.reply_text("Фотография отправлена! Наши модераторы рассматривают ее!", reply_markup=ReplyKeyboardMarkup(menu_keyboard))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not isLegal(update, context):
        return

    txt = update.message.text

    if txt in all_goal_types.keys():
        return await set_goal(update, context)

    print("Unhandled:", txt)
    pass

async def __test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("qwerty")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"{update}\nSays: {context.error}\n")

if __name__ == "__main__":
    print("✅Bot started...✅")

    conn = sqlite3.connect(f'{DB_TABLE_PATH}')
    curs=conn.cursor()

    app = Application.builder().token(TOKEN).build()

    # Admin Commands
    app.add_handler(CommandHandler('start', start_command))

    app.add_handler(CommandHandler('del', alter_goal, has_args=True))
    app.add_handler(CommandHandler('done', alter_goal, has_args=True))
    app.add_handler(CommandHandler('undone', alter_goal, has_args=True))

    app.add_handler(MessageHandler(filters.Regex('Ҷисмонӣ'), goal_menu_physical))
    app.add_handler(MessageHandler(filters.Regex('Интеллектуалӣ'), goal_menu_intel))
    app.add_handler(MessageHandler(filters.Regex('Арзишӣ'), goal_menu_spirit))
    app.add_handler(MessageHandler(filters.Regex('Сотсиалӣ'), goal_menu_social))
    app.add_handler(MessageHandler(filters.Regex('Натичаҳо'), results))

    app.add_handler(MessageHandler(filters.PHOTO, accept_goal_photo))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    app.add_error_handler(error_handler)

    app.run_polling(5)