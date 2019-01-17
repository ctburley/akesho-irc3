from gsearch.googlesearch import search
import irc3
from irc3.plugins.command import command

@irc3.plugin
class UrbanDict:
    def __init__(self, _bot):
        self.bot = _bot
        print('google search loaded')
        
    @command(aliases=['g'],options_first=True,use_shlex=False)
    def search(self, mask, channel, args):
        """Use google to look up words or phrases.
            %%search [<word>...]"""
        if args['<word>']:
            udict = search(" ".join(args['<word>']))
            if udict:
                udict = udict[0]
                self.bot.privmsg(channel, "\x02{}  \x0F--  {}".format(udict[0],udict[1]))
            else:
                self.bot.privmsg(channel, "Something went wrong?")
        else:
            self.bot.privmsg(channel, "I can't look for nothing!")
            
