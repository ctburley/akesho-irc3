import irc3
from irc3.plugins.command import command
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen


@irc3.plugin
class Scopey:
    def __init__(self, bot):
        self.bot = bot
        self.signs = "aquarius pisces aries taurus gemini cancer leo virgo libra scorpio sagittarius capricorn"
        print("got here")
        self.short = self.scrape_short()
        
    @command
    def horo(self, mask, channel, args):
        """Get horoscope for <sign>
            %%horo <sign>"""
        sign = args['<sign>'].lower()
        if sign in self.signs:
            self.bot.privmsg(channel, "Today's horoscope for {}: {}".format(sign, self.short[sign]))
        else:
            self.bot.privmsg(channel, "Sign must be one of: {}".format(self.signs))
            
    def scrape_short(self):
        soup = BeautifulSoup(
                    urlopen(
                        Request(
                            "https://cafeastrology.com/dailyhoroscopesall.html",
                            headers={'User-Agent': 'Mozilla/5.0'}
                        )
                    ),
                    features="html.parser"
                )
        content = soup.find('div','entry-content')
        read_flag = False
        horos = {}
        cur_horo = None
        last = '.'
        for tag in content:
            if tag.name is not None:
                if read_flag:
                    if tag.name == last:
                        read_flag = False
                    else:
                        if tag.name == 'h4':
                            cur_horo = tag.string.split(' ')[1].lower()
                        if tag.name == 'p':
                            horos[cur_horo] = tag.text
                    last = tag.name
                if tag.string == "Patrick Arundell’s Today’s Horoscopes":
                    read_flag = True
        return horos
