from bs4 import BeautifulSoup
from urllib2 import urlopen
from time import sleep
import sqlite3 as lite
import json

BASE_URL = "http://www.chicagoreader.com"
DB = 'best-of.db'

# connect to sqlite

con = None

con = lite.connect(DB)


def make_soup(url):
   html = urlopen(url).read()
   # maybe use HTML5 parser instead?
   return BeautifulSoup(html, 'lxml')

def get_category_links(section_url):
    soup = make_soup(section_url)
    boccat = soup.find('dl', 'boccat')
    category_links = [BASE_URL + dd.a['href'] for dd in boccat.findAll('dd')]
    print 'success'
    return category_links

def get_category_winner(category_url):
    soup = make_soup(category_url)
    print 'soup!'
    category = soup.find('h1', 'headline').string
    # purge nasty Unicode characters with encode('ascii', 'ignore')
    winner = [h2.string.encode('ascii', 'ignore') for h2 in soup.findAll('h2', 'boc1')]
    runners_up = [h2.string.encode('ascii', 'ignore') for h2 in soup.findAll('h2', 'boc2')]
    return {'category': category,
            'category_url': category_url,
            'winner': winner,
            'runners_up': runners_up
            }
       
if __name__ == '__main__':
    food_and_drink = ('http://www.chicagoreader.com/chicago/'
                        'best-of-chicago-2011-food-drink/BestOf?oid=4106228')

    categories = get_category_links(food_and_drink)

    limit = 0
    data = []
    for category in categories:

        winner = get_category_winner(category)
        data.append(winner)
        # limit += 1
        # if limit == 1: # be kind to poor print media site!
        #     break
        sleep(1) # be kind to poor print media site!


    # print data
    with con:
        cur = con.cursor()
        cur.execute('DROP TABLE IF EXISTS bestof')
        cur.execute(''' CREATE TABLE bestof
                        (id integer primary key autoincrement, category text, winner text, runners_up text)

            ''')
        # cur.execute('insert into bestof values (?,?,?)', [data['category'], data['winner'], data['runners_up']])

        for item in data:
            category = item['category'].strip()
            print "Category: {0}\n\n".format(category)
            run_ups = json.dumps(item['runners_up'])
            index = 1
            for restaurant in item['runners_up']:
                run_up = json.dumps(restaurant.strip())
                print "Runner Up #{0}: {1}".format(index, restaurant)
                index += 1
            winner = item['winner'][0].strip()
            print "\nWINNER: {0}".format(winner)
            cur.execute('insert into bestof (category, winner, runners_up) values(?,?,?)',
                [category, winner, run_ups])



