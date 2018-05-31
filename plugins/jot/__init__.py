import irc3, shelve, re, os.path
from irc3.plugins.cron import cron
from random import choice

@irc3.plugin
class Plugin:

    def __init__(self, bot):
        self.training = False
        self.bot = bot
        self.jotfile = self.bot.config.get('jot', {}).get('jotfile','.jots')
        self.controlchar = self.bot.config.get('jot', {}).get('controlchar','>')
        
        self.features = {
            'add': [ # key [-g ]= value
                '(?P<key>[\w\s]+?)(?P<global>\s*-g)?\s*=\s*(?P<data>.*)',
                self.jot_add, ['key', 'data', 'global']],
            
            'also': [ # key [-g ]|= value
                '(?P<key>[\w\s]+?)(?P<global>\s*-g)?\s*\|=\s*(?P<data>.*)',
                self.jot_also, ['key', 'data', 'global']],
            
            'suppliment': [ # key[.#] [-g ]+= data
                '(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<global>\s*-g)?\s*\+=\s*(?P<data>.*)',
                self.jot_suppliment, ['key', 'data', 'rpi', 'global']],
            
            'subtract': [ # key[.#] [-g ]-= needle
                '(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<global>\s*-g)?\s*\-=\s*(?P<data>.*)',
                self.jot_subtract, ['key', 'data', 'rpi', 'global']],
            
            'substitute':  [ # key[.#] [-g] ~needle=data
                '(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<global>\s*-g)?\s*\~(?P<needle>.*)(?<!\\\\)=\s*(?P<data>.*)',
                self.jot_substitute, ['key', 'needle', 'data', 'rpi', 'global']],
            
            'get': [ # key[.#] [-g]
                '(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<global>\s*-g)?',
                self.jot_get, ['key', 'rpi', 'global']],
            
            'tell': [ # key[.#] [-g ]@ target
                '(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<global>\s*-g)?\s*@\s*(?P<at>\S+)',
                self.jot_get, ['key', 'rpi', 'global', 'at']],
            
            'search': [ # ?key
                '\?(?P<key>[\w\s]+?)',
                self.jot_search, ['key']],
            
            'remove': [ # -key[.#] [-g]
                '-(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<global>\s*-g)?',
                self.jot_remove, ['key', 'rpi', 'global']],
            
            'save': [ # double command character save + nick is opped in channel
                self.controlchar+'save', self.jot_force_save, []],
        }
        
        # compile feature regexps
        for feature in self.features:
            self.features[feature][0] = re.compile('^'+self.controlchar+self.features[feature][0]+'\s*$')
        
        self.jotfile_upgrade()
        
        self.jot_load()
        
        if os.path.isfile(self.jotfile+'.tr'):
            self.training = True
            self.jot_train()
            self.training = False
        print("JOT ~ LOADED")
       
    def jot_train(self):
        tr = open(self.jotfile+".tr",'r')
        lines = tr.readlines()
        tr.close()
        # \t(channel)
        # trigger lines follow
        channel = ''
        nick = self.bot.nick
        newchan = re.compile('^>(?P<channel>\S+)$')
        for line in lines:
            change = newchan.match(line)
            if change:
                print("NEW CHANNEL")
                channel = change.group('channel')
            else:
                self.jot_core(nick, channel, self.controlchar+line)
    # --- Features
    
    def jot_add(self, nick, target, key, data, globl=None):
        if globl is not None and nick in list(self.bot.channels[target].modes['@']):
            target = ''
        if not self.jot_exists(key, target):
            self.jot_write(key, {'key':key, 'from':nick, 'value':[data]}, target)
            if not self.training:
                self.bot.privmsg(nick, 'Ok.')
        else:
            if not self.training:
                self.bot.privmsg(nick, "'"+key+"' already exists.")
    
    def jot_also(self, nick, target, key, data, globl=None):
        if globl is not None and nick in list(self.bot.channels[target].modes['@']):
            target = ''
        if self.jot_exists(key, target):
            result = self.jot_read(key, target)
            result['value'].append(data)
            self.jot_write(key, result, target)
            if not self.training:
                self.bot.privmsg(nick, 'Ok.')
        else:
            self.jot_add(nick, target, key, data, globl)
            
    def jot_suppliment(self, nick, target, key, data, rpi=None, globl=None):
        self.jot_substitute(nick, target, key, None, data, rpi, globl)
        
    def jot_subtract(self, nick, target, key, data, rpi=None, globl=None):
        self.jot_substitute(nick, target, key, data, '', rpi, globl)
        
    def jot_substitute(self, nick, target, key, needle, data, rpi=None, globl=None):
        if self.training:
            return
        rpi = int(rpi) if rpi else -1
        if globl is not None and nick in list(self.bot.channels[target].modes['@']):
            target = ''
        jot = self.jot_read(key, target)
        if jot:
            if rpi > -1:
                if rpi < len(jot['value']):
                    if needle:
                        jot['value'][rpi] = jot['value'][rpi].replace(needle, data)
                    else:
                        jot['value'][rpi] += data
                    if not self.training:
                        self.bot.privmsg(nick, 'Ok.')
            else:
                if len(jot['value']) > 1:
                    self.bot.privmsg(nick, '"'+key+'" has more than one respone, please indicate which you which you modify with decimal notation. (key.0+)')
                else:
                    if needle:
                        jot['value'][0] = jot['value'][0].replace(needle, data)
                    else:
                        jot['value'][0] += data
                    if not self.training:
                        self.bot.privmsg(nick, 'Ok.')
            self.jot_write(key, jot, target)
    
    def jot_get(self, nick, target, key, response_index=None, globl=None, at=None):
        if self.training:
            return
        response_index = -1 if response_index is None else int(response_index)
        nick = at if at is not None else nick
        jot = self.jot_read(key) if (globl or not self.jot_exists(key, target)) else self.jot_read(key, target)
        if jot:
            if response_index > -1:
                if response_index < len(jot['value']):
                    self.bot.privmsg(target, nick + ": " + jot['value'][response_index])
            else:
                self.bot.privmsg(target, nick + ": " + choice(jot['value']))
            return
            
    def jot_search(self, nick, target, key):
        if self.training:
            return
        result = "Results "
        count = 0
        if target in self.jots:
            for k in self.jots[target]:
                if key.lower() in k:
                    result = result + " " + self.controlchar + k + " "
                    count+=1
        for k in self.jots['']:
            if key.lower() in k:
                result = result + " " + self.controlchar + k + " "
                count+=1
        self.bot.privmsg(target, nick + ": " + str(count) + " " + result)
    
    def jot_remove(self, nick, target, key, rpi=None, globl=None):
        if self.training or nick in list(self.bot.channels[target].modes['@']):
            rpi = int(rpi) if rpi else -1
            target = '' if globl else target
            key = key.lower()
            
            if self.jot_exists(key, target):
                if rpi > -1:
                    if len(self.jots[target][key]['value']) > 1:
                        if rpi < len(self.jots[target][key]['value']):
                            self.jots[target][key]['value'].pop(rpi)
                    else:
                        del self.jots[target][key]
                else:
                    del self.jots[target][key]
                if not self.training:
                    self.bot.privmsg(nick, 'Ok.')
                    
    # --- Reload & Accessors
                    
    @classmethod
    def reload(cls, old):
        return cls(old.bot)
    
    def jot_load(self):
        self.jots = {}
        with shelve.open(self.jotfile) as channels:
            for channel in channels:
                self.jots[channel] = channels[channel]
        if '' not in self.jots:
            self.jots[''] = {}
    
    def jot_force_save(self, nick, target):
        if nick not in list(self.bot.channels[target].modes['@']):
            return
        self.jot_save()
        self.bot.privmsg(nick, 'Ok.')

    @cron('*/5 * * * *')
    def jot_save(self):
        with shelve.open(self.jotfile) as channels:
            for channel in self.jots:
                channels[channel] = self.jots[channel]
    
    def jot_read(self, key, channel=''):
        key = key.lower()
        if channel in self.jots:
            if key in self.jots[channel]:
                return self.jots[channel][key]
        return None
    
    def jot_write(self, key, value, channel):
        if channel not in self.jots:
            self.jots[channel] = {}
        result = not self.jot_exists(key, channel)
        self.jots[channel][key.lower()] = value
        return result
    
    def jot_exists(self, key, channel=''):
        return (channel in self.jots) and (key.lower() in self.jots[channel])
        
    # ** Upgrade jotfile if needed
    def jotfile_upgrade(self):
        with shelve.open(self.jotfile) as channels:
            if 'g#l#o#b#a#l' in channels:
                beep = channels['g#l#o#b#a#l']
                del channels['g#l#o#b#a#l']
                channels[''] = beep
    
    # ---  Core
        
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
                    self.log(name, nick, target, arglist)
                    func(nick, target, *arglist)

    def log(self, feature, nick, target, args):
        print('JOT:\t' +nick +'@' +target +' ' +feature +' ',args)
    


    @irc3.event('^(@\S+ )?:(?P<nick>\S+)!\S+@\S+ PRIVMSG (?P<channel>\S+) :(\{|\[)(?P<highlvl>\d+)(\}|\])$')
    def hack_for_treesbot(self, nick, channel, highlvl, **kw):
        self.jot_core(nick, channel, self.controlchar+highlvl)
