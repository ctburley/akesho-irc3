import irc3, shelve
from irc3.plugins.command import command
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from irc3.plugins.cron import cron

@irc3.plugin
class Scopey:
    def __init__(self, bot):
        self.bot = bot
        self.signs = "aquarius pisces aries taurus gemini cancer leo virgo libra scorpio sagittarius capricorn"
        self.update()
        self.store = {}
        with shelve.open('data/horos') as pstore:
            for item in pstore:
                self.store[item] = pstore[item]
        print("The Oracle is in.")
                
    @cron("47 2 * * *")
    def update(self):
        self.short = self.scrape_short()
        print(self.short)
        print("horos updates")

    @command(aliases=['hor','horoscope'])
    def horo(self, mask, channel, args):
        """Get horoscope for <sign>
            %%horo [<sign>]"""
        sign = args['<sign>'].lower() if args['<sign>'] else None if mask.lnick not in self.store else self.store[mask.lnick]
        if sign:
            if sign in self.signs:
                self.bot.privmsg(channel, "Today's horoscope for {}: {}".format(sign, self.short[sign]))
                if mask.lnick not in self.store:
                    self.store[mask.lnick] = sign
                    with shelve.open('data/horos') as pstore:
                        pstore[mask.lnick] = sign
            else:
                self.bot.privmsg(channel, "Sign must be one of: {}".format(self.signs))
        else:
            self.bot.privmsg(channel, "Command must be used with a sign at least once.")
            
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
        entry_content = soup.find('div','entry-content')
        pane_container = entry_content.find("div", {"class": "su-tabs-panes"})
        content_panes = pane_container.findAll("div", {"class": "su-tabs-pane"})
        
        horos = {}
        for pane in content_panes:
            bits = pane.findAll()
            horos[bits[0].text.split()[1].lower()] = bits[2].text.split('.')[0]+'. - https://cafeastrology.com/dailyhoroscopesall.html'
        
        return horos
        soup.findAll("div", {"class": "stylelistrow"})
