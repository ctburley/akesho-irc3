import irc3, shelve, random, os
from irc3.plugins.command import command

@irc3.plugin
class Plugin:

	def __init__(self, bot):
		self.bot = bot
		if (os.path.isfile('friends')):
			print("friends file found.")

	@classmethod
	def reload(cls, old):
		return cls(old.bot)
	
	def get_record(self, nick):
		with shelve.open('friends') as fr:
			if nick in fr:
				return fr[nick]
		return None
	
	def set_record(self, nick, record):
		if record is not None:
			with shelve.open('friends') as fr:
				fr[nick] = record
	
	@irc3.event('^(@(?P<tags>\S+) )?:(?P<nick>\S+)(?P<mask>!\S+@\S+) PRIVMSG (?P<channel>\S+) :\.befs$')
	def befs(self, nick=None, mask=None, channel=None, **kw):
#		if channel == '#trees':
#		    return
		if self.bot.obeying_commands(channel):
			rec = self.get_record(nick)
			if rec is not None:
				if channel in rec:
					del rec[channel]['  total  ']
					for item in rec[channel]:
						rec[channel][self.bot.np(item)] = rec[channel][item]
						del rec[channel][item]
					friended = ": " + ', '.join(rec[channel])
					self.bot.privmsg(channel, nick+" you have "+str(len(rec[channel]))+" friends in this channel"+friended)
				else:
					self.bot.privmsg(channel, "I'm so sorry...")
			else:
				self.bot.privmsg(channel, "Oh... you poor thing...")
		
	
	@irc3.event('^(@(?P<tags>\S+) )?:(?P<nick>\S+)(?P<mask>!\S+@\S+) PRIVMSG (?P<channel>\S+) :\.bef\s+(?P<target>\S+)\s*$')
	def bef(self, nick=None, mask=None, channel=None, target=None, **kw):
#		if channel == '#trees':
#		    return
		if self.bot.obeying_commands(channel):
			target = target.strip()
			if target in self.bot.channels[channel]:
				rec = self.get_record(nick)
				if rec is None:
					print ('no record')
					rec = {channel:{target:1, '  total  ':1}}
				else:
					if channel not in rec:
						rec[channel] = {target:1, '  total  ':1}
					else:
						if target not in rec[channel]:
							rec[channel][target] = 1
							rec[channel]['  total  '] += 1
						else:
							rec[channel][target] += 1
							rec[channel]['  total  '] += 1
				self.set_record(nick, rec)
				self.bot.privmsg(channel, nick + " you befriended a "+target+" in "+str(random.choice(range(2,14)))+" seconds! You have befriended someone "+str(rec[channel]['  total  '])+" times in this channel.")
				
