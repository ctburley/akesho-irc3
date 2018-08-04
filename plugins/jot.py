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
                '(?P<key>[\w\s]+?)(?P<globl>\s*-g)?\s*=(?P<literal>=)?\s*(?P<data>.*)',
                self.jot_add, ['key', 'data', 'literal', 'globl']],
            
            'also': [ # key [-g ]|= value
                '(?P<key>[\w\s]+?)(?P<globl>\s*-g)?\s*\|=\s*(?P<data>.*)',
                self.jot_also, ['key', 'data', 'globl']],
            
            'count': [ #   -#key
                '#(?P<key>[\w\s]+?)(?P<globl>\s*-g)?',
                self.jot_count, ['key', 'globl']],
            
            'suppliment': [ # key[.#] [-g ]+= data
                '(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<globl>\s*-g)?\s*\+=(?P<data>.*)',
                self.jot_suppliment, ['key', 'data', 'rpi', 'globl']],
            
            'subtract': [ # key[.#] [-g ]-= needle
                '(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<globl>\s*-g)?\s*\-=(?P<data>.*)',
                self.jot_subtract, ['key', 'data', 'rpi', 'globl']],
            
            'substitute':  [ # key[.#] [-g] ~needle=data
                '(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<globl>\s*-g)?\s*\~(?P<needle>.*)(?<!\\\\)=(?P<data>.*)',
                self.jot_substitute, ['key', 'needle', 'data', 'rpi', 'globl']],
            
            'get': [ # key[.#] [-g] [| chain]
                '(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<globl>\s*-g)?(?P<chain>\s*(?:\|\s*\S+\s*)+)?',
                self.jot_get, ['key', 'rpi', 'globl','chain']],
             
            'literal': [ # !key.# -g
                '!(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<globl>\s*-g)?',
                self.jot_literal, ['key', 'rpi', 'globl']],
            
            'tell': [ # key[.#] [-g ]@ target
                '(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<globl>\s*-g)?\s*@\s*(?P<at>\S+)',
                self.jot_get, ['key', 'rpi', 'globl', 'at']],
            
            'search': [ # ?key
                '\?(?P<key>[\w\s]+?)',
                self.jot_search, ['key']],
            
            'remove': [ # -key[.#] [-g]
                '-(?P<key>[\w\s]+?)(?:\.(?P<rpi>\d+))?(?P<globl>\s*-g)?',
                self.jot_remove, ['key', 'rpi', 'globl']],
            
            'save': [ # double command character save + nick is opped in channel
                self.controlchar+'save', self.jot_force_save, []],
        }
        
        # compile feature regexps
        for feature in self.features:
            self.features[feature][0] = re.compile('^'+self.controlchar+self.features[feature][0]+'\s*$')
        
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
                return "'{}' added to {} storage.".format(key, 'global' if globl else target)
            else:
                return "'"+key+"' already exists."
    
    def jot_also(self, nick, channel, key, data, globl=None):
        target = '' if globl and nick in list(self.bot.channels[channel].modes['@']) else channel
        if self.jot.exists(key, target):
            result = self.jot.read(key, target)
            result['value'].append(data)
            self.jot.write(key, target, result)
            if not self.training:
                return "'{}' added as '{}.{}' in {} storage.".format(data,key,len(result['value'])-1,'global' if globl else target)
        else:
            if not self.training:
                return "'{}' does not exist yet, perhaps you meant = instead of |=?".format(key)
    
    def jot_count(self, nick, channel, key, globl=None):
        target = '' if globl else channel
        if self.jot.exists(key, target):
            result = self.jot.read(key, target)
            return "Key '{key}' has {count} responses.".format(key=key, count=len(result['value']))
        else:
            return "Key '{}' does not exist.".format(key)
        
            
    def jot_suppliment(self, nick, target, key, data, rpi=None, globl=None):
        return self.jot_substitute(nick, target, key, None, data, rpi, globl)
        
    def jot_subtract(self, nick, target, key, data, rpi=None, globl=None):
        return self.jot_substitute(nick, target, key, data, '', rpi, globl)
        
    def jot_substitute(self, nick, channel, key, needle, data, rpi=None, globl=None):
        if self.training:
            return None
        rpi = int(rpi) if rpi else -1
        target = '' if globl and nick in list(self.bot.channels[channel].modes['@']) else channel
        jot = self.jot.read(key, target)
        if jot:
            if rpi > -1:
                if rpi < len(jot['value']):
                    if needle:
                        jot['value'][rpi] = jot['value'][rpi].replace(needle, data)
                    else:
                        jot['value'][rpi] += data
                    if not self.training:
                        return "'{}' has been modified.".format(key)
            else:
                if len(jot['value']) > 1:
                    return '"'+key+'" has '+str(len(jot['value']))+' responses, please indicate which you intend to modify with decimal notation. (key.0+)'
                else:
                    if needle:
                        jot['value'][0] = jot['value'][0].replace(needle, data)
                    else:
                        jot['value'][0] += data
                    if not self.training:
                        return "'{}' has been modified.".format(key)
            self.jot.write(key, jot, target)
    
    def jot_get(self, nick, target, key, rpi=None, globl=None, at=None, chain=None, embed=False):
        if self.training:
            return None
        that_was = "That was "+self.controlchar+key+" used by "+nick+"."
        rpi = -1 if rpi is None else int(rpi)
        that_was += " It was read from {} storage.".format("global" if globl or not self.jot.exists(key,target) else target)
        jot = self.jot.read(key) if (globl or not self.jot.exists(key, target)) else self.jot.read(key, target)
        if jot:
            value = None
            if rpi > -1:
                that_was += " They asked for response #"+str(rpi)+"."
                if rpi < len(jot['value']):
                    value = jot['value'][rpi]
            else:
                rpi = choice(range(len(jot['value'])))
                if len(jot['value']) > 1:
                    that_was += " They got random response #"+str(rpi)+"."
                value = jot['value'][rpi]
            if value:
                if key.lower() != 'what was that' and not embed:
                    self.jot.write('what was that', target, {'literal': True, 'key':'what was that', 'from':nick, 'value':[that_was]})
                to_chain = (('' if jot['literal'] else "{}: ".format(at if at else nick)) + \
                    value.format(
                        **{'me':nick,
                        'target':(at if at else 'someone'),
                        'channel':target,
                        'botnick':self.bot.nick,
                        'cc':self.controlchar,
                        self.controlchar:JotCursor(self,target,nick,(at if at else None))}
                    ))
                if chain:
                    chain = chain.split('|')[1:]
                    if len(chain) > 1:
                        chain = chain[0] +" "+ to_chain + "|" + "|".join(chain[1:])
                    else:
                        chain = chain[0] +" "+ to_chain
                    return self.bot.chain(chain)
                else:
                    return to_chain
        else:
            return None
                    
    def jot_literal(self, nick, target, key, rpi=None, globl=None):
        if self.training:
            return None
        rpi
        jot = self.jot.read(key) if (globl or not self.jot.exists(key, target)) else self.jot.read(key, target)
        if jot:
            if rpi:
                rpi = int(rpi)
                if rpi < len(jot['value']):
                    return jot['value'][rpi]
                else:
                    return "'{}' only has {} values.".format(key,len(jot['values']))
            else:
                if len(jot['value']) > 1:
                    return "'{}' has {} responses to choose from, which one would you like to see?".format(key,len(jot['value']))
                return jot['value'][0]
        return None
            
    def jot_search(self, nick, channel, key):
        if self.training:
            return None
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
        return nick + ": " + str(count) + " " + result
    
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
                                return "Response {} removed from '{}' in {} storage.".format(rpi, key, 'global' if target == '' else target)
                    else:
                        del self.jot.data[target][key]
                        if not self.training:
                             return "Only one response value, '{}' removed from {} storage.".format(key, 'global' if target == '' else target)
                else:
                    del self.jot.data[target][key]
                    if not self.training:
                        return "'{}' removed from {} storage.".format(key, 'global' if target == '' else target)
                    
    @cron('*/5 * * * *')
    def auto_save(self):
        self.jot.save()
                
    def jot_force_save(self, nick, target):
        if nick not in list(self.bot.channels[target].modes['@']):
            return None
        self.jot.save()
        return 'Jotfile forcibly saved.'
    
    # ---  Core
        
    @irc3.event('^(@\S+ )?:(?P<nick>\S+)!\S+@\S+ PRIVMSG (?P<target>\S+) :(?P<data>.*)$')
    def jot_core(self, nick, target, data, **kw):
        if (self.bot.obeying_commands(target)):
            for name in self.features:
                (pattern, func, args) = self.features[name]
                result = pattern.match(data)
                if result:
                    arglist = {'nick': nick, 'target': target}
                    for arg in args:
                        arglist[arg] = result.group(arg)
                    
                    self.log(name, arglist)
                    result = func(**arglist)
                    if result:
                        self.bot.privmsg(target, result)

    def log(self, feature, a):
        print('JOT:\t' + feature + str(a))
    
    @irc3.event(r'^(@\S+ )?:(?P<nick>\S+)!\S+@\S+ PRIVMSG (?P<channel>\S+) :(?P<data>.*?)\s*$')
    def hack_for_treesbot(self, nick, channel, data, **kw):
        do = None
        (o,key,c) = (data[0],data[1:-1],data[-1])
        if o == '!':
            do = key + c
        if o in ['[','{']:
            if c in [']','}']:
                do = key
            else:
                do = key + c
        else:
            if c in [']','}']:
                do = o+key
        if do:
            self.jot_core(nick, channel, self.controlchar+do)



class JotCursor:
    def __init__(self, _plugin, _channel, _nick, _target):
        self.controlchar = _plugin.controlchar
        (self.pattern,self.func,self.args) = _plugin.features['get']
        self.channel = _channel
        self.nick = _nick
        self.target = _target
        
    def __getitem__(self, key):
        result = self.pattern.match(self.controlchar+str(key))
        if result:
            arglist = {
                'nick': self.nick,
                'target': self.channel,
                'key': result.group('key'),
                'rpi': result.group('rpi'),
                'globl': result.group('global'),
                'embed': True
            }
            if self.target:
                arglist['at'] = self.target
            result = self.func(**arglist)
            if result:
                return result
        return "Not Found"
    



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
