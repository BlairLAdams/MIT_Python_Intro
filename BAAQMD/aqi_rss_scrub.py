import urllib2
import xml.etree.ElementTree as ElementTree
import dateutil.parser as parser
import time
import datetime
 
aqi_url = 'http://www.baaqmd.gov/Feeds/AirForecastRSS.aspx'
forecasts_raw = urllib2.urlopen(aqi_url).read()
aqi_root = ElementTree.fromstring(forecasts_raw)
 
northern = 'Northern Zone'
coastal = 'Coastal Zone'
eastern = 'Eastern Zone'
central = 'South Central Bay Zone'
southern = 'Southern Zone'
 
pretty_name = {
    'North Counties': northern,
    'Coast and Central Bay': coastal,
    'Eastern District': eastern,
    'South and Central Bay': central,
    'Santa Clara Valley': southern,
}
 
date_text = aqi_root[0][4].text
iso_date = (parser.parse(date_text))
dates = date_text.split()
day = dates[0].split(',')[0]
month = dates[1]
day = dates[2]
year = (time.strftime("%Y"))
date_string = month + "-" + day + "-" + year
date = datetime.datetime.strptime(date_string, '%B-%d-%Y').date()
 
print '''<rss version="2.0">
    <channel>
        <title>Bay Area Air Quality Management District Air Quality Forecast</title>
        <link>http://www.baaqmd.gov</link>
        <language>en</language>
        <lastUpdated>''' + iso_date.isoformat() + '</lastUpdated>'
i = 0
items = aqi_root.findall('.//item')
for item in items:  
    descriptions = item.findall('./description')
    for description in descriptions:
        description_text = description.text
        lines = iter(description.text.split('\n'))
        next_date = date + datetime.timedelta(days = i)
        short_date = datetime.datetime.strptime(str(next_date), '%Y-%m-%d').strftime('%x')
        print '\t<item>'
        print '\t\t<date>' + short_date + '</date>'
        next(lines)
        for line in lines:
            name = line.split('-')[0].rstrip(' ')
            aqi = line.split('AQI: ')[1].split(',')[0]
            pollutant = line.split('Pollutant: ')[1].rstrip('.').title()
            print '\t\t<zone>'
            if name in pretty_name:
                print '\t\t\t<title>' + pretty_name[name] + '</title>'
            print '\t\t\t<measurement>' + aqi + '</measurement>'
            print '\t\t\t<pollutant>' + pollutant + '</pollutant>\n\t\t</zone>'
        print '\t</item>'
    i += 1
print '\t</channel>\n</rss>'