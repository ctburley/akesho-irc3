import irc3
from random import choice

@irc3.plugin
class Plugin:

	def __init__(self, bot):
		self.bot = bot
		
		self.opts = ('you are welcome',
					'no problem',
					'do not mention it',
					'it is my pleasure',
					'sure thing',
					'of course',
					'happy to help',
					'beep boop')
		
		print("<3 <3 <3 luv ~ LOADE")
	
	@classmethod
	def reload(cls, old):
		return cls(old.bot)

	@irc3.event(r'(?i)^(@\S+ )?:(?P<nick>\S+)!\S+@\S+ privmsg (?P<channel>\S+) :(?:.+? |)(?:t(?:hank(?:s| you)| ?y(?: ?v ?m)?),? akesho)(?P<luv>(?: *<3)*)?(?: +[^$]*)??$')
	def ty(self, nick=None, channel=None, luv=None, **kw):
		if self.bot.obeying_commands(channel):
			self.bot.privmsg(channel, choice(self.opts)+('' if luv is None else ' ' + (' '.join(luv.split()))))
	
	#@command
	#def hug(self, mask, channel, args):
	#	"""Hug someone!
	#		%%hug <someone>...
	#	"""
	#	wraps " + target + " in (2-13) different arms and squeezes until they look like a koosh toy
