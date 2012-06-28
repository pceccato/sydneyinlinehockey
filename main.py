import webapp2
import os
from google.appengine.ext.webapp import template
import weather

from google.appengine.ext import db
from google.appengine.api import users




class BaseHandler(webapp2.RequestHandler):

    # override in your class and call base first if you need to add any more template
    # values for your page.
    # every page header needs the news, which is why we do it here
    def get_template_values(self):
        # could use djangos template tags feature instead of
        # explicitly loading the weather from google here and
        # passing it in as an argument to the template
        # en-GB for metric units
        weatherinfo = weather.getweather('Sydney','en-GB')
        user = users.get_current_user()
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>" %
                        users.create_login_url("/"))

        #TODO render this greeting
        template_values = { 'weather_dict' : weatherinfo,
                            'greeting' : greeting
                          }
                          
        return template_values
    

class MainHandler(BaseHandler):
    def get(self):
        self.response.out.write(template.render('templates/index.html', self.get_template_values()))
        
class NewsHandler(BaseHandler):
    def get(self):

        self.response.out.write(template.render('templates/news.html', self.get_template_values()))
        
class LocationHandler(BaseHandler):
    def get(self):
        self.response.out.write(template.render('templates/location.html', self.get_template_values()))
        
class ContactHandler(BaseHandler):
    def get(self):
        self.response.out.write(template.render('templates/contact.html', self.get_template_values()))
        
class GamesHandler(BaseHandler):
    def get(self):
        self.response.out.write(template.render('templates/games.html', self.get_template_values()))
        
class LinksHandler(BaseHandler):
    def get(self):
        self.response.out.write(template.render('templates/links.html', self.get_template_values()))
        
class MailHandler(BaseHandler):
    def get(self):
        self.response.out.write(template.render('templates/maillist.html', self.get_template_values()))

from google.appengine.api import images
   
class Advert(db.Model):
  """Models a for sale entry"""
  seller = db.UserProperty()
  summary = db.StringProperty()
  description  = db.StringProperty(multiline=True)
  image = db.BlobProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  
  
class ShowItemHandler(BaseHandler):
    def get(self):
        template_values = self.get_template_values()
            
        adverts = db.GqlQuery("SELECT * "
                            "FROM Advert "
                            " ORDER BY date DESC")
        template_values['adverts'] = adverts
            
        self.response.out.write(template.render('templates/showitems.html', template_values ))
            
              
class SellItemHandler(BaseHandler):
    def get(self):
        template_values = self.get_template_values()
        user = users.get_current_user()
        if not user:
            # make them login so they can list and add
            self.redirect(users.create_login_url(self.request.uri))
        else:
            template_values['username'] = user.nickname()
            
            adverts = db.GqlQuery("SELECT * FROM Advert WHERE seller=:1 ORDER BY date DESC", user )
            template_values['adverts'] = adverts
            
            self.response.out.write(template.render('templates/sellItem.html', template_values ))
            
    def saveAd( self, summary, description, image ):
        """save ad to datastore"""   
        advert = Advert()
        advert.summary = summary
        advert.description = description
        user = users.get_current_user()
        advert.seller = user
        
        # make a thumbnail
        if image:
            # thumbnail = images.resize(image, 32, 32)
            thumbnail = image
            advert.image = db.Blob(thumbnail)
            
        advert.put()
        return True
    
    def deleteAd(self, ad):
            db.delete(ad)

                
    def post(self):
        ad = self.request.get('deletead')
        summary = self.request.get('summary')
        description = self.request.get('description')
        image = self.request.get('image')
        
        if ad:
            self.deleteAd(ad)           
        else: 
            self.saveAd( summary, description, image )
            
        # is there a better way than hardcoding?
        self.redirect('/sellitem.html')
               
        #self.response.out.write('<html><body>Your Ad:<br>')
        #self.response.out.write(ad)
        #self.response.out.write('<br>')
        #self.response.out.write(summary)
        #self.response.out.write('<br>')
        #self.response.out.write(description)
        #self.response.out.write('</body></html>')

# simply serves the images stored in our adverts
class Image(webapp2.RequestHandler):
    def get(self):
        advert = db.get(self.request.get("img_id"))
        if advert.image:
            self.response.headers['Content-Type'] = "image"
            self.response.out.write(advert.image)
        else:
            self.error(404)         
            
app = webapp2.WSGIApplication(  [('/', MainHandler),
                                ('/news.html', NewsHandler),
                                ('/location.html', LocationHandler),
                                ('/contact.html', ContactHandler),
                                ('/games.html', GamesHandler),
                                ('/index.html', MainHandler),
                                ('/links.html', LinksHandler),
                                 ('/sellitem.html', SellItemHandler),
                                 ('/showitems.html', ShowItemHandler ),
                                ('/maillist.html', MailHandler),
                                ('/img', Image)],
                                debug=True)
