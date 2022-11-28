
import telegram

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from PyQt5.QtCore import *

telegram_token = '5931508948:AAGcxh_JXNy2XbZTfW-PmSHfXjRD-AxztIw'
telegram_chat_id = 5888866829

bot = telegram.Bot(token=telegram_token)
updater = Updater(token=telegram_token, use_context=True)
dispatcher = updater.dispatcher

class myTelegram(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.token = '5931508948:AAGcxh_JXNy2XbZTfW-PmSHfXjRD-AxztIw'
        self.id = 5888866829
        self.isTelegram = False
        #self.telegramInit()

    def run(self):
        while True:
            pass

    def sendImg(self, img):      #   이미지 전송,
        bot.send_photo(chat_id=telegram_chat_id, photo=open(img, 'rb'))

    def telegramInit(self):
        if self.isTelegram == False:
            self.add_handler('task', self.cmd_task_buttons)
            self.callbsck_handler(self.cb_button)
            self.isTelegram = True

    def cmd_task_buttons(self, update, context):
        task_buttons = [
        [
            InlineKeyboardButton('작업1', callback_data=1), InlineKeyboardButton('작업2', callback_data=2)
        ],
        [
            InlineKeyboardButton('작업3', callback_data=3), InlineKeyboardButton('작업4', callback_data=4)
        ],
        [
            InlineKeyboardButton('종료', callback_data=9)
        ]
        ]

        reply_markup = InlineKeyboardMarkup(task_buttons)

        context.bot.send_message(chat_id=update.message.chat_id, text='작업을 선택해주세요.', reply_markup=reply_markup)

    def cb_button(self, update, context):
        query = update.callback_query
        data = query.data

        context.bot.send_chat_action(chat_id=update.effective_user.id, action=ChatAction.TYPING)

        context.bot.edit_message_text(text='[{}]작업을 완료 하였습니다.'.format(data), chat_id=query.message.chat_id, message_id=query.message.message_id)

    def add_handler(self, cmd, func):
        updater.dispatcher.add_handler(CommandHandler(cmd, func))

    def callbsck_handler(self, func):
        updater.dispatcher.add_handler(CallbackQueryHandler(func))

    def send_message(self, update, context):
        bot.sendMessage(chat_id=telegram_chat_id, text='챗봇 자동응답')





