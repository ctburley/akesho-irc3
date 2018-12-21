import irc3
import googlemaps

@irc3.plugin
class Googlemaps_IRC3:
    def __init__(self, bot):
        self.bot = bot
        self.client = googlemaps.Client(key=self.bot.config.get('googlemaps', {}).get('apikey',None))
    
    #for now just make function to retrieve the client to make calls on from within other bot plugins
    @irc3.extend
    def googlemaps(self):
        return self.client
    
    @irc3.extend
    def gmap_geocode(self, location):
        return self.client.geocode(location)
