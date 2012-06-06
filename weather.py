import xml.dom.minidom
from google.appengine.api import urlfetch

def weathertodict(xmlstring):
    doc = xml.dom.minidom.parseString(xmlstring)
    return elementtodict(doc.documentElement)

def elementtodict(parent):
    
    # get first child
    child = parent.firstChild
    
    if (not child):
        return None
    
    elif (child.hasAttribute('data')):
        
        # convert tags and data attributes to dictionary
        v = {}
        while child:
            v.update({child.tagName : child.getAttribute('data')})
            child = child.nextSibling
        return v
    
    d={}
    while child:
        
        if (child.nodeType == xml.dom.minidom.Node.ELEMENT_NODE):
            
            # create or extend entry with tag name
            try:
                d[child.tagName]
            except KeyError:
                d[child.tagName]=[]
            
            # append node values, recursive call
            d[child.tagName].append(elementtodict(child))
        
        # select next sibling
        child = child.nextSibling
            
    return d
    
def getweather( location, language ):

        request = 'http://www.google.com/ig/api?weather=%s&hl=%s' % (location, language)
        
        result = urlfetch.fetch(request)
        xml = unicode(result.content, 'ISO-8859-1').encode('utf-8')

        weather_dict = weathertodict(xml)
        weather = weather_dict.get('weather')[0]

  
        return weather
