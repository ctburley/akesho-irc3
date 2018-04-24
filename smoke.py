import math
import time
import irc3
from random import randint
from threading import Timer
from irc3.plugins.command import command

@irc3.plugin
class Plugin:

	def __init__(self, bot):
		self.bot = bot
		self.smokers = {}
		self.wait = {} # 
		print("SMOKE ~ loaded 420 blaze it")

	def reset(self, channel):
		if self.smoking(channel):
			del self.wait[channel]
			del self.smokers[channel]

	def smoking(self, channel):
		return channel in self.smokers

	def in_cooldown(self, channel):
		if self.smoking(channel):
			if self.wait[channel] > 2:
				return True
		return False
		
	@command
	def toke(self, mask, channel, args):
		"""Emulates treesbot's !toke command
			
			%%toke
		"""
		self.sendMessage(channel, "420 Hit It!")

	@command
	def iwish(self, mask, channel, args):
		"""Get a virtual bowl loaded for you so you can join the round.
			
			%%iwish
		"""
		self.sendAction(channel, "packs a bowl for " + mask.nick)
		self.smokers[channel].extend(['carl','mike','tonya','sasha','patricia','tony','daryl'])

	@command
	def wait(self, mask, channel, args):
		"""Gives you another 30 seconds, works only once while in a round.
			
			%%wait
		"""
		# Is there a round
		if self.smoking(channel):
			# Round exists, but, have we already waited or hit ten seconds
			if self.wait[channel] > 0:
				# Already waited, or we have reached the ten second warning
				self.sendMessage(channel, "We have waited long enough, there is always next round!")
				return
			
			# We can delay this round
			self.wait[channel] = 1
			self.sendMessage(channel, "Hold up, " + mask.nick + " needs another 30 seconds.")
			return
		
	
	@command
	def ambush(self, mask, channel, args):
		"""Start the countdown early.
			
			%%ambush
		"""
		if self.smoking(channel):
			if self.in_cooldown(channel):
				self.sendMessage(channel, "Last round was less than two minutes ago, go ahead and hit it!")
				return
			else:
				if mask.nick not in self.smokers[channel]:
					self.smokers[channel].append(mask.nick)
				self.sendMessage(channel, mask.nick + " started the countdown early, grab your piece!")
		else:
			self.smokers[channel] = [mask.nick]
			self.wait[channel] = 0
			self.sendMessage(channel, mask.nick + " is ambushing the channel! Does that piece have a hit left?")
		
		self.countdown(channel)


	def countdown(self, channel):
		if (self.in_cooldown(channel)):
			return
		
		# Do the countdown
		time.sleep(1)
		self.sendMessage(channel, "2..")
		time.sleep(1)
		self.sendMessage(channel, "1..")
		time.sleep(1)
		self.sendMessage(channel, "Fire in the bowl!")
	
		self.wait[channel] = 3
		self.bot.goTime(120, self.reset, channel)

	@command
	def whosin(self, mask, channel, args):
		"""Check who is already in the round
			
			%%whosin
		"""
		reply = "Nobody yet, what about you?"
		if self.smoking(channel):
			reply = "The round was started by " + self.smokers[channel][0] + "."
			if len(self.smokers[channel]) == 2:
				reply += " Also smoking is " + self.smokers[channel][1] + "."
			if len(self.smokers[channel]) > 2:
				reply += " Also smoking are "
				reply += ', '.join(self.smokers[channel][1:-1])
				reply += ', and '
				reply += self.smokers[channel][-1] +"."
		self.sendMessage(channel, reply)


	@command(show_in_help_list=False)
	def i(self, mask, channel, args):
		"""Join the round, optional arguments allow you to use the command in the beginning of a sentence.
			
			%%i [<optional>...]
		"""
		self.imin(mask, channel, args)
		
	@command
	def imin(self, mask, channel, args):
		"""Join the round, optional arguments allow you to use the command in the beginning of a sentence.
			
			%%imin [<optional>...]
		"""
		if (self.smoking(channel)):
			if self.in_cooldown(channel):
				self.sendMessage(channel, "Last round was less than two minutes ago, go ahead and hit it!")
				return
			if mask.nick in self.smokers[channel]:
				self.sendMessage(channel, "You are already in!")
			else:
				self.smokers[channel].append(mask.nick)
				self.sendMessage(channel, mask.nick + " is in!")
		else:
			# Round has not begun, start it
			self.getin(mask, channel, args)


	def warn10Second(self, channel):
		if self.smoking(channel):
			if self.in_cooldown(channel):
				return
			
			if self.wait[channel] == 1:
				self.wait[channel] = 2
				self.bot.goTime(30, self.warn20Second, channel)
				return
	
			# Warn the channel
			self.sendMessage(channel, "Ten seconds, grab your lighter.")
		
			self.wait[channel] = 2
			self.bot.goTime(7, self.countdown, channel)

	def warn20Second(self, channel):
		if self.smoking(channel):
			if self.in_cooldown(channel):
				return
			
			if self.wait[channel] == 1:
				self.wait[channel] = 2
				self.bot.goTime(30, self.warn20Second, channel)
				return
			self.sendMessage(channel, "Twenty seconds, is that bowl packed yet?");
	
			self.bot.goTime(10, self.warn10Second, channel)


	@command
	def getin(self, mask, channel, args):
		"""Start a round. 
			
			%%getin
		"""# Is the round already started?
		if (self.smoking(channel)):
			if self.in_cooldown(channel):
				self.sendMessage(channel, "Last round was less than two minutes ago, go ahead and hit it!")
			else:
				if mask.nick not in self.smokers[channel]:
					self.imin(mask, channel, args)
			return
		
		# Initialize the round information
		self.smokers[channel] = [mask.nick]
		self.wait[channel] = 0
		
		# Inform the channel the round has begun
		self.sendMessage(channel, mask.nick + " is ready to burn one, who else is in?")
	
		# Start the four minute timer
		self.bot.goTime(4*60, self.warn20Second, channel)
		
	def sendMessage(self, channel, text):
		print('smoke~~~ ' + text)
		self.bot.privmsg(channel, text, True)

	def sendAction(self, channel, text):
		self.sendMessage(channel, "\x01ACTION " + text + "\x01")

