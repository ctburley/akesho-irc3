import irc3
from irc3.plugins.command import command

@irc3.plugin
class TMPlugin:

    def __init__(self, bot):
        self.bot = bot

    @command(use_shlex=False)
    def tm(self, mask, channel, args):
        """Makes Stuff Happen™
            %%tm [<stuff>...]"""
        self.bot.privmsg(channel, ' '.join(args['<stuff>']).title() + '™')

