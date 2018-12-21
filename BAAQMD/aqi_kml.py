# Required libraries
import urllib2
import xml.etree.ElementTree as ElementTree
import datetime
from zipfile import ZipFile, ZIP_DEFLATED
from jinja2 import FileSystemLoader, Environment
 
# File naming declarations
# Constants named in all caps
TABLE_TEMPLATE_FILENAME = 'aqi_color_table.html'
AQI_TABLE_OUTPUT_FILE_PREFIX = 'aqi_table_'
KMZ_FILENAME = 'BAAQMD.kmz'
AQI_OUTPUT_FILE_PREFIX = 'aqi_'
OBS_OUTPUT_FILE_PREFIX = 'obs_'
STA_OUTPUT_FILE_PREFIX = 'sta_'
 
# URL declarations
AQI_RSS_FEED_URL = 'http://www.baaqmd.gov/Feeds/AirForecastRSS.aspx'
OBS_RSS_FEED_URL = 'http://www.baaqmd.gov/Feeds/OpenBurnRSS.aspx'
STA_RSS_FEED_URL = 'http://www.baaqmd.gov/Feeds/AlertRSS.aspx'
 
# Output file names for Air Quality Index Zones
SOUTHERN = 'aqi_south'
SOUTH_CENTRAL = 'aqi_south_central'
NORTHERN = 'aqi_north'
EASTERN = 'aqi_east'
CENTRAL = 'aqi_coast'
 
# Output file names for Open Burn Status zones
OBS_SOUTH = 'obz_south'
OBS_COAST = 'obz_coast'
OBS_NORTH = 'obz_north'
 
# List of Open Burn Status file name variables
OBS_NAMES = [OBS_SOUTH, OBS_COAST, OBS_NORTH]
 
# Open Burn Status attribute value declarations
OBS_NO_ALERT_FLAG = 'Burn Allowed'
STA_NO_ALERT_FLAG = 'No Alert'
 
# Air Quality Index attribute value declarations
GOOD = 'Good'
MODERATE = 'Moderate'
UNHEALTHY_SENSITIVE = 'Unhealthy for Sensitive Groups'
UNHEALTHY = 'Unhealthy'
VERY_UNHEALTHY = 'Very Unhealthy'
 
# Air Quality Index attribute range value declarations
GOOD_MAX = 51
MODERATE_MAX = 101
UNHEALTHY_SENSITIVE_MAX = 151
UNHEALTHY_MAX = 201
 
# Open Burn Zone alert color declarations
ALERT_COLOR = 'bf3300CC'
BLANK_COLOR = '00000000'
 
# Date format declarations for air quality and open burn
# obs date format applies to sta as well
AQI_FULL_DATE_FORMAT = '%A, %B %d at %H:%M %p'
OBS_FULL_DATE_FORMAT = '%A, %B %d, %Y %H:%M'
 
# Air Quality Index attribute KML map style dictionary declarations
# kml hex colors unlike web (inverted)
AQI_COLOR_MAP = {
    GOOD: 'bf669900',
    MODERATE: 'bf33deff',
    UNHEALTHY_SENSITIVE: 'bf3399ff',
    UNHEALTHY: 'bf3300CC',
    VERY_UNHEALTHY: 'bf990066',
}
 
# Air Quality Index attribute HTML table style dictionary declarations
# regular web hex values
TABLE_AQI_COLOR_MAP = {
    GOOD: '#009966',
    MODERATE: '#FFDE33',
    UNHEALTHY_SENSITIVE: '#FF9933',
    UNHEALTHY: '#CC0033',
    VERY_UNHEALTHY: '#660099',
}
 
# Air Quality Index map zone name dictionary declarations
NAME_MAP = {
    'North Counties': NORTHERN,
    'Coast and Central Bay': CENTRAL,
    'Eastern District': EASTERN,
    'South and Central Bay': SOUTH_CENTRAL,
    'Santa Clara Valley': SOUTHERN,
}
 
# Function definition, essentially calls the functions required to do all the processing
def main():
    full_kml_str = get_full_kml_str()
    build_aqi_files(full_kml_str)
    build_obs_files(full_kml_str)
    build_sta_files(full_kml_str)
 
# Function to unzip the KMZ file and read in the data
def get_full_kml_str():
    full_kmz = ZipFile(KMZ_FILENAME, 'r')
    return full_kmz.read('BAAQMD.kml', 'r')
 
# Function to check to parse KML string and write out HTML table
def build_aqi_files(full_kml_str=None):
    if full_kml_str == None:
        full_kml_str = get_full_kml_str()
 
# Dictionary of dictionaries, for jinja elegance
    zone_table_data = {}
    for name in NAME_MAP:
        zone_table_data[name] = {
            'name': name,
            'aqis': [],
            'pollutants': [],
        }
# Dictionary passed into jinja
    table_data = {
      'start_date': '',
      'zones': [],
      'days': []
    }
 
# Declare and assign RSS root and last build date tag contents
    aqi_forecast_root = get_rss_root(AQI_RSS_FEED_URL)
    last_build_date = get_last_build_date(aqi_forecast_root)
 
# Grabs date from RSS and iterates through to build 5 forecast dates
# Assumes last build date is first day of 5-day forecast
    table_data['start_date'] = last_build_date.strftime(AQI_FULL_DATE_FORMAT)
    table_start_date = last_build_date
    for i in range(5):
        next_day = last_build_date + datetime.timedelta(days=i)
        table_data['days'].append(next_day.strftime('%a'))
 
# Reset colors for each new day of forecast
    items = aqi_forecast_root.findall('.//item')
    for item in items:
        color_map = {
            NORTHERN: BLANK_COLOR,
            CENTRAL: BLANK_COLOR,
            EASTERN: BLANK_COLOR,
            SOUTH_CENTRAL: BLANK_COLOR,
            SOUTHERN: BLANK_COLOR,
        }
# Find AQI RSS title section and loops through to assign title
# Also used as name for KMZ layer
        name_text = ''
        names = item.findall('./title')
        for name in names:
            name_text = name.text
 
# Find AQI RSS description sections and assign lines for parsing
        descriptions = item.findall('./description')
        for description in descriptions:
            lines = description.text.split('\n')
# Split line to find names
            for line in lines:
                name = line.split(' -')[0]
                aqi = ''
                pollutant = ''
# Split out pollutant and aqi values and shave off last punctuation mark                
                if len(line.split('Pollutant: ')) > 1:
                    pollutant = line.split('Pollutant: ')[1].split('. ')[0].rstrip('.')
                if len(line.split('AQI: ')) > 1:
                    aqi = line.split('AQI: ')[1].split(',')[0]
                    table_aqi = aqi
# Test aqi values to determine category name
                    try:
                        aqi = int(aqi)
                        if aqi < GOOD_MAX:
                            aqi = GOOD
                        elif aqi < MODERATE_MAX:
                            aqi = MODERATE
                        elif aqi < UNHEALTHY_SENSITIVE_MAX:
                            aqi = UNHEALTHY_SENSITIVE
                        elif aqi < UNHEALTHY_MAX:
                            aqi = UNHEALTHY
                        else:
                            aqi = VERY_UNHEALTHY
                    except ValueError:
## AQI string value represented in HTML as single letter - double check on this to make sure it's true for all status
                        table_aqi = table_aqi[0]
## Prevents script from exploding, rather carries on to next line because we know it's a numeric value which is valid
                        pass
# Build the dictionaries to pass to jinja
# For each day build the values dictionaries for AQI and Pollutant data
                if name in zone_table_data:
                    zone_table_data[name]['aqis'].append({
                        'aqi': table_aqi,
                        'color': TABLE_AQI_COLOR_MAP[aqi]
                    })
                    zone_table_data[name]['pollutants'].append(pollutant)
                if name in NAME_MAP and aqi in AQI_COLOR_MAP:
                    color_map[NAME_MAP[name]] = AQI_COLOR_MAP[aqi]
# ElementTree requires namespace definition hence long URL strings       
        full_kml = ElementTree.fromstring(full_kml_str)
        folders = full_kml.findall(".//{http://www.opengis.net/kml/2.2}Folder[{http://www.opengis.net/kml/2.2}name='Air Quality Index']")
        for folder in folders:
            styles = full_kml.findall('.//{http://www.opengis.net/kml/2.2}Style') + full_kml.findall('.//{http://www.opengis.net/kml/2.2}StyleMap')
            zones = folder.findall("./{http://www.opengis.net/kml/2.2}Folder") + folder.findall("./{http://www.opengis.net/kml/2.2}Placemark")
# Creating elements for new kmz
            new_kml = ElementTree.Element('{http://www.opengis.net/kml/2.2}kml')
            document = ElementTree.SubElement(new_kml, '{http://www.opengis.net/kml/2.2}Document')
            style_container = ElementTree.Element('{http://www.opengis.net/kml/2.2}Document')
            name_element = ElementTree.SubElement(document, '{http://www.opengis.net/kml/2.2}name')
            name_element.text = name_text
# Pull universe of styles from kml file and load them into a list
           for style in styles:
                style_container.append(style)
# Iterate over zone nodes to setup new features
# Get names assign color
            for zone in zones:
                document.append(zone)
                names = zone.findall('./{http://www.opengis.net/kml/2.2}name')
                zone_name = ''
                for kml_zone_name in names:
                    zone_name = kml_zone_name.text
                if zone_name in color_map:
                    in_use_styles = update_polystyles_recursive(zone, style_container, color_map[zone_name])
                    for style in in_use_styles:
                        document.append(style)
# Write out updated file
            output_kmz_file(new_kml, AQI_OUTPUT_FILE_PREFIX, last_build_date)
            last_build_date = last_build_date + datetime.timedelta(days=1)
# Transform dictionary of dictionaries into list
    for name in zone_table_data:
        table_data['zones'].append(zone_table_data[name])
# Jinja logic and pythin IO
    template_env = Environment(loader=FileSystemLoader(searchpath=""))
    template = template_env.get_template(TABLE_TEMPLATE_FILENAME)
    table_content = template.render(table_data)
    table_output = open(AQI_TABLE_OUTPUT_FILE_PREFIX + table_start_date.strftime('%m%d%Y') + '.html', 'w')
    table_output.truncate()
    table_output.write(table_content)
    
# Function that accepts KML string and writes out Open Burn Status files RSS mashup
# Similar logic to build_aqi_files - see comments there
def build_obs_files(full_kml_str):
    if full_kml_str == None:
        full_kml_str = get_full_kml_str()
 
    obs_forecast_root = get_rss_root(OBS_RSS_FEED_URL)
    last_build_date = get_last_build_date(obs_forecast_root, OBS_FULL_DATE_FORMAT)
 
    items = obs_forecast_root.findall('.//item')
    for item in items:
        name_text = ''
        names = item.findall('./title')
        for name in names:
            name_text = name.text
 
        descriptions = item.findall('./description')
        for description in descriptions:
            north_desc = description.text.strip().lstrip('North: ').split('South: ')[0].strip()
            south_desc = description.text.strip().lstrip('North: ').split('South: ')[1].split('Coastal: ')[0].strip()
            coastal_desc = description.text.strip().lstrip('North: ').split('South: ')[1].split('Coastal: ')[1].strip()
           
        full_kml = ElementTree.fromstring(full_kml_str)
        folders = full_kml.findall(".//{http://www.opengis.net/kml/2.2}Folder[{http://www.opengis.net/kml/2.2}name='Open Burn Zones']")
        for folder in folders:
            styles = full_kml.findall('.//{http://www.opengis.net/kml/2.2}Style') + full_kml.findall('.//{http://www.opengis.net/kml/2.2}StyleMap')
            obs_zones = folder.findall("./{http://www.opengis.net/kml/2.2}Placemark")
 
            new_kml = ElementTree.Element('{http://www.opengis.net/kml/2.2}kml')
            document = ElementTree.SubElement(new_kml, '{http://www.opengis.net/kml/2.2}Document')
            style_container = ElementTree.Element('{http://www.opengis.net/kml/2.2}Document')
            name_element = ElementTree.SubElement(document, '{http://www.opengis.net/kml/2.2}name')
            name_element.text = name_text
 
            for style in styles:
                style_container.append(style)
 
            for zone in obs_zones:
                document.append(zone)
                names = zone.findall('./{http://www.opengis.net/kml/2.2}name')
                zone_name = ''
                for kml_zone_name in names:
                    zone_name = kml_zone_name.text
               
                if zone_name in OBS_NAMES:
                    if zone_name == OBS_NORTH:
                        zone_desc = north_desc
                    elif zone_name == OBS_SOUTH:
                        zone_desc = south_desc
                    else:
                        zone_desc = coastal_desc
                    color = ALERT_COLOR
                    if zone_desc == OBS_NO_ALERT_FLAG:
                        color = BLANK_COLOR
 
                    in_use_styles = update_polystyles_recursive(zone, style_container, color)
                    for style in in_use_styles:
                        document.append(style)
 
            output_kmz_file(new_kml, OBS_OUTPUT_FILE_PREFIX, last_build_date)
            last_build_date = last_build_date + datetime.timedelta(days=1)
 
# Function that accepts KML string and write out spare the air files RSS mashup
# Similar logic to build_aqi_files - see comments there
def build_sta_files(full_kml_str):
    if full_kml_str == None:
        full_kml_str = get_full_kml_str()
 
    sta_forecast_root = get_rss_root(STA_RSS_FEED_URL)
    last_build_date = get_last_build_date(sta_forecast_root, OBS_FULL_DATE_FORMAT)
 
    items = sta_forecast_root.findall('.//item')
    for item in items:
        name_text = ''
        names = item.findall('./title')
        for name in names:
            name_text = name.text
 
        description_text = ''
        descriptions = item.findall('./description')
        for description in descriptions:
            description_text = description.text.strip()
        color = ALERT_COLOR
        if description_text == STA_NO_ALERT_FLAG:
            color = BLANK_COLOR
       
        full_kml = ElementTree.fromstring(full_kml_str)
        district_documents = full_kml.findall(".//{http://www.opengis.net/kml/2.2}Document[{http://www.opengis.net/kml/2.2}name='District Boundary']")
        for district_document in district_documents:
            styles = full_kml.findall('.//{http://www.opengis.net/kml/2.2}Style') + full_kml.findall('.//{http://www.opengis.net/kml/2.2}StyleMap')
            features = district_document.findall(".//{http://www.opengis.net/kml/2.2}Placemark")
 
            new_kml = ElementTree.Element('{http://www.opengis.net/kml/2.2}kml')
            document = ElementTree.SubElement(new_kml, '{http://www.opengis.net/kml/2.2}Document')
            style_container = ElementTree.Element('{http://www.opengis.net/kml/2.2}Document')
            name_element = ElementTree.SubElement(document, '{http://www.opengis.net/kml/2.2}name')
            name_element.text = name_text
 
            for style in styles:
                style_container.append(style)
 
            for feature in features:
                document.append(feature)
                in_use_styles = update_polystyles_recursive(feature, style_container, color)
                for style in in_use_styles:
                    document.append(style)
 
            output_kmz_file(new_kml, STA_OUTPUT_FILE_PREFIX, last_build_date)
            last_build_date = last_build_date + datetime.timedelta(days=1)
 
# Write out and name files
def output_kmz_file(kml, prefix, datestamp):
    date_string = datestamp.strftime('%m%d%Y')
    output_kmz_file = ZipFile(prefix + date_string + '.kmz', 'w', ZIP_DEFLATED)
    output_kmz_file.writestr('doc.kml', ElementTree.tostring(kml))
 
# Get URL and returns elementTree elements
def get_rss_root(url):
    rss_raw = urllib2.urlopen(url).read()
    return ElementTree.fromstring(rss_raw)
 
#   
def get_last_build_date(rss_root, format=AQI_FULL_DATE_FORMAT):
    build_dates = rss_root.findall('.//lastBuildDate')
    last_build_date = datetime.datetime.now()
    for build_date in build_dates:
        year = last_build_date.year
        last_build_date = datetime.datetime.strptime(build_date.text, format)
        last_build_date = last_build_date.replace(year=year)
    return last_build_date
# Recursive function to dig down through nodes to return styles as a list
def update_polystyles_recursive(node, root, new_color, in_use_styles=[]):
    styleUrls = node.findall('.//{http://www.opengis.net/kml/2.2}styleUrl')
    for styleUrl in styleUrls:
        styles = root.findall(".//*[@id='" + styleUrl.text.split('#')[1] + "']")
        for style in styles:
            in_use_styles.append(style)
            if style.tag == '{http://www.opengis.net/kml/2.2}StyleMap':
                update_polystyles_recursive(style, root, new_color, in_use_styles)
            else:
                polystyles = style.findall('.//{http://www.opengis.net/kml/2.2}PolyStyle')
                for polystyle in polystyles:
                    colors = polystyle.findall('./{http://www.opengis.net/kml/2.2}color')
                    for color in colors:
                        color.text = new_color
    return in_use_styles
 
# convention used to allow this script to be called as a library rather than run from top to bottom
# dunder
if __name__ == "__main__":
    main()