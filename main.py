import webapp2
import os
from google.appengine.ext.webapp import template
import weather

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache



class BaseHandler(webapp2.RequestHandler):

    # cache weather as we only get 500 weather requests per day in the free plan!
    def get_weather(self):
        data = memcache.get('weather')
        if data is not None:
            return data
        else:
            data = weather.getWeatherFromWunderground('Australia','Sydney')
            memcache.add('weather', data, 30 * 60) #refresh every half hour
            return data
            
    # override in your class and call base first if you need to add any more template
    # values for your page.
    # every page header needs the news, which is why we do it here
    def get_template_values(self):
        
        user = users.get_current_user()
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>" %
                        users.create_login_url("/"))

        #TODO render this greeting
        template_values = { 'weather_dict' : self.get_weather(),
                            'greeting' : greeting,
                            'user' : user
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
  thumbnail = db.BlobProperty()
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
            
    def rescale(self, img_data, width, height, halign='middle', valign='middle'):
        """Resize then optionally crop a given image.
        
        Attributes:
        img_data: The image data
        width: The desired width
        height: The desired height
        halign: Acts like photoshop's 'Canvas Size' function, horizontally
                aligning the crop to left, middle or right
        valign: Verticallly aligns the crop to top, middle or bottom
        
        """
        image = images.Image(img_data)
        
        desired_wh_ratio = float(width) / float(height)
        wh_ratio = float(image.width) / float(image.height)
        
        if desired_wh_ratio > wh_ratio:
            # resize to width, then crop to height
            image.resize(width=width)
            image.execute_transforms()
            trim_y = (float(image.height - height) / 2) / image.height
            if valign == 'top':
                image.crop(0.0, 0.0, 1.0, 1 - (2 * trim_y))
            elif valign == 'bottom':
                image.crop(0.0, (2 * trim_y), 1.0, 1.0)
            else:
                image.crop(0.0, trim_y, 1.0, 1 - trim_y)
        else:
        # resize to height, then crop to width
            image.resize(height=height)
            image.execute_transforms()
            trim_x = (float(image.width - width) / 2) / image.width
            if halign == 'left':
                image.crop(0.0, 0.0, 1 - (2 * trim_x), 1.0)
            elif halign == 'right':
                image.crop((2 * trim_x), 0.0, 1.0, 1.0)
            else:
                image.crop(trim_x, 0.0, 1 - trim_x, 1.0)
                
        return image.execute_transforms()
            
    def saveAd( self, summary, description, image ):
        """save ad to datastore"""   
        advert = Advert()
        advert.summary = summary
        advert.description = description
        user = users.get_current_user()
        advert.seller = user
        

        if image:
            thumbnail = self.rescale(image, 130, 130)
            #doesn't respect aspect
            #thumbnail = images.resize(image,130,130)
            advert.thumbnail = db.Blob(thumbnail)
            advert.image = db.Blob(image)
            
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

#we could get ride of these handlers if we stored out images in the blobstore
# and used get_serving_url() to generate URLS for them
#
# simply serves the images stored in our adverts
class Image(webapp2.RequestHandler):
    def get(self):
        advert = db.get(self.request.get("img_id"))
        if advert.image:
            self.response.headers['Content-Type'] = "image"
            self.response.out.write(advert.image)
        else:
            self.error(404)  
            
# simply serves the thumbnails stored in our adverts
class Thumb(webapp2.RequestHandler):
    def get(self):
        advert = db.get(self.request.get("img_id"))
        if advert.thumbnail:
            self.response.headers['Content-Type'] = "image"
            self.response.out.write(advert.thumbnail)
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
                                ('/img', Image),
                                ('/thm', Thumb)],
                                debug=True)
