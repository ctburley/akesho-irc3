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
            ix = int(args['<word>'][-1]) if args['<word>'][-1].isdigit() else None
            udict = self.lookup(" ".join(args['<word>'][0:-1] if ix else args['<word>']))
        else:
            (ix, udict) = (None, self.lookup())
            
        if udict:
            idx = ix if ix else 0
            args = {'word': "{}{}: ".format(udict[idx]['word'],(", "+str(idx) if ix else ""))}
            defi = udict[idx]['definition']
            if defi.lower().startswith(udict[idx]['word'].lower()+":"):
                defi = defi[len(udict[idx]['word'])+1:].strip()
            if (len(defi)+len(args['word'])) > 449:
                args['definition'] = defi[:445-len(args['word'])] + "[...]"
            else:
                args['definition'] = defi
            self.bot.privmsg(channel, "{word}{definition}".format(**args))
    
    def lookup(self, term=None):
        try:
            if term:
                req = urlopen("http://api.urbandictionary.com/v0/define?"+urlencode({'term': term}))
            else:
                req = urlopen("http://api.urbandictionary.com/v0/random")
            return loads(req.read().decode())['list']
        except HTTPError as e:
            return None
        except URLError as e:
            return None
        return None
        

