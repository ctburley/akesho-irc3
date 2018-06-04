import irc3
import time
from irc3.plugins.command import command
from irc3.plugins.cron import cron
from threading import Timer
import random
import fnmatch
import logging

@irc3.plugin
class Utility:

    def __init__(self, bot):
        self.bot = bot
        self.obey_commands = {}
        print("UTIL ~ LOADE")
    
    #move these into alerts
    @cron('30 1 * * *')
    def med(s):
        options = (
            'Snorlaxian, Oakee or alsooakee, tinysprout, and bkembo: have you taken your meds?',
            'bkembo: have you, tinysprout, Snorlaxian, and Oakee or alsooakee taken your meds?',
            'bEeP BoOp ThIs iS A MeDiCaTIOn rEmInDe FoR  bKeMbO, tInYsPrOuT, sNoRlAxIaN, anD OaKeE oR AlSOoAkEe',
            "Oakee or alsooakee, guee what time it is! That's right! It's medication time! bkembo, Snorlaxian, tell tinysprout what they've won!",
            "If Oakee or alsooakee, Snorlaxian, tinysprout, and bkembo aren't on drugs... they need to be.",)
        s.bot.privmsg('#textfriends', random.choice(options))
    
    @cron('5 1 * * *')
    def medi(cation):
        options = (
            'Snorlaxian, Oakee or alsooakee, tinysprout, and bkembo: have you taken your meds?',
            'bkembo: have you, tinysprout, Snorlaxian, and Oakee or alsooakee taken your meds?',
            'bEeP BoOp ThIs iS A MeDiCaTIOn rEmInDe FoR  bKeMbO, tInYsPrOuT, sNoRlAxIaN, anD OaKeE oR AlSOoAkEe',
            "Oakee or alsooakee, guee what time it is! That's right! It's medication time! bkembo, Snorlaxian, tell tinysprout what they've won!",
            "If Oakee or alsooakee, Snorlaxian, tinysprout, and bkembo aren't on drugs... they need to be.",)
        cation.bot.privmsg('#textfriends', random.choice(options))
    
    
    @cron('00 23 * * *')
    def smed(s):
        s.bot.privmsg('#textfriends', 'Snorlaxian, have you taken your meds?')
    
    @command(permission='admin',show_in_help_list=False)
    def goto(s,m,t,a):
        """Goto another channel
            
            %%goto <channel>
        """
        s.bot.join(a['<channel>'])
    
    @command(permission='admin',show_in_help_list=False)
    def leave(s,m,t,a):
        """Leave this channel
            
            %%leave
        """
        s.bot.part(t)

    @irc3.extend
    def np(self, inp):
        return inp[:1]+u'\u200B'+inp[1:]
    
    @command(permission='owner', show_in_help_list=False)
    def eybdoog(self, mask, target, text):
        """Shut down the bot
            
            %%eybdoog
        """
        self.bot.quit()
        exit()
    
    
class mode_based_policy:
    """Allow only valid masks. Able to take care or permissions. Will not allow commands during first seven seconds after a channel join."""

    def __init__(self, bot):
        self.context = bot
        self.log = logging.getLogger(__name__)
        self.has_permission={
            'user':    lambda mask,t: True,
            'voice':   lambda mask,t: mask.nick in list(self.context.channels[t].modes['+']) or self.levels['hop'](mask,t),
            'hop':     lambda mask,t: mask.nick in list(self.context.channels[t].modes['%']) or self.levels['admin'](mask,t),
            'admin':   lambda mask,t: mask.nick in list(self.context.channels[t].modes['@']) or self.levels['owner'](mask,t),
            'owner':   lambda mask,t: fnmatch.fnmatch(mask, '*@user/ctburley') or mask.nick in list(self.context.channels[t].modes['!'])
        }
        
    def __call__(self, predicates, meth, client, target, args, **kwargs):
        if ( self.context.obeying_commands(target) ):
            if self.has_permission[predicates.get('permission', 'user')](client, target):
                return meth(client, target, args)
            self.log.log("Denying command '{}' requested by '{}' in {}".format(meth.__name__, client.nick, target))
