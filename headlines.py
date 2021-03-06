import datetime
import feedparser
import json
import urllib2
import urllib

from flask import Flask, render_template, request, make_response

app = Flask(__name__)


RSS_FEEDS = {'bbc':'http://feeds.bbci.co.uk/news/rss.xml',
	    'cnn':'http://rss.cnn.com/rss/edition.rss',
	    'fox':'http://feeds.foxnews.com/foxnews/latest',
	    'iol':'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication':'bbc',
             'city':'Asuncion,PY',
             'currency_from':'GBP',
             'currency_to':'USD'     
           }

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=ca9fc36ec5a528f44fdd64d03ba422a3"
CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=42a70c11cb134ddea6999e5325c66f21"

# WEBSITE ROOT
@app.route("/")
def home():
    # get customized headlines, based on user inpit or default
    publication = get_value_with_fallback('publication')

    articles = get_news(publication)

    # get customized weather based on user input or default
    city = get_value_with_fallback('city')
    
    weather = get_weather(city)

    # get customized currency based on user input or default
    currency_from = get_value_with_fallback("currency_from")
    
    currency_to = get_value_with_fallback("currency_to")

    rate, currencies = get_rate(currency_from, currency_to)
    
    # save cookies and return template
    response = make_response(render_template("homepro.html", articles=articles,weather=weather,
                                        currency_from=currency_from, 
                                        currency_to=currency_to, 
                                        rate=rate,
                                        currencies=sorted(currencies)))
    
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)    


    return response
# FUNCTIONS

#FALLBACK
def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)

    return DEFAULTS[key]

#RSS_FEEDS
def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = "bbc"
    else:
        publication = query.lower()
    
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']

#OPENWEATHERMAP
def get_weather(query):
    query = urllib.quote(query)
    url = WEATHER_URL.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {'description':parsed['weather'][0]['description'],
                   'temperature':parsed['main']['temp'],
                    'city':parsed['name'],
                    'country': parsed['sys']['country']
                  }
    return weather

# OPENEXCHANGERATES
def get_rate(frm, to):
    all_currency = urllib2.urlopen(CURRENCY_URL).read()
    
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    
    return (to_rate/frm_rate, parsed.keys())





if __name__ == "__main__":
    app.run()

