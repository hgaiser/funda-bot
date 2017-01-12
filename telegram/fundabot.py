#!/usr/bin/env python

import telegram
import telegram.ext
import logging
import threading
import zmq
import time
import json
import pickle

logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.INFO
)

class FundaBot:
	def __init__(self):
		self.bot        = telegram.Bot(token='TOKEN')
		self.updater    = telegram.ext.Updater(bot=self.bot)
		self.dispatcher = self.updater.dispatcher
		self.chats      = []

		print(self.bot.getMe())

		try:
			self.chats = pickle.load(open("chats.pkl", "rb"))
		except:
			self.chats = []

		try:
			self.houses = pickle.load(open("houses.pkl", "rb"))
		except:
			self.houses = {}

		self.dispatcher.add_handler(telegram.ext.CommandHandler('register', self.register))
		self.dispatcher.add_handler(telegram.ext.CommandHandler('unregister', self.unregister))
		self.dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, self.message))
		logging.info('Initialised FundaBot.')

	def register(self, bot, update):
		id = update.message.chat_id
		if not id in self.chats:
			update.message.reply_text('{}, I am adding you to the list of users.'.format(update.message.from_user.first_name))
		else:
			update.message.reply_text('{}, you are already registered!'.format(update.message.from_user.first_name))
			return

		logging.info('Adding id "{}" to registered users.'.format(id))
		self.chats.append(id)

		pickle.dump(self.chats, open("chats.pkl", "wb"))

	def unregister(self, bot, update):
		id = update.message.chat_id
		if id in self.chats:
			update.message.reply_text('{}, I am removing you from the list of users.'.format(update.message.from_user.first_name))
		else:
			update.message.reply_text('{}, you are not registered yet!'.format(update.message.from_user.first_name))
			return

		logging.info('Removing id "{}" from registered users.'.format(id))
		self.chats.remove(id)

		pickle.dump(self.chats, open("chats.pkl", "wb"))

	def addHouse(self, house):
		self.houses[house['id']] = house
		pickle.dump(self.houses, open("houses.pkl", "wb"))

	def notifyHouse(self, house):
		msg = "[{}]({})\n".format(house['street'], house['link'])
		msg += "Price: *{}*\n".format(house['price'])
		msg += "Living area: *{}m2*".format(house['living-area'])
		for id in self.chats:
			self.bot.sendMessage(chat_id=id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

	def message(self, bot, update):
		if self.bot.getMe()['first_name'].lower() in update.message.text.lower():
			update.message.reply_text("What can I do you for {} ?".format(update.message.from_user.first_name))

	def update_worker(self, port='5555'):
		context = zmq.Context()
		socket = context.socket(zmq.PAIR)
		socket.bind('tcp://*:%s' % port)

		while True:
			msg = socket.recv().decode('utf-8')
			house = json.loads(msg)
			logging.info('Received house {}'.format(house['id']))
			if house['id'] not in self.houses:
				self.addHouse(house)
				self.notifyHouse(house)
			time.sleep(1)

	def run(self):
		logging.info('Running FundaBot.')

		thread = threading.Thread(target=self.update_worker)
		thread.start()

		self.updater.start_polling()
		self.updater.idle()


if __name__ == '__main__':
	bot = FundaBot()
	bot.run()
