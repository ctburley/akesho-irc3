import irc3, re
from random import choice
from zalgo_text import zalgo

@irc3.plugin
class StringModifier:
    
    TO_SUPER = str.maketrans("abcdefghijklmnoprstuvwxyzABDEGHIJKLMNOPRTUVW0123456789+-=()", "ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻᴬᴮᴰᴱᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᴿᵀᵁⱽᵂ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾")
    HALFWIDTH_TO_FULLWIDTH = str.maketrans(
        '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&()*+,-./:;<=>?@[]^_`{|}~',
        '０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ！゛＃＄％＆（）＊＋、ー。／：；〈＝〉？＠［］＾＿‘｛｜｝～'
    )
    ZALGO = zalgo.zalgo()
    
    def __init__(self, bot):
        self.bot = bot
        self.features = {
            'stripformat':  ['strip(?:f(?:ormat)?)?',       self.stripformat],
            'rainbow':      ['(?:rainbow|rb)',              self.rainbow],
            'wrainbow':     ['(?:wrainbow|wrb)',            self.wrainbow],
            'fullwidth':    ['(?:fw|vapor|aes|fullwidth)',  self.full],
            'uppercase':    ['upper(?:case)?',              self.upper],
            'lowercase':    ['lower(?:case)?',              self.lower],
            'title':        ['title(?:case)?',              self.title],
            'swapcase':     ['sw(?:itch|ap)?(?:case)?',     self.swap],
            'superscript':  ['super(?:script)?',            self.super],
            'reverse':      ['rev(?:erse)?',                self.reverse],
            'dekify':       ['dek(?:ify)?',                 self.dekify],
            'embolden':     ['(?:bold|embolden)',           self.embolden],
            'italicize':    ['ital(?:ic(?:ize)?)?',         self.italicize],
            'underline':    ['under(?:line)?',              self.underline],
            'zalgofy':      ['zalgo(?:i?fy)?',                self.zalgofy],
        }
        
        # compile feature regexps
        for feature in self.features:
            self.features[feature][0] = re.compile('^\s*'+self.features[feature][0]+'\s+(?P<text>.*)\s*$')
        
        print("strmodr ~ loaded".translate(self.HALFWIDTH_TO_FULLWIDTH))
       
    # --- Features
    def help(self, text):
        return "commands available: " + ', '.join(list(self.features.keys()))
        
    def stripformat(self, text):
        return re.sub("[\u0003\u0002\u001F\u001D\u000F](?:,?\d{1,2}(?:,\d{1,2})?)?", '', text)
        
    def rainbow(self, text):
        text = self.stripformat(text)
        return ''.join([u"\x03{:02}{}".format((l%10)+3,text[l]) for l in range(len(text))])
    
    def wrainbow(self, text):
        text = self.stripformat(text)
        return ' '.join([u"\x03{}{}".format(choice(range(10))+3,l) for l in text.split(' ')])
    
    def full(self, text):
        return self.stripformat(text).translate(self.HALFWIDTH_TO_FULLWIDTH)
    
    def upper(self, text):
        return str(text).upper()
            
    def lower(self, text):
        return str(text).lower()
    
    def title(self, text):
        return str(text).title()
        
    def swap(self, text):
        return str(text).swapcase()
    
    def super(self, text):
        return self.stripformat(text).translate(self.TO_SUPER)
            
    def reverse(self, text):
        return self.stripformat(text)[::-1]
    
    def dekify(self, text):
        text = self.stripformat(text)
        u, l = text.upper(), text.lower()
        return ''.join([choice([u[i],l[i]]) for i in range(len(u))])
    
    def embolden(self, text):
        return "\x02"+text
    
    def italicize(self, text):
        return "\x1D"+text
    
    def underline(self, text):
        return "\x1F"+text
    
    def zalgofy(self, text):
        return self.ZALGO.zalgofy(self.stripformat(text))
    # ---  Core
        
    @irc3.event('^(@\S+ )?:(?P<nick>\S+)!\S+@\S+ PRIVMSG (?P<target>\S+) :(?P<datas>.*)$')
    def _core(self, nick, target, datas, **kw):
        if self.bot.obeying_commands(target) and datas[0] == '!':
            text = None
            datas = datas[1:].strip().split('|')
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
                self.bot.privmsg(target, self.bot.np("  ")[1]+text)
    
