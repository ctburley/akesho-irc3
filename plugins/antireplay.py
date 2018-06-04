import irc3
import fnmatch
#import logging

@irc3.plugin
class AntiReplay:

    def __init__(self, bot):
        self.bot = bot
        self.obeying = {}
        print("Channel Replay Command Blocker - Loaded.")
    
    @irc3.extend
    def obeying_commands(self, channel):
        return channel not in self.obeying
    
    @irc3.event('^:\S+ NOTICE (?P<target>\S+) :Replaying up to \S+ lines of pre-join history spanning up to \S+ seconds')
    def disable_commands(self, target, **kw):
        self.obeying[target] = False
        self.bot.loop.call_later(6, self.reenable_commands, target)
    
    def reenable_commands(self, channel):
        del self.obeying[channel]
        
