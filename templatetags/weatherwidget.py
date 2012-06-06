import urllib
import urllib2
from django import template
from weather import getweather

register = template.Library()

@register.inclusion_tag('google_weather/weather_widget.html')
def google_weather(location, language):
    request = 'http://www.google.com/ig/api?weather=%s&hl=%s' % (location, language)
    xml = unicode(urllib2.urlopen(urllib2.Request(request)).read(), 'ISO-8859-1').encode('utf-8')
    weather_dict = getweather(location,language)   
    return {
        'weather_dict' : weather_dict,
    }