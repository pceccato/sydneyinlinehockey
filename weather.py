import urllib2
import json
    
def getWeatherFromWunderground(country, city):

    request = 'http://api.wunderground.com/api/f1de8fe992f2c09c/geolookup/conditions/forecast/q/%s/%s.json' % (country, city) 
    f = urllib2.urlopen(request)
    json_string = f.read()
    f.close()
    parsed_json = json.loads(json_string)
    location = parsed_json['location']['city']    
    # temp_c = parsed_json['current_observation']['temp_c']
    # weather = parsed_json['current_observation']['weather']
    # print "%s. Current temperature in %s is: %s degrees celcius" % (weather, location, temp_c ) 

    return parsed_json
