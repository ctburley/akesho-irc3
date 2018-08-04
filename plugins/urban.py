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
        
    @command(aliases=['u','ud'],options_first=True,use_shlex=False)
    def urban(self, mask, channel, args):
        """Use urban dictionary to look up words or phrases.
            %%urban [<word>...]"""
        (ix, udict, link) = (None, None, False)
        if args['<word>']:
            word = args['<word>']
            link = False
            if word[-1].isdigit():
                ix = int(word[-1])
                word.pop(-1)
            if word[0].lower() == '-link' or word[0].lower() == '-l':
                link = True
                word.pop(0)
            udict = self.lookup(" ".join(word))
        else:
            (ix, udict, link) = (None, self.lookup(), False)
            
        if udict:
            idx = ix if ix else 0
            args = {'word': "{}{}: ".format(udict[idx]['word'],(", "+str(idx) if ix else ""))}
            if link:
                defi = udict[idx]['permalink']
            else:
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
        

