#!/usr/bin/env python

import pycurl
import time
import datetime
import sys
import getopt
from pymongo import Connection

# Return google properties from tl.cfg configuration file
def load_google_properties():
    import ConfigParser
    
    config = ConfigParser.ConfigParser()
    try:
        config.read('tl.cfg')
        url = config.get('google', 'url')
        api_key = config.get('google', 'api_key')
        return (url, api_key)
    except Exception, e:
        print "ERROR: An error occurred when reading tl.cfg google configuration: "+e
        sys.exit(2)

# Return mongodb connection properties from tl.cfg configuration file
def load_mongodb_properties():
    import ConfigParser
    
    config = ConfigParser.ConfigParser()
    try:
        config.read('tl.cfg')
        host = config.get('mongodb', 'host')
        port = int(config.get('mongodb', 'port'))
        user = config.get('mongodb', 'user')
        password = config.get('mongodb','password')
        data_collection = config.get('mongodb','data_collection')
        station_collection = config.get('mongodb','station_collection')
        crawled_time_collection = config.get('mongodb','crawled_time_collection')
        return (host,port,user,password,data_collection,station_collection,crawled_time_collection)
    except Exception, e:
        print "ERROR: An error occurred when reading tl.cfg mongodb configuration: "+e
        sys.exit(2)
        
# Output path properties from tl.cfg configuration file
def load_output_properties():
    import ConfigParser
    
    config = ConfigParser.ConfigParser()
    try:
        config.read('tl.cfg')
        video_output_path = config.get('output', 'video_output_path')
        image_output_path = config.get('output', 'image_output_path')
        return (video_output_path,image_output_path)
    except Exception, e:
        print "ERROR: An error occurred when reading tl.cfg mongodb configuration: "+e
        sys.exit(2)

# Script help screen
def print_script_help():
    print ''
    print 'main.py <parameters>'
    print '   <Mandatory parameters>'
    print '     -b: bike system.                    Example: bicing'
    print '     -o: City coordinates.               Example: 41.405,2.185593'
    print '     -s: Timelapse start time.           Example: 20130601-00:00'
    print '     -e: Timelapse end time.             Example: 20130731-23:59'
    print ''
    print '   <Optional parameters>'
    print '     -z: Map zoom.                       Default: 12'
    print '     -g: Granularity.                    Default: 12'
    print '     -r: Timelapse resolution.           Default: 1024x768'
    print '     -t: Time in seconds between images. Default: 1'
    print '     -m: Station set.                    Default: all'
    print ''
    print '  example: main.py -b bicing -o 41.405,2.185593 -s 20130601-00:00 -e 20130731-23:59 -t 2'
    print ''    

# Parsing arguments
def main(argv):
    global bike_system
    global city_coordinates
    global tl_starttime
    global tl_endtime
    global granularity
    global resolution
    global zoom
    global gap_time
    global station_set
    bike_system = ''
    city_coordinates = ''
    tl_starttime = ''
    tl_endtime = ''
    granularity = 12
    resolution = '1024x768'
    zoom = 12
    gap_time = 1
    station_set = []

    
    try:
        opts, args = getopt.getopt(argv,"hmgzrtb:o:s:e:")
    except getopt.GetoptError:
        print 'ERROR: Please, check help for mandatory parameters' 
        print_script_help()
        sys.exit(2)

# TO-DO . Control input errors    
    for opt, arg in opts:
        if opt == '-h':
            print_script_help()
            sys.exit()
        elif opt == '-b':
            bike_system = arg
        elif opt == '-o':
            city_coordinates = arg
        elif opt == '-s':
            tl_starttime = time.mktime(datetime.datetime.strptime(arg, "%Y%m%d-%H:%M").timetuple())
        elif opt == '-e':
            tl_endtime = time.mktime(datetime.datetime.strptime(arg, "%Y%m%d-%H:%M").timetuple())
        elif opt == '-g':
            granularity = arg
        elif opt == '-r':
            resolution = arg
        elif opt == '-z':
            zoom = arg
        elif opt == '-t':
            gap_time = arg
        elif opt == '-m':
            station_set = arg

# Function to increase startime for recursive function parameter
def increase_tl_starttine(increment):
    global tl_starttime
    tl_starttime += increment
    
def get_pictures_from_range():
    print ""
    host,port,user,password,data_collection,station_collection,crawled_time_collection = load_mongodb_properties()
    
    try:
        connection = Connection(host,port)
        db = connection[bike_system]
        # Collection to store crawled data is "data"
        collection = db[data_collection]
        st_collection = db[station_collection]
        partial_time = tl_starttime + ((60/granularity)*60)
        cursor = collection.find({ "t": { "$gte": datetime.datetime.fromtimestamp(tl_starttime), "$lt": datetime.datetime.fromtimestamp(partial_time) }})
        if cursor.count() == 0:
                print "ERROR: No crawled data in the specified time range"
                sys.exit(2)
        else:
                marker_list = []
                for station in cursor:
                    # http://maps.googleapis.com/maps/api/staticmap?center=63.259591,-144.667969&zoom=6&size=400x400\
                    #        &markers=color:blue%7Clabel:S%7C62.107733,-145.541936&markers=size:tiny%7Ccolor:green%7CDelta+Junction,AK\
                    #        &markers=size:mid%7Ccolor:0xFFFF00%7Clabel:C%7CTok,AK&sensor=false" />
                    # Each station_mark is a marker in the map
                    station_coordinates = st_collection.find({ "id": station['s'] },{ "location":1 }).limit(1)
                    print station_coordinates['lon']
                    print station['s']
                # Call API to generate image
 
    except Exception, e:
        print "ERROR: An error occurred when connecting to MongoDB"
        sys.exit(2)
    finally:
        connection.close()
        # Increase recursive function parameter
        increase_tl_starttine((60/granularity)*60)

def generate_animation():
    while tl_starttime < tl_endtime:
        get_pictures_from_range() 

if __name__ == '__main__':
    # Call to retrieve arguments
    main(sys.argv[1:])
    
    # Generate animation
    generate_animation()
    
    
    
    
