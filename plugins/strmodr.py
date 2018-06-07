import irc3, re
from random import choice

@irc3.plugin
class StringModifier:
    
    def __init__(self, bot):
        self.bot = bot
        
        self.TO_SUPER = str.maketrans("abcdefghijklmnoprstuvwxyzABDEGHIJKLMNOPRTUVW0123456789+-=()", "ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻᴬᴮᴰᴱᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᴿᵀᵁⱽᵂ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾")
        self.HALFWIDTH_TO_FULLWIDTH = str.maketrans(
            '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&()*+,-./:;<=>?@[]^_`{|}~',
            '０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ！゛＃＄％＆（）＊＋、ー。／：；〈＝〉？＠［］＾＿‘｛｜｝～'
        )
        
        self.features = {
            'rainbow':   ['(?:rainbow|rb)\s*(?P<text>.*)?',             self.rainbow],
            'wrainbow':  ['(?:wrainbow|wrb)\s*(?P<text>.*)?',           self.wrainbow],
            'fullwidth': ['(?:fw|vapor|aes|fullwidth)\s*(?P<text>.*)?', self.full],
            'uppercase': ['upper(?:case)?\s*(?P<text>.*)?',             self.upper],
            'lowercase': ['lower(?:case)?\s*(?P<text>.*)?',             self.lower],
            'title':     ['title(?:case)?\s*(?P<text>.*)?',             self.title],
            'swapcase':  ['sw(?:itch|ap)?(?:case)?\s*(?P<text>.*)?',    self.swap],
            'super':     ['super(?:script)?\s*(?P<text>.*)?',           self.super],
            'reverse':   ['rev(?:erse)?\s*(?P<text>.*)?',               self.reverse]
        }
        
        # compile feature regexps
        for feature in self.features:
            self.features[feature][0] = re.compile('^\s*'+self.features[feature][0]+'\s*$')
        
        print("strmodr ~ loaded".translate(self.HALFWIDTH_TO_FULLWIDTH))
       
    # --- Features
    def strip(self, text):
        return re.sub("[\u0003\u0002\u001F\u000F](?:,?\d{1,2}(?:,\d{1,2})?)?", '', text)
        
    def rainbow(self, text):
        text = self.strip(text)
        return ''.join([u"\x03{:02},{:02}{}".format((l%10)+3,99,text[l]) for l in range(len(text))])
    
    def wrainbow(self, text):
        text = self.strip(text)
        return ' '.join([u"\x03{},{}{}".format(choice(range(10))+3,99,l) for l in text.split(' ')])
    
    def full(self, text):
        return self.strip(text).translate(self.HALFWIDTH_TO_FULLWIDTH)],
    
    def upper(self, text):
        return str(text).upper()
            
    def lower(self, text):
        return str(text).lower()
    
    def title(self, text):
        return str(text).title()
        
    def swap(self, text):
        return str(text).swapcase()
    
    def super(self, text)
        return self.strip(text).translate(self.TO_SUPER)],
            
    def reverse(self, text):
        return self.strip(text)[::-1]
    
    
    
    # ---  Core
        
    @irc3.event('^(@\S+ )?:(?P<nick>\S+)!\S+@\S+ PRIVMSG (?P<target>\S+) :!(?P<datas>.*)$')
    def _core(self, nick, target, datas, **kw):
        if (self.bot.obeying_commands(target)):
            text = None
            datas = datas.split('|')
            for data in datas:
                for name in self.features:
                    (pattern, func) = self.features[name]
                    result = pattern.match(data)
                    if result:
                        if text is None and result.group('text') is None:
                            self.bot.privmsg(target, "No text to process!")
                            return
                        text = func(result.group('text') if text is None else text)
            if text is not None:
                self.bot.privmsg(target, " "+text)
    
