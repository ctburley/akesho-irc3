from forecastiopy import *

@plugin
class WeatherIRC3:
    def __init__(self, bot):
        self.bot = bot
        self.apikey=self.bot.config.get('weather', {}).get('apikey',None))
        self.toc=lambda x: (x-32)/1.8
        
    @command
    def weather(self, mask, channel, args):
        """Get weather local to <location>
            %%weather <location>..."""
        where = ' '.join(args['<location>'])
        location = self.bot.googlemaps().geocode(where)[0]
        fio = ForecastIO.ForecastIO(dskey,
            'units'=ForecastIO.ForecastIO.UNITS_US,
            'exclude'='minutely,flags',
            'latitude'=location['geometry']['location']['lat'],
            'longitude'=location['geometry']['location']['lng']
        )
        
        data = {
            'location': location['formatted_address'],
            'ftemp': fio.currently['temperature'],
            'ctemp': self.toc(fio.currently['temperature']),
            'humidity': fio.currently['humidity'],
            'hsum': fio.hourly['summary'],
            'dsum': fio.daily['summary'],
            'mwind': fio.currently['windSpeed'],
            'kwind': fio.currently['windSpeed']*1.60934,
            'wbearing': (["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE","S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"])[int(16*(fio.currently['windBearing']/360))],
            'fhigh': fio.daily['data'][0]['temperatureHigh'],
            'flow': fio.daily['data'][0]['temperatureLow'],
            'chigh': self.toc(fio.daily['data'][0]['temperatureHigh']),
            'clow': self.toc(fio.daily['data'][0]['temperatureHigh'])
        }
        output="[{location} - {ftemp:.0f}F/{ctemp:.0f}C {humidity:.0%} {mwind:.0f}MPH/{kwind:.0f}KPH {wbearing}, High: {fhigh:.0f}F/{chigh:.0f}C, Low: {flow:.0f}F/{clow:.0f}C] {hsum} {dsum} - https://darksky.net/poweredby/"
        self.bot.privmsg(channel, output.format(**data))
