from flask import Flask, jsonify, request
import re, urllib
import googlesearch
from ordered_set import OrderedSet
app = Flask(__name__)
import logging
logger = logging.getLogger('application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

bannedlist = ["facebook.com",'aclcareers.com',"tripadvisor","trivago",'crunchbase.com', 'zoominfo.com',
        "dailymail","booking.com","yelp.com","slideshare.net","indeed","youtube.com","linkedin.com","justdial.com","twitter.com","rocketreach",
        "bloomberg","www.bayt.com","reachuae.com","zawya.com","instagram.com","soundcloud.com","cutestat.com",
        "en.wikipedia.org","moneycontrol.com","naukri.com","shine.com","in.jora.com","economictimes.indiatimes.com",
        ".glassdoor.","blog.", "portal.","console.","account.","hiring.","careers.","app.","help.","about.","jobs.","get.","news.",
              "newsroom.","investor.","corporate.", "docs.","tor.","bay.","manager.","insights.","media.","member.","community.",
              "wallet.","github.com","angel.co","beta.","login.","forms.","hub.","investors.","guides.","labs.","my.",
              "open.","content."]

def get_value(companyname):
    accurateset = OrderedSet()
    multipleset = OrderedSet()
    try:
        user_agent_str = googlesearch.get_random_user_agent()
        logger.info('google search for %s', companyname) 
        for j in googlesearch.search(companyname, tld="co.in", num=3, stop=3, pause=1, user_agent=user_agent_str):
            #logger.info('google search result %s', companyname) 
            #print(j)
            correct = True
            for item in bannedlist:
                if j.__contains__(item):
                    correct = False
                    break
            if correct:
                try:
                    newstr = re.split("www.", j)[1]
                except IndexError as e:
                    newstr = re.split("//", j)[1]
                finamdomain = re.split("/", newstr)[0]

                if "."==finamdomain[0]:
                    finamdomain.replace(".","",1)

                multipleset.add(finamdomain)

                pattren_str = re.compile(r'([a-z]+)')
                firstname = re.search(pattren_str, companyname.lower()).group(0)

                if firstname in finamdomain:
                    accurateset.add(finamdomain)

    except urllib.error.HTTPError as httperr:
        #print(httperr.headers,httperr.read())  # Dump the headers to see if there's more information
        return {'error':'captcha'}

    data = {'companyname':companyname,'accurate':list(accurateset),'multiple':list(multipleset)}
    return data

@app.route('/getdomain', methods=['GET'])
def get_domain():
     
    companyname = request.args.get('company')
    return jsonify(get_value(companyname))

@app.route('/getdomains', methods=['POST'])
def get_domains():
    companynames = request.json['companies']
    data = {}
    for companyname in companynames:
       data[companyname]=get_value(companyname)
    return jsonify(data)

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
