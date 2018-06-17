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
            "{nick} hugs {target} into a coma xP",
            "{nick} squeezes {target} like they were an avocado...",
            "{nick} pulls {target} into a tight, friendly shoulder hug.",
            "{nick} runs at and tackles {target} into a pile of pillows, hugging them in a rain of feathers!",
            "{nick} gives {target} a very friendly hug :)",
            "{nick} hugs {target}!",
            "{nick} hugs {target} forever and ever and ever~ and ever~ <3",
            "With a hug so tight it could create a quantum singularity, {nick} embraces {target} until the sun goes cold.",
            "{nick} rallies up everyone in the channel to give {target} a group hug",
            "{nick} dances happily, holding {target} in a tight hug!",
            "{nick} jumps at {target} and growls like a tiger, then bites their arm saying, 'mouf hug', through their teeth.",
            "{nick} smothers {target} with a loving hug."
        )
        
        self.strings['snuggles'] = (
            "Finding themselves without a blanket, {nick} grabs {target} and curls up to get warm.",
            "Roses are red, {nick} learned to juggle. Will that impress {target} enough to snuggle?",
            "A snuggly {nick} reaches out and grabs an arm, pulling {target} in for additional heat.",
            "Holding {target} tight, a content {nick} ponders the evils of a world without snuggling...",
            "{nick} asks {target} whose turn it is to be the big spoon?",
            "{nick} lays their head on {target}'s shoulder and sighs happily.",
            "Without a care in the world, {nick} snuggles back up with {target}."
        )
        
        self.strings['gifts'] = (
            "{nick} carefully crafts a gift for {target} out of pipe cleaners and cooked macaroni.",
            "Lacking the essential pipe cleaners, {nick} cooks a delicious macaroni birthday dinner for {target}.",
            "{nick} wraps a boxin silver paper and ties it with red string for {target}.",
            "A box appears before {target}! They open it and are showered with love and money and a note. Opening the note it reads, 'wishing you the best, love {nick}!'.",
            "{nick} bakes a three tier cake for {target} and sends them flowers at work.",
            "{nick} sings a birthday song for {target} and dances around wearing a rainbow ghillie suit.",
            "{nick} hires a singing telegram to rickroll {target} and wish them a happy birthday!",
            "{nick} orders a pizza and calls {target} over to celebrate!",
            "{nick} gives {target} a bag from 7-11 full of magazines and packs of gum and a mix-cd of trucker songs.",
            "{nick} blows the work dust off their project and presents {target} with a life sized replica of Benedict Cumberbatch with the mouth cut out.",
            "{nick} builds a birthday pie special for {target}.",
            "{nick} puts another candle on {target}'s cake for good luck.",
            "{nick} pulls {target} aside to wish them happy birthday privately. ;)",
            "Jumping out from behind a door {nick} surprises {target} with a gift certificate for a massage.",
            "{nick} pulls out a wad of cash and hands it to {target} saying, 'We all know what this is for'."
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
        self.bot.privmsg(channel, " *** "+str(choice(self.strings['hugs'])).format(target=target,nick=mask.nick))
    
    @command
    def snuggle(self, mask, channel, args):
        """Snuggle someone!
            %%snuggle <someone>...
        """
        target = ' '.join(args['<someone>'])
        self.bot.privmsg(channel, " *** "+str(choice(self.strings['snuggles'])).format(target=target,nick=mask.nick))
    
    @command
    def birthday(self, mask, channel, args):
        """Celebrate someone's life!
            %%birthday <someone>...
        """
        target = ' '.join(args['<someone>'])
        self.bot.privmsg(channel, " *** "+str(choice(self.strings['gifts'])).format(target=target,nick=mask.nick))
