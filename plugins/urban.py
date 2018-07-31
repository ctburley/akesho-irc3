from json import loads
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import irc3
from irc3.plugins.command import command

@irc3.plugin
class UrbanDict:
    def __init__(self, _bot):
        self.bot = _bot
        print('urban dict loaded')
        
    @command(aliases=['u','ud'])
    def urban(self, mask, channel, args):
        """Use urban dictionary to look up words or phrases.
            %%urban [<word>...]"""
        if args['<word>']:
            idx = args['<word>'][-1] if args['<word>'][-1].isdigit() else None
            udict = self.lookup(" ".join(args['<word>'][0:-1] if idx else args['<word>']))
        else:
            (idx, udict) = (None, self.random())
            
        if udict:
            idx = idx if idx and idx < len(udict) else None
            self.bot.privmsg(channel, "{word}: {definition}".format(**{'word': udict[int(idx if idx else 0)]['word'], 'definition': udict[int(idx if idx else 0)]['definition'][:400]}))
    
    def random(self):
        try:
            req = urlopen("http://api.urbandictionary.com/v0/random")
            return loads(req.read().decode())['list']
        except HTTPError as e:
            return None
        except URLError as e:
            return None
        return None
        
    def lookup(self, term):
        try:
            req = urlopen("http://api.urbandictionary.com/v0/define?"+urlencode({'term': term}))
            return loads(req.read().decode())['list']
        except HTTPError as e:
            return None
        except URLError as e:
            return None
        return None
    
