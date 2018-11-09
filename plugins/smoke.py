import math, shelve
import time
import irc3
import googlemaps
from irc3.plugins.cron import cron
from irc3.utils import IrcString
from datetime import datetime
from datetime import timedelta
from random import randint, choice
from threading import Timer
from irc3.plugins.command import command


class Circle:
    def __init__(self, bot, channel, smoker):
        self.bot = bot
        self.channel = channel
        self.smokers = [smoker]
        self.wait = False
        self.waited = False
        self.timer = None
        self.over = False
        self.current_timer = None
    
    def reply(self, line):
        self.bot.privmsg(self.channel, line, True)

    def reply_action(self, line):
        self.reply("\x01ACTION " + line + "\x01")
    
    def add_smoker(self, smoker):
        if smoker not in self.smokers:
            self.smokers.append(smoker)
    
    def is_in(self, smoker):
        return smoker in self.smokers
    
    def countdown(self):
        self.bot.loop.call_later(1, self.reply, "2..")
        self.bot.loop.call_later(2, self.reply, "1..")
        self.bot.loop.call_later(3, self.reply, "Fire in the bowl!")
        self.over = True

@irc3.plugin
class Plugin:

    def __init__(self, bot):
        self.bot = bot
        self.circles = {}
        self.tz_load()
        print("SMOKE ~ loaded 420 blaze it")

    def reset(self, channel):
        self.circles.pop(channel, None)

    @command
    def iwish(self, mask, channel, args):
        """Get a virtual bowl loaded for you so you can join the round.
            
            %%iwish
        """
        self.sendAction(channel, "packs a bowl for " + mask.nick)

    @command
    def wait(self, mask, channel, args):
        """Gives you another 30 seconds, works only once while in a round.
            
            %%wait
        """
        if channel in self.circles:
            if self.circles[channel].wait:
                self.sendMessage(channel, "We have waited long enough, there is always next round!")
                return
            self.circles[channel].wait = True
            self.circles[channel].reply("Hold up, " + mask.nick + " needs some more time.")
        
    
    @command(use_shlex=False)
    def ambush(self, mask, channel, args):
        """Start the countdown early.
            
            %%ambush [<etc>...]
        """
        if channel in self.circles:
            if self.circles[channel].over:
                self.sendMessage(channel, "Last round was less than two minutes ago, go ahead and hit it!")
                return
            else:
                self.circles[channel].current_timer.cancel()
                if not self.circles[channel].is_in(mask.nick):
                    self.circles[channel].add_smoker(mask.nick)
                self.circles[channel].reply(mask.nick + " started the countdown early, grab your piece!")
        else:
            self.circles[channel] = Circle(self.bot, channel, mask.nick)
            self.sendMessage(channel, mask.nick + " is ambushing the channel! Does that piece have a hit left?")
        
        self.countdown(channel)


    def countdown(self, channel):
        self.circles[channel].countdown()
        self.circles[channel].current_timer = self.bot.loop.call_later(120, self.reset, channel)

    @command
    def whosin(self, mask, channel, args):
        """Check who is already in the round
            
            %%whosin
        """
        reply = "Nobody yet, what about you?"
        if channel in self.circles:
            smokers = self.circles[channel].smokers
            reply = "The round was started by " + smokers[0] + "."
            if len(smokers) == 2:
                reply += " Also smoking is " + smokers[1] + "."
            if len(smokers) > 2:
                reply += " Also smoking are " + ', '.join(smokers[1:-1]) + ', and ' + smokers[-1] +"."
        self.sendMessage(channel, reply)

    @command(aliases=['i','in','im'],use_shlex=False)
    def imin(self, mask, channel, args):
        """Join the round, optional arguments allow you to use the command in the beginning of a sentence.
            
            %%imin [<optional>...]
        """
        if channel in self.circles:
            if self.circles[channel].over:
                self.sendMessage(channel, "Last round was less than two minutes ago, go ahead and hit it!")
                return
                
            if self.circles[channel].is_in(mask.nick):
                self.sendMessage(channel, "You are already in!")
            else:
                self.circles[channel].add_smoker(mask.nick)
                self.circles[channel].reply(mask.nick + " is in!")
        else:
            # Round has not begun, start it
            self.getin(mask, channel, args)


    def warn10Second(self, channel):
        if channel in self.circles:
            if self.circles[channel].wait and not self.circles[channel].waited:
                self.circles[channel].waited = True
                self.circles[channel].current_timer = self.bot.loop.call_later(150, self.warn20Second, channel)
                return
    
            # Warn the channel
            self.circles[channel].reply("Ten seconds, grab your lighter.")
            self.circles[channel].waited = True
            self.circles[channel].current_timer = self.bot.loop.call_later(7, self.countdown, channel)

    def warn20Second(self, channel):
        if channel in self.circles:
            if self.circles[channel].wait and not self.circles[channel].waited:
                self.circles[channel].waited = True
                self.circles[channel].current_timer = self.bot.loop.call_later(160, self.warn20Second, channel)
                return
            
            self.circles[channel].reply("Twenty seconds, is that bowl packed yet?");
            self.circles[channel].current_timer = self.bot.loop.call_later(10, self.warn10Second, channel)


    @command
    def getin(self, mask, channel, args):
        """Start a round. 
            
            %%getin
        """
        if channel in self.circles:
            if self.circles[channel].over:
                self.circles[channel].reply("Last round was less than two minutes ago, go ahead and hit it!")
            else:
                if not self.circles[channel].is_in(mask.nick):
                    self.imin(mask, channel, args)
            return
        self.circles[channel] = Circle(self.bot, channel, mask.nick)
        self.circles[channel].reply(mask.nick + " is ready to burn one, who else is in?")
        self.circles[channel].current_timer = self.bot.loop.call_later(4*60, self.warn20Second, channel)
        
    def sendMessage(self, channel, text):
        print('smoke~~~ ' + text)
        self.bot.privmsg(channel, text, True)

    def sendAction(self, channel, text):
        self.sendMessage(channel, "\x01ACTION " + text + "\x01")
        
        
        
        
        
        
        
        
        ##  420 in locations code
    def tz_load(self):
        self.music_text = " ♫ Don't forget to turn your music back on! ♬ "
        self.music_last = datetime.utcnow() - timedelta(hours=1)
        self.store = Store20(self.bot, './data/smoke')
        self.announce_to = self.bot.config.get('smoke', {}).get('announce', '')
        
    @command(permission='admin')
    def del420(self, nick, target, args):
        """Remove a location from the 420 announcements
            %%del420 <location>
        """
        if self.store.remove(args['<location>']):
            self.bot.privmsg(nick.nick, 'Ok.')
    
    @command(permission='admin')
    def add420(self, mask, target, args):
        """Add a location to the 420 announcements
            %%add420 <location>...
        """
        where = ' '.join(args['<location>'])
        if self.store.add(where, mask.nick):
            self.bot.privmsg(mask.nick, 'Ok.')
            
    @command(permission='admin')
    def rename420(self, mask, target, args):
        """Rename a 420 location
            %%rename420 <pid> <newname>...
        """
        if self.store.rename(args['<pid>'], ' '.join(args['<newname>'])):
            self.bot.privmsg(mask.nick, 'Ok.')
            
    @command
    def list420(self, mask, target, args):
        """PM you a list of active time zones, the locations respresented under them, and who added them.
            %%list420
            %%list420 [-o] pid <pid>
            %%list420 [-o] name <name>
            -o  output to channel
        """
        to = target if args['-o'] and mask.nick in list(self.bot.channels[target].modes['@']) else mask.nick
        
        if args['pid']:
            lines = self.store.list(pid=args['<pid>'])
        else:
            if args['name']:
                lines = self.store.list(name=args['<name>'])
            else:
                lines = self.store.list()
        if len(lines) > 1:
            if len(lines) == 2:
                self.bot.privmsg(to, lines[1], True)
            else:
                for line in lines:
                    self.bot.privmsg(to, line, True)
    
    @cron('15 16 * * *')
    def my420(self):
        #self.lock420 = self.announce_to
        #self.current[self.announce_to].cancel()
        self.bot.privmsg(self.announce_to, choice(['Oh!','Ooo!','Whoops!','Hmm? Ah..']))
        self.bot.loop.call_later(7,self.bot.privmsg, self.announce_to, "\x01ACTION gets "+choice(['up.','up to get something.','something.','ready.','excited.'])+"\x01")
        #if not self.smoking(self.announce_to):
        #    if choice(['a','b','c','d']) == 'c':
        #        self.bot.loop.call_later(32, self.bot.privmsg, self.announce_to, "!getin")
        #        self.bot.loop.call_later(37, self.bot.privmsg, self.announce_to, "Oh yeah, that's me...")
        #else:
        #    self.bot.loop.call_later(33, self.bot.privmsg, self.announce_to, "Oh, ok.")
        #    self.bot.loop.call_later((4*60)+40, self.warn20Second, self.announce_to)
        #    self.bot.loop.call_later(37, self.bot.privmsg, self.announce_to, "There we go.")
        #self.bot.loop.call_later(40, self.imin, IrcString(self.bot.nick+'!user@host'), self.announce_to, [])
        self.bot.loop.call_later(5*61, self.bot.privmsg, self.announce_to, "\x01ACTION "+choice(['hits it!','tokes.','knocks the bong over! :(','gets faded...','shrieks "ACHE SHAW" at the top of their lungs and hits the bong like a madperson!'])+"\x01")
        
    @cron('*/5 * * * *')
    def check420(self):
        offsets = self.store.get_next()
        now = datetime.utcnow()
        if offsets:
            zones = {'AM':[],'PM':[]}
            for offset in offsets:
                time = now + timedelta(seconds=offset)
                for pid in self.store.offset[offset]:
                    zone = self.store.location[pid]['name'] if 'altname' not in self.store.location[pid] else self.store.location[pid]['altname']
                    ap = 'AM' if time.hour < 12 else 'PM'
                    if zone not in zones[ap]:
                        zones[ap].append(zone)
            zone_text = ''.join(sorted([("  {}: {}".format(z, ', '.join(zones[z])) if len(zones[z]) > 0  else '') for z in zones]))
            delta = timedelta(minutes=(20-time.minute)-1,seconds=(60-time.second))
            (self.music_last, mt) = (now, self.music_text) if now-self.music_last > timedelta(minutes=50) else (self.music_last, '')
            self.bot.loop.call_later(delta.seconds, self.bot.privmsg, self.announce_to, 'Happy 4:20!'+zone_text+'! ')
        if now-self.store.last_update > timedelta(24):
            self.store.update()

class Store20:
    def __init__(self, bot, tzfile):
        self.bot = bot
        self.tzfile = tzfile
        self.location = {}
        self.offset = {}
        self.load()
        
    def save(self):
        with shelve.open(self.tzfile) as tzos:
            tzos['locations'] = self.location
            tzos['since'] = self.last_update
            
    def load(self):
        with shelve.open(self.tzfile) as tzos:
            self.last_update = datetime.utcnow()
            self.location = tzos['locations'] if 'locations' in tzos else {}
        self.update()
        print("Store20 Loaded.")
        
        
    def update(self):
        self.offset = {}
        for pid in self.location:
            self.location[pid]['timezone'] = self.bot.googlemaps().timezone(self.location[pid]['geocode']['geometry']['location'])
            offset = self.location[pid]['timezone']['rawOffset']+self.location[pid]['timezone']['dstOffset']
            if offset not in self.offset:
                self.offset[offset] = []
            self.offset[offset].append(pid)
        self.last_update = datetime.utcnow()
        print('Time Zone Offsets Updated')
        
    def get_next(self):
        now = datetime.utcnow()
        offsets = []
        for offset in self.offset:
            time = now + timedelta(seconds=offset)
            if time.hour%12 == 4:
                if 15 <= time.minute < 20:
                    offsets.append(offset)
        return offsets if len(offsets) else None

    def list(self, pid=None, name=None):
        lines = []
        line = "[UTC {:<+5.1f}] {:30} {:30} added by {:20} {}"
        lines.append("[UTC {}] {:30} {:30} added by {:20} {}".format('Offset','Time Zone','Location','Nick','Delete ID'))
        name = name.lower() if name else ''
        if pid:
            if pid in self.location:
                loc = self.location[pid]
                return [line.format((loc['timezone']['rawOffset'] + loc['timezone']['dstOffset'])/(60*60), loc['timezone']['timeZoneId'], "'{}'".format(loc['name'] if 'altname' not in loc else loc['altname']), loc['by'], pid)]
        for offset in sorted(self.offset.keys()):
            for pid in self.offset[offset]:
                loc = self.location[pid]
                if name in loc['name'].lower() or ('altname' in loc and name in loc['altname'].lower()):
                    lines.append(line.format(offset/(60*60), loc['timezone']['timeZoneId'], "'{}'".format(loc['name'] if 'altname' not in loc else loc['altname']+'*'), loc['by'], pid))
        return lines
        
    def add(self, name, by):
        geocode = self.bot.googlemaps().geocode(name)
        if geocode:
            geocode = geocode[0]
            timezone = self.bot.googlemaps().timezone(geocode['geometry']['location'])
            offset = timezone['rawOffset']+timezone['dstOffset']
            self.location[geocode['place_id']] = {'by':by, 'name':name,'geocode':geocode,'timezone':timezone}
            if offset not in self.offset:
                self.offset[offset] = []
            self.offset[offset].append(geocode['place_id'])
            print("Location added: "+geocode['place_id'])
            self.save()
            return True
        return False
    
    def rename(self, pid, newname):
        if pid in self.location:
            self.location[pid]['altname'] = newname
            self.save()
            return True
        return False
        
    def remove(self, place_id):
        if place_id in self.location:
            del self.location[place_id]
            print("Location removed: "+place_id)
            self.save()
            self.update()
            return True
        return False
