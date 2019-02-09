import irc3
from irc3.plugins.command import command

@irc3.plugin
class TMPlugin:

    def __init__(self, bot):
        self.bot = bot

    @command(use_shlex=False)
    def touch(self, mask, channel, args):
        """Makes Stuff Happen
            %%touch [<stuff>...]"""
        self.bot.privmsg(channel, '༼ つ ◕_◕ ༽つ'+self.bot.chain('super '+' '.join(args['<stuff>'])))

