import irc3
import shelve
import time
import os
from random import randint
from random import choice
from irc3.plugins.command import command


@irc3.plugin
class Henk:

    def __init__(self, bot):
        self.bot = bot
        
        self.directory = './data/deks/'
        
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            
        self.huntEnabled = self.dekSpotted = self.lineCount = self.dekDelay = self.dekTime = self.quietFail = {}
        
        print("HENK ~ Deks Loaded Redy 2 Go")

    def load_deks(self, filename):
        if not filename.startswith('#'):
            return False;
        if filename in self.huntEnabled:
            print("Enabled: {}   Quieter: {}   Dek Loose: {}   When: {}".format(
                self.huntEnabled[filename], self.quietFail[filename], self.dekSpotted[filename], self.dekTime[filename]))
            return True
        
        
        if not os.path.isfile(os.path.join(self.directory, filename+'-data')):
            with shelve.open(os.path.join(self.directory, filename+'-data')) as data:
                data['quiet'] = False
                data['dekTime'] = -1

        print("Loading Deks for " + filename)  # filename is the channel name
        self.lineCount[filename] = 0
        self.dekDelay[filename] = 70
        
        with shelve.open(os.path.join(self.directory, filename+'-data')) as data:
            self.huntEnabled[filename] = 'hunt' in data
            self.quietFail[filename] = False if 'quiet' not in data else data['quiet']
            self.dekTime[filename] = -1 if 'dekTime' not in data else data['dekTime']
            self.dekSpotted[filename] = (self.dekTime[filename] is not -1)
        print("Enabled: {}   Quieter: {}   Dek Loose: {}   When: {}".format(
            self.huntEnabled[filename], self.quietFail[filename], self.dekSpotted[filename], self.dekTime[filename]))
        return True

    @command
    def ht(s,m,t,a):
        """a
            %%ht
        """
        
    @command(permission='admin',show_in_help_menu=False)
    def mergedeks(self, mask, target, args):
        """MeRgE FroM One tO AnOtHer
            
            %%mergedeks <from> <to> [yes]
        """
        return
        d_from = args['<from>'].lower()
        d_to = args['<to>'].lower()
        if args['yes']:
            print("DEKS MERGING FROM: " + d_from + "  TO: " + d_to + "  BY: " + mask.nick)
            with shelve.open(os.path.join(self.directory, target)) as reks:
                self.bot.privmsg(mask.nick, "Ok.")
                reks[d_to] = {'f': (reks[d_to]['f'] + reks[d_from]['f']), 'b': (reks[d_to]['b'] + reks[d_from]['b'])}
                del reks[d_from]
        
    @classmethod
    def reload(cls, old):
        return cls(old.bot)
    
    def dek_send(self, target, text, immediate=True):
        if len(text) < 1:
            text = "¯\_(ツ)_/¯"
        i, u, l = 1, text.upper(), text.lower()
        text = choice([u[0],l[0]])
        for i in range(1, len(u)):
            text += u[i] if ((randint(1,56)%2) == 0) else l[i]
        print('HENK~~~ ' + target + ":" + text)
        self.bot.privmsg(target, text, immediate)

    def get_record(self, target, nick):
        with shelve.open(self.directory+target) as records:
            record = {'f': 0, 'b': 0} if (nick.lower() not in records) else records[nick.lower()]
        return record
    
    def setRecord(self, target, nick, record):
        with shelve.open(self.directory+target) as records:
            records[nick.lower()] = record
    
    @command
    def dekhelp(self, mask, target, args):
        """EsPlAiNs a DeK HeNt. hEnK HenK.
            
            %%dekhelp
        """
        self.dek_send(target, 'welcome to shitty dek hunt, !fren or !beng, '
                              'check your !deks and leader boards, !friendos and !bangers')
    
    @command(permission='owner',show_in_help_menu=False)
    def dektest(self, mask, target, args):
        """test a dek
            %%dektest
        """
        print("DEK TEST: " + mask.nick)
        if not self.load_deks(target):
            return
        self.lineCount[target] = 2000
        self.on_line(target, 'PRIVMSG', None, mask)
        
    @command(permission='admin')
    def hunt(self, mask, target, args):
        """HuNt a dEk? tUrN Me oN. nO LoOk fOr DeK? TuRn mE OfF. I cAn AlSo fAiL SiLeNtLy.
            %%hunt [on|off|quieter]
        """
        if not self.load_deks(target):
            return
        
        if args['on']:
            self.huntEnabled[target] = True
            self.dek_send(target, "ok hot stuff, bring it on!")
            with shelve.open(os.path.join(self.directory, target+'-data')) as data:
                print("SAVING STATE")
                data['hunt'] = {}
            return
        else:
            if args['off']:
                self.huntEnabled[target] = False
                self.dek_send(target, "i see how it is, pansy!")
                with shelve.open(os.path.join(self.directory, target+'-data')) as data:
                    if 'hunt' in data:
                        del data['hunt']
                return
        
        if args['quieter']:
            self.quietFail[target] = not self.quietFail[target]
            if self.quietFail[target]:
                self.dek_send(target, "i will now be less verbose. repeat to toggle.")
            else:
                self.dek_send(target, "i will not be less verbose. repeat to toggle.")
            with shelve.open(self.directory+target+'-data') as data:
                data['quiet'] = self.quietFail[target]
            return
        
        self.dek_send(target, 'The hunt is ' + ('on.' if self.huntEnabled[target] else 'not on.'))

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_line(self, target, event, data, mask):
        if event == 'NOTICE':
            return
        if not self.load_deks(target):
            return

        if self.huntEnabled[target]:
            self.lineCount[target] += 1
            if self.lineCount[target] > self.dekDelay[target]+randint(int(self.dekDelay[target]/10),
                                                                      int(self.dekDelay[target]/3)):
                self.lineCount[target] = 0
                if self.dekSpotted[target]:
                    self.dek_send(target, (''.join(' ' for i in range(randint(11, 55))) + 'flap.'))
                else:
                    self.dekSpotted[target] = True
                    self.dek_send(target, "there is a dek", False)
                    self.dekTime[target] = time.time()
                    with shelve.open(self.directory + target + '-data') as data:
                        data['dekTime'] = self.dekTime[target]
                    return
            
    @command
    def fren(self, mask, target, args):
        """MaKe FRiENDs wItH a DeK
            
            %%fren
        """
        if not self.load_deks(target):
            return

        if (self.huntEnabled[target]):
            if (self.dekSpotted[target]):
                stopTime = time.time()
                tDiff = stopTime - self.dekTime[target]
                record = self.get_record(target, mask.nick)
                record['f'] += 1
                fasts = ""
                if ('fast' in record):
                    if (tDiff < record['fast']):
                        fasts = " Wowee that is your fastest dek yet!"
                        record['fast'] = tDiff
                else:
                    record['fast'] = tDiff
                    
                if ('slow' in record):
                    if (tDiff > record['slow']):
                        fasts = " That was your longest so far, what took you so long bby?"
                        record['slow'] = tDiff
                else:
                    record['slow'] = tDiff
                
                self.setRecord(target, mask.nick, record)
                with shelve.open(self.directory+target+'-data') as data:
                    data['dekTime'] = -1
                self.dek_send(target, "henk henk henk! after " + str(round(tDiff, 3)) + " seconds; " + str(mask.nick) + ", " + str(record['f']) + " deks now owe you a life debt." + fasts)
                self.dekSpotted[target] = False
            else:
                if not self.quietFail[target]:
                    self.dek_send(target, "there is no dek, why you do that?")
    
    @command
    def beng(self, mask, target, args):
        """ShOoT At a dEk
            
            %%beng
        """
        if not self.load_deks(target):
            return

        if (self.huntEnabled[target]):
            if (self.dekSpotted[target]):
                stopTime = time.time()
                tDiff = stopTime - self.dekTime[target]
                record = self.get_record(target, mask.nick)
                record['b'] += 1
                fasts = ""
                if ('fast' in record):
                    if (tDiff < record['fast']):
                        fasts = " Wowee that is your fastest dek yet!"
                        record['fast'] = tDiff
                else:
                    record['fast'] = tDiff
                    
                if ('slow' in record):
                    if (tDiff > record['slow']):
                        fasts = " That was your longest so far, nearly got away!"
                        record['slow'] = tDiff
                else:
                    record['slow'] = tDiff
                
                self.setRecord(target, mask.nick, record)
                with shelve.open(self.directory+target+'-data') as data:
                    data['dekTime'] = -1
                self.dek_send(target, "pew, pew, pew; " + mask.nick + " kills a dek in the face in " + str(round(tDiff, 3)) + " seconds!" + fasts + " Watching from the shadows are " + str(record['b']) + " ghostly pairs of beady eyes.")
                self.dekSpotted[target] = False
            else:
                if not self.quietFail[target]:
                    self.dek_send(target, "watch out, is no dek, no pew pew!")
    
    @command
    def deks(self, mask, target, args):
        """ChEcK Ur dEkS oR sUmOnE eLsEs
            
            %%deks [<nick>] [times]
        """
        if not self.load_deks(target):
            return
        if not self.huntEnabled[target]:
            return
            
        sum1_els = args['<nick>'] is not None
        usr = mask.nick if not sum1_els else args['<nick>']
        record = self.get_record(target, usr)
        frens = str('no' if (record['f'] == 0) else record['f'])
        emine = str('no' if (record['b'] == 0) else record['b'])
        wyb = 'watch ur back' if (record['b'] >= record['f']) else 'yuo safe, fren.'
        if not sum1_els:
            fast = '' if ((not args['times']) or ('fast' not in record)) else 'ur fastest dek was '+str(round(record['fast'],4))+'s, and slowest was '+str(round(record['slow'],4))+'s, and '
            self.dek_send(target, "Hey, " + mask.nick + ", " + fast + "you has " + frens + " dek frens protecting you from " + emine + " dek emines. " + wyb)
        else:
            fast = '' if ((not args['times']) or ('fast' not in record)) else ', and their fastest dek was '+str(round(record['fast'],4))+'s, and slowest was '+str(round(record['slow'],4))+'s'
            self.dek_send(target, mask.nick + ", " + self.bot.np(usr) + " has " + frens + " frens, " + emine + " emines" + fast + ". Soz I tell dem '" + wyb + "'")
        
    @command
    def friendos(self, mask, target, args):
        """WhO goT Da mOaSt fRiEnDo DeKs
            
            %%friendos
        """
        if not self.load_deks(target):
            return
        if not self.huntEnabled[target]:
            return

        top = {}
        with shelve.open(self.directory+target) as records:
            s_records = sorted(records, key=lambda x: records[x]['f'], reverse=True)
            idx = 0
            while idx < 5 and idx < len(s_records):
                if records[s_records[idx]]['f'] > 0:
                    top[s_records[idx]] = records[s_records[idx]]['f']
                    idx += 1
        response = ":: best friendos :: "
        topnames = sorted(top, key=lambda x: top[x], reverse=True)
        for names in topnames:
            response += self.bot.np(names) + " with " + str(top[names]) + " :: "
        self.dek_send(target, response)
    
    @command
    def bangers(self, mask, target, args):
        """WhO BeEn BaNgIn dEm DeKS?
            
            %%bangers
        """
        if not self.load_deks(target):
            return
        if not self.huntEnabled[target]:
            return

        top = {}
        with shelve.open(self.directory+target) as records:
            s_records = sorted(records, key=lambda x: records[x]['b'], reverse=True)
            idx = 0
            while idx < 5 and idx < len(s_records):
                if records[s_records[idx]]['b'] > 0:
                    top[s_records[idx]] = records[s_records[idx]]['b']
                    idx += 1
        response = ":: dem bangerinos :: "
        topnames = sorted(top, key=lambda x: top[x], reverse=True)
        for names in topnames:
            response += self.bot.np(names) + " with " + str(top[names]) + " :: "
        self.dek_send(target, response)
    
    @command
    def dektimes(self, mask, target, args):
        """SeE tHe ChAnNeLs FaStEsT aNd SlOwEsT dEkS, uSe GlOBAl To SeE aCrOsS aLl ChAnNeLs
            %%dektimes [global]"""
        if not self.load_deks(target):
            return
        if not self.huntEnabled[target]:
            return
        
        top = None
        pot = None
        f, s = '', ''

        if args['global']:
            top_channel = ""
            pot_channel = ""
            for file in os.listdir(self.directory):
                if not file.endswith('-data'):
                    with shelve.open(self.directory + file) as records:
                        for name in records.keys():
                            rec = records[name]
                            if 'name' not in rec:
                                rec['name'] = name

                            (top, top_channel) = (rec, file) if top is None \
                                and 'fast' in rec or 'fast' in rec and rec['fast'] < top['fast'] else (top, top_channel)
                            (pot, pot_channel) = (rec, file) if pot is None \
                                and 'slow' in rec or 'slow' in rec and rec['slow'] > pot['slow'] else (pot, pot_channel)
            f = '' if top is None else "Fastest dekerino is " + top['name'] + " in "+top_channel+" with " + str(
                round(top['fast'], 5)) + " seconds. "
            s = '' if pot is None else "Longest time a dek has been free is " + str(round(pot['slow'])) + " seconds. " + \
                                       pot['name'] + " ended that in "+pot_channel+"."
        else:
            with shelve.open(self.directory+target) as records:
                for name in records.keys():
                    rec = records[name]
                    if 'name' not in rec:
                        rec['name'] = name

                    top = rec if top is None and 'fast' in rec or 'fast' in rec and rec['fast'] < top['fast'] else top
                    pot = rec if pot is None and 'slow' in rec or 'slow' in rec and rec['slow'] > pot['slow'] else pot
            f = '' if top is None else "Fastest dekerino is "+top['name']+" with "+str(round(top['fast'],5))+" seconds. "
            s = '' if pot is None else "Longest time a dek has been free is "+str(round(pot['slow']))+" seconds. " + pot['name'] + " ended that."

        self.dek_send(target, f + s)
