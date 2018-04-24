import irc3, shelve
from irc3.plugins.command import command

@irc3.plugin
class Plugin:

	def __init__(self, bot):
		self.bot = bot
		print("JOT ~ LOADED")
			
	@classmethod
	def reload(cls, old):
		return cls(old.bot)
	
	@irc3.event('^(@(?P<tags>\S+) )?:(?P<nick>\S+)(?P<mask>!\S+@\S+) PRIVMSG (?P<target>\S+) :;\+(?P<key>[\w\s]+?)\s+(?P<verb>is|are|=)\s+(?P<data>\S+.*)$')
	def jot_plus(self, nick=None, target=None, mask=None, key=None, verb=None, data=None, **kw):
		if (self.bot.obeying_commands(target)):
			with shelve.open('jot.shelf') as jot:
				if (key.lower() not in jot):
					print("JOT~~~ +[" + nick + "] " + key + " " + verb + " " + data)
					jot[key.lower()] = {'key':key, 'from':nick, 'verb':verb, 'value':data}
					self.bot.privmsg(nick, 'Ok.')
				else:
					self.bot.privmsg(nick, "The key '"+key+"' already exists.")
			
	@irc3.event('^(@(?P<tags>\S+) )?:(?P<nick>\S+)(?P<mask>!\S+@\S+) PRIVMSG (?P<target>\S+) :;(?P<key>[\w\s]+?)\s*$')
	def jot_get(self, nick=None, mask=None, target=None, key=None, **kw):
		if (self.bot.obeying_commands(target)):
			with shelve.open('jot.shelf') as jot:
				key = key.lower()
				if (key in jot):
					print("JOT~~~ [" + nick + "] " + jot[key]['key'] + " " + jot[key]['verb'] + " " + jot[key]['value'])
					if (jot[key.lower()]['verb'] == '='):
						self.bot.privmsg(target, nick + ": " + jot[key]['value'])
					else:
						return self.bot.privmsg(target, nick + ": " + jot[key]['key'] + " " + jot[key]['verb'] + " " + jot[key]['value'])
	
	@irc3.event('^(@(?P<tags>\S+) )?:(?P<nick>\S+)(?P<mask>!\S+@\S+) PRIVMSG (?P<target>\S+) :;(?P<key>[\w\s]+?)\s*@\s*(?P<audience>[^,]+)\s*$')
	def jot_tell(self, nick=None, mask=None, target=None, audience=None, key=None, **kw):
		if (self.bot.obeying_commands(target)):
			with shelve.open('jot.shelf') as jot:
				key = key.lower()
				if (key in jot):
					print("JOT~~~ [" + nick + "] " + jot[key]['key'] + " " + jot[key]['verb'] + " " + jot[key]['value'])
					if (jot[key.lower()]['verb'] == '='):
						self.bot.privmsg(target, audience.strip() + ": " + jot[key]['value'])
					else:
						return self.bot.privmsg(target, audience + ": " + jot[key]['key'] + " " + jot[key]['verb'] + " " + jot[key]['value'])
	
	@irc3.event('^(@(?P<tags>\S+) )?:(?P<nick>\S+)(?P<mask>!\S+@\S+) PRIVMSG (?P<target>\S+) :;\?(?P<key>[\w\s]+?)\s*$')
	def jot_search(self, nick=None, mask=None, target=None, key=None, **kw):
		if (self.bot.obeying_commands(target)):
			with shelve.open('jot.shelf') as jot:
				print ("JOTSEARCH~~~ +[" + nick + "] " + key)
				result = "Results"
				count = 0
				for k in jot:
					if ((key.lower() in k) or (key.lower() in jot[k]['value'].lower())):
						result = result + "| " + k + " "
						count+=1
				if (count > 0):
					self.bot.privmsg(target, nick + ": " + str(count) + " " + result)
		
	@irc3.event('^(@(?P<tags>\S+) )?:(?P<nick>\S+)(?P<mask>!\S+@\S+) PRIVMSG (?P<target>\S+) :;-(?P<key>[\w\s]+?)\s*$')
	def jot_remove(self, nick=None, mask=None, target=None, key=None, **kw):
		if (self.bot.obeying_commands(target) and nick in list(self.bot.channels[target].modes['@'])):
			with shelve.open('jot.shelf') as jot:
				key = key.lower()
				if (key in jot):
					print("JOT~~~ -[" + nick + "] " + jot[key]['key'] + " " + jot[key]['verb'] + " " + jot[key]['value'])
					del jot[key]
					self.bot.privmsg(nick, 'Ok.')
