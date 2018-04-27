import irc3, shelve, re
from irc3.plugins.command import command

@irc3.plugin
class Plugin:

	def __init__(self, bot):
		self.bot = bot
		self.patterns = {
			'add':	re.compile('^;(?P<key>[\w\s]+?)\s+=\s+(?P<data>.*)$'),
			'get':	re.compile('^;(?P<key>[\w\s]+?)\s*$'),
			'tell':	re.compile('^;(?P<key>[\w\s]+?)\s*@\s*(?P<at>\S+)\s*$'),
			'search':	re.compile('^;\?(?P<key>[\w\s]+?)\s*$'),
			'remove':	re.compile('^;-(?P<key>[\w\s]+?)\s*$')
		}
		self.reserved = [ 'help' ]
		
		print("JOT ~ LOADED")
			
	@classmethod
	def reload(cls, old):
		return cls(old.bot)
	

	@irc3.event('^(@\S+ )?:(?P<nick>\S+)!\S+@\S+ PRIVMSG (?P<target>\S+) :(?P<data>.*)$')
	def jot_core(self, nick, target, data, **kw):
		if (self.bot.obeying_commands(target)):
			### Add
			result = self.patterns['add'].match(data)
			if result:
				self.jot_plus(nick, target, result.group('key'), result.group('data'))
			### Append
			### Get
			result = self.patterns['get'].match(data)
			if result:
				self.jot_get(nick, target, result.group('key'))
			### Tell
			result = self.patterns['tell'].match(data)
			if result:
				self.jot_get(result.group('at'), target, result.group('key'))
			### Search
			result = self.patterns['search'].match(data)
			if result:
				self.jot_search(nick, target, result.group('key'))
			### Delete
			result = self.patterns['remove'].match(data)
			if result:
				self.jot_remove(nick, target, result.group('key'))
	
	def jot_plus(self, nick, target, key, data):
		with shelve.open('jot.shelf') as jot:
			if (key.lower() not in jot):
				jot[key.lower()] = {'key':key, 'from':nick, 'verb':'=', 'value':data}
				self.bot.privmsg(nick, 'Ok.')
			else:
				self.bot.privmsg(nick, "The key '"+key+"' already exists.")
			
	def jot_get(self, nick, target, key):
		with shelve.open('jot.shelf') as jot:
			key = key.lower()
			if (key in jot):
					if (jot[key]['verb'] == '='):
						self.bot.privmsg(target, nick + ": " + jot[key]['value'])
					else:
						return self.bot.privmsg(target, nick + ": " + jot[key]['key'] + " " + jot[key]['verb'] + " " + jot[key]['value'])
	
	def jot_search(self, nick, target, key):
		with shelve.open('jot.shelf') as jot:
			result = "Results"
			count = 0
			for k in jot:
				if ((key.lower() in k) or (key.lower() in jot[k]['value'].lower())):
					result = result + "| " + k + " "
					count+=1
			if (count > 0):
				self.bot.privmsg(target, nick + ": " + str(count) + " " + result)
		
	def jot_remove(self, nick, target, key):
		if nick in list(self.bot.channels[target].modes['@']):
			with shelve.open('jot.shelf') as jot:
				key = key.lower()
				if (key in jot):
					del jot[key]
					self.bot.privmsg(nick, 'Ok.')
	
	@command
	def jot_dump(self, m,t,a):
		"""mwememem
			%%jot_dump
		"""
		with shelve.open('jot.shelf') as jot:
			for key in jot:
				print (jot[key]['key'] + " = " jot[key]['value']) 
