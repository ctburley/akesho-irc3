import irc3, shelve, re, os.path
from irc3.plugins.cron import cron
from random import choice

@irc3.plugin
class Jot:
    def __init__(self, bot):
        self.training = False
        self.bot = bot
        self.config = self.bot.config.get('jot', {})
        self.jotfile = self.config.get('jotfile', '.jots')
        self.controlchar = self.config.get('controlchar', '>')
        
        self.features = {
            #'': [ # template
            #    '(?P<key>[\w\s]+?)(?P<global>\s*-g)?',
            #    self., ['key', 'global']]
            'add': [ # key [-g ]= value
                '(?P<key>[\w\s]+?)(?P<global>\s*-g)?\s*=(?P<literal>=)?\s*(?P<data>.*)',
                self.jot_add, ['key', 'data', 'literal', 'global']],
            
            'also': [ # key [-g ]|= value
                '(?P<key>[\w\s]+?)(?P<global>\s*-g)?\s*\|=\s*(?P<data>.*)',
                self.jot_also, ['key', 'data', 'global']],
            
            'count': [ #   -#key
                '#(?P<key>[\w\s]+?)(?P<global>\s*-g)?',
                self.jot_count, ['key', 'global']],
            
            'suppliment': [ # key[.#] [-g ]+= data
                '(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<global>\s*-g)?\s*\+=(?P<data>.*)',
                self.jot_suppliment, ['key', 'data', 'rpi', 'global']],
            
            'subtract': [ # key[.#] [-g ]-= needle
                '(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<global>\s*-g)?\s*\-=(?P<data>.*)',
                self.jot_subtract, ['key', 'data', 'rpi', 'global']],
            
            'substitute':  [ # key[.#] [-g] ~needle=data
                '(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<global>\s*-g)?\s*\~(?P<needle>.*)(?<!\\\\)=(?P<data>.*)',
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
        self.jot = Jots(self.jotfile)
        
        if os.path.isfile(self.jotfile+'.tr'):
            self.training = True
            self.jot_train()
            self.training = False
        print("JOT ~ LOADED")
       
    def jot_train(self):
        tr = open(self.jotfile+".tr",'r')
        lines = tr.readlines()
        tr.close()
        # >channel
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
    
    def jot_add(self, nick, channel, key, data, literal=None, globl=None):
        target = '' if globl and nick in list(self.bot.channels[channel].modes['@']) else channel
        result = self.jot.add(key, target, {'literal': True if literal else False, 'key':key, 'from':nick, 'value':[data]})
        if not self.training:
            if result:
                self.bot.privmsg(channel, "'{}' added to {} storage.".format(key, 'global' if globl else target))
            else:
                self.bot.privmsg(channel, "'"+key+"' already exists.")
    
    def jot_also(self, nick, channel, key, data, globl=None):
        target = '' if globl and nick in list(self.bot.channels[channel].modes['@']) else channel
        if self.jot.exists(key, target):
            result = self.jot.read(key, target)
            result['value'].append(data)
            self.jot.write(key, target, result)
            if not self.training:
                self.bot.privmsg(channel, "'{}' added to '{}' in {} storage.".format(data,key,'global' if globl else target))
        else:
            if not self.training:
                self.bot.privmsg(channel, "'{}' does not exist yet, perhaps you meant = instead of |=?".format(key))
    
    def jot_count(self, nick, channel, key, globl=None):
        target = '' if globl else channel
        if self.jot.exists(key, target):
            result = self.jot.read(key, target)
            self.bot.privmsg(channel, "Key '{key}' has {count} responses.".format(key=key, count=len(result['value'])))
        else:
            self.bot.privmsg(channel, "Key '{}' does not exist.".format(key))
        
            
    def jot_suppliment(self, nick, target, key, data, rpi=None, globl=None):
        self.jot_substitute(nick, target, key, None, data, rpi, globl)
        
    def jot_subtract(self, nick, target, key, data, rpi=None, globl=None):
        self.jot_substitute(nick, target, key, data, '', rpi, globl)
        
    def jot_substitute(self, nick, channel, key, needle, data, rpi=None, globl=None):
        if self.training:
            return
        rpi = int(rpi) if rpi else -1
        target = '' if globl and nick in list(self.bot.channels[target].modes['@']) else channel
        jot = self.jot.read(key, target)
        if jot:
            if rpi > -1:
                if rpi < len(jot['value']):
                    if needle:
                        jot['value'][rpi] = jot['value'][rpi].replace(needle, data)
                    else:
                        jot['value'][rpi] += data
                    if not self.training:
                        self.bot.privmsg(channel, "'{}' has been modified.".format(key))
            else:
                if len(jot['value']) > 1:
                    self.bot.privmsg(channel, '"'+key+'" has '+str(len(jot['value']))+' responses, please indicate which you intend to modify with decimal notation. (key.0+)')
                else:
                    if needle:
                        jot['value'][0] = jot['value'][0].replace(needle, data)
                    else:
                        jot['value'][0] += data
                    if not self.training:
                        self.bot.privmsg(channel, "'{}' has been modified.".format(key))
            self.jot.write(key, jot, target)
    
    def jot_get(self, nick, target, key, response_index=None, globl=None, at=None):
        if self.training:
            return
        response_index = -1 if response_index is None else int(response_index)
        jot = self.jot.read(key) if (globl or not self.jot.exists(key, target)) else self.jot.read(key, target)
        if jot:
            value = None
            if response_index > -1:
                if response_index < len(jot['value']):
                    value = jot['value'][response_index]
            else:
                value = choice(jot['value'])
            if value:
                self.bot.privmsg(
                    target,
                    ('' if jot['literal'] else "{}: ".format(at if at else nick)) + \
                    value.format(
                        me=nick,
                        target=(at if at else 'someone'),
                        channel=target,
                        botnick=self.bot.nick,
                        cc=self.controlchar
                    )
                )

            
    def jot_search(self, nick, channel, key):
        if self.training:
            return
        result = "Results "
        count = 0
        target = channel
        if target in self.jot.data:
            for k in self.jot.data[target]:
                if key.lower() in k:
                    result = result + " " + self.controlchar + k + " "
                    count+=1
        for k in self.jot.data['']:
            if key.lower() in k:
                result = result + " " + self.controlchar + k + " "
                count+=1
        self.bot.privmsg(channel, nick + ": " + str(count) + " " + result)
    
    def jot_remove(self, nick, target, key, rpi=None, globl=None):
        channel = target
        if self.training or nick in list(self.bot.channels[target].modes['@']):
            rpi = int(rpi) if rpi else -1
            target = '' if globl else target
            key = key.lower()
            
            if self.jot.exists(key, target):
                if rpi > -1:
                    if len(self.jot.data[target][key]['value']) > 1:
                        if rpi < len(self.jot.data[target][key]['value']):
                            self.jot.data[target][key]['value'].pop(rpi)
                            if not self.training:
                                self.bot.privmsg(channel, "Response {} removed from '{}' in {} storage.".format(rpi, key, target))
                    else:
                        del self.jot.data[target][key]
                        if not self.training:
                            self.bot.privmsg(channel, "Only one response value, '{}' removed from {} storage.".format(key))
                else:
                    del self.jot.data[target][key]
                    if not self.training:
                        self.bot.privmsg(channel, "'{}' removed from {} storage.".format(key))
                    
    @cron('*/5 * * * *')
    def auto_save(self):
        self.jot.save()
                
    def jot_force_save(self, nick, target):
        if nick not in list(self.bot.channels[target].modes['@']):
            return
        self.jot.save()
        self.bot.privmsg(target, 'Jotfile forcibly saved.')

    # ** Upgrade jotfile if needed
    def jotfile_upgrade(self):
        with shelve.open(self.jotfile) as channels:
            if 'version' not in channels['']:
                print("UPGRADING JOTFILE")
                for channel in channels:
                    print(channel if channel != '' else "Global")
                    for jot in channels[channel]:
                        print(jot)
                        if 'literal' not in channels[channel][jot]:
                            print("upgraded")
                            channels[channel][jot]['literal'] = False
                channels['']['version'] = {'literal': False, 'key':'version', 'from':'bot', 'value':['0.0.1']}
    
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
    
    @irc3.event('^(@\S+ )?:(?P<nick>\S+)!\S+@\S+ PRIVMSG (?P<channel>\S+) :(?P<o>\S)?(?P<highlvl>(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?)(?P<c>\S)?\s*$')
    def hack_for_treesbot(self, nick, channel, o, highlvl, c, **kw):
        if o in ['[','{','!'] or c in [']','}']:
            self.jot_core(nick, channel, self.controlchar+highlvl)










class Jots:
    
    def add(self, key, target, data):
        if self.exists(key, target):
            return False
        else:
            self.write(key, target, data)
            return True
            
    def exists(self, key, channel=''):
        return (channel in self.data) and (key.lower() in self.data[channel])
        
    def read(self, key, channel=''):
        return self.data.get(channel,{}).get(key.lower(),None)
    
    def write(self, key, channel, value):
        if channel not in self.data:
            self.data[channel] = {}
        self.data[channel][key.lower()] = value
    
    def erase(self, key, channel, index=-1):
        if channel not in self.data:
            self.data[channel] = {}
        self.data[channel].pop(key.lower(), None)
    
    # --- utility functions
    def __init__(self, shelf_file):
        self.filename = shelf_file
        self.data = {}
        self.load()
    
    def load(self, newfile=False):
        if newfile:
            self.filename = newfile
        with shelve.open(self.filename) as channels:
            for channel in channels:
                self.data[channel] = channels[channel]
        if '' not in self.data:
            self.data[''] = {}
            
    def save(self):
        with shelve.open(self.filename) as channels:
            for channel in self.data:
                channels[channel] = self.data[channel]
