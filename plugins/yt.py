import irc3
from irc3.plugins.command import command

@irc3.plugin
class Plugin:
  def __init__(self, bot):
    self.bot = bot
    print("yt loaded")

  @irc3.event('^(@(?P<tags>\S+) )?:(?P<nick>\S+)(?P<mask>!\S+@\S+) PRIVMSG (?P<channel>\S+) :\.yt\s+(?P<target>.*?)$')
  def yt(self, nick=None, mask=None, channel=None, target=None, **kw):
    if self.bot.obeying_commands(channel):
      target = target.strip()
      self.bot.privmsg(channel, "Hey " + nick + " .yt isn't working right now, try '.gse youtube "+target+"' instead! <3")
