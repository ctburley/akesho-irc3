import irc3
from irc3.plugins.command import command
from random import choice

@irc3.plugin
class UserActions:

    def __init__(self, bot):
        self.bot = bot
        self.strings = {}
        self.strings['thanks'] = (
            'you are welcome!',
            'no problem!',
            'do not mention it!',
            'it is my pleasure!',
            'sure thing!',
            'of course!',
            'every time!',
            'how could I not?',
            'happy to help!',
            'beep boop.'
       )

        self.strings['hugs'] = (
            "{nick} wraps {target} with seven hairy arms and squeezes until they look like a koosh toy!",
            "{nick} picks {target} up in a giant bear hug.",
            "{nick} wraps arms around {target} and clings forever",
            "{nick} gives {target} a BIIIIIIIIG hug!!!",
            "{nick} gives {target} a warming hug",
            "{nick} hugs {target} into a coma",
            "{nick} squeezes {target} to death",
            "{nick} gives {target} a christian side hug",
            "{nick} glomps {target}",
            "{nick} gives {target} a well-deserved hug :)",
            "{nick} hugs {target}",
            "{nick} hugs {target} forever and ever and ever",
            "cant stop, wont stop. {nick} hugs {target} until the sun goes cold",
            "{nick} rallies up everyone in the channel to give {target} a group hug",
            "{nick} gives {target} a tight hug and rubs their back",
            "{nick} hugs {target} and gives their hair a sniff",
            "{nick} smothers {target} with a loving hug"            
        )
                            
        print("<3 <3 <3 luv ~ LOADE")
    
    @classmethod
    def reload(cls, old):
        return cls(old.bot)

    @irc3.event(r'(?i)^(@\S+ )?:(?P<nick>\S+)!\S+@\S+ privmsg (?P<channel>\S+) :(?:.+? |)(?:t(?:hank(?:s| you)| ?y(?: ?v ?m)?),? akesho)(?P<luv>(?: *<3)*)?(?: +[^$]*)??$')
    def ty(self, nick=None, channel=None, luv=None, **kw):
        if self.bot.obeying_commands(channel):
            self.bot.privmsg(channel, choice(self.strings['thanks'])+('' if luv is None else ' ' + (' '.join(luv.split()))))
    
    @command
    def hug(self, mask, channel, args):
        """Hug someone!
            %%hug <someone>...
        """
        target = ' '.join(args['<someone>'])
        self.bot.privmsg(channel, "\x01ACTION "+str(choice(self.strings['hugs'])).format(target=target,nick=mask.nick)+"\x01")
        
