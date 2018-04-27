import irc3, shelve, re
from irc3.plugins.command import command

@irc3.plugin
class Plugin:

	def __init__(self, bot):
		self.bot = bot
		self.jotfile = 'jotfile'
		self.controlchar = '>'
		self.features = {
			'add':	(re.compile('^'+self.controlchar+'(?P<key>[\w\s]+?)\s+=\s+(?P<data>.*)$'), self.jot_add, ['key', 'data']),
			'get':	(re.compile('^'+self.controlchar+'(?P<key>[\w\s]+?)\s*$'), self.jot_get, ['key']),
			'tell':	(re.compile('^'+self.controlchar+'(?P<key>[\w\s]+?)\s*@\s*(?P<at>\S+)\s*$'), self.jot_get, ['key', 'at']),
			'search':	(re.compile('^'+self.controlchar+'\?(?P<key>[\w\s]+?)\s*$'), self.jot_search, ['key']),
			'remove':	(re.compile('^'+self.controlchar+'-(?P<key>[\w\s]+?)\s*$'), self.jot_remove, ['key'])
		}
		
		print("JOT ~ LOADED")
			
	@classmethod
	def reload(cls, old):
		return cls(old.bot)
	
	def jot_load(self):
		self.jots = {}
		with shelve.open(self.jotfile) as channels:
			for channel in channels:
				self.jots[channel] = channels[channel]
	
	def jot_save(self):
		with shelve.open(self.jotfile) as channels:
			for channel in self.jots:
				channels[channel] = self.jots[channel]
	
	def jot_read(self, key, channel='g#l#o#b#a#l'):
		if channel in self.jots:
			if key.lower() in self.jots[channel]:
				return self.jots[channel][key.lower()]
		return None
	
	def jot_write(self, key, value, nick, channel='g#l#o#b#a#l'):
		if channel not in self.jots:
			self.jots[channel] = {}
		if key not in self.jots[channel]
			self.jots[channel][key.lower()] = {'key':key, 'from':nick 'value':data}
			return True
		return False
	
	@irc3.event('^(@\S+ )?:(?P<nick>\S+)!\S+@\S+ PRIVMSG (?P<target>\S+) :(?P<data>.*)$')
	def jot_core(self, nick, target, data, **kw):
		if (self.bot.obeying_commands(target)):
			for name in self.features:
				(pattern, func, args) = self.features[name]
				result = pattern.match(data)
				if result:
					arglist = []
					for arg in args:
						arglist.append(result.group(arg))
					func(nick, target, *arglist)
	
	def jot_add(self, nick, target, key, data):
		with shelve.open(self.jotfile) as jot:
			if (key.lower() not in jot):
				jot[key.lower()] = {'key':key, 'from':nick, 'verb':'=', 'value':data}
				self.bot.privmsg(nick, 'Ok.')
			else:
				self.bot.privmsg(nick, "The key '"+key+"' already exists.")
			
	def jot_get(self, nick, target, key, at=None):
		with shelve.open(self.jotfile) as jot:
			nick = at if at is not None else nick
			key = key.lower()
			if (key in jot):
					if (jot[key]['verb'] == '='):
						self.bot.privmsg(target, nick + ": " + jot[key]['value'])
					else:
						return self.bot.privmsg(target, nick + ": " + jot[key]['key'] + " " + jot[key]['verb'] + " " + jot[key]['value'])
	
	def jot_search(self, nick, target, key):
		with shelve.open(self.jotfile) as jot:
			result = "Results "
			count = 0
			for k in jot:
				if ((key.lower() in k) or (key.lower() in jot[k]['value'].lower())):
					result = result + " ;" + k + " "
					count+=1
			if (count > 0):
				self.bot.privmsg(target, nick + ": " + str(count) + " " + result)
		
	def jot_remove(self, nick, target, key):
		if nick in list(self.bot.channels[target].modes['@']):
			with shelve.open(self.jotfile) as jot:
				key = key.lower()
				if (key in jot):
					del jot[key]
					self.bot.privmsg(nick, 'Ok.')
