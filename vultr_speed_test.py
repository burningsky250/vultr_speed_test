#!/usr/bin/env python

import subprocess
import requests 
import json
import sys
from bs4 import BeautifulSoup
from multiprocessing import Pool


target_url = "https://www.vultr.com/faq/"

def get_geo_link():
    rsp = requests.get(target_url)
    soup = BeautifulSoup(rsp.content)
    geo_map = []
    for elem in soup.select('#speedtest_v4 > tr'):
        all_tds = elem.findAll('td')
        geo_location = all_tds[0].text.strip()
        ping_url = all_tds[2].findAll("a")[0]['href'].strip()
        geo_map.append((geo_location, ping_url))
    return geo_map 

def fmt_speed(speed):
    if speed < 1024:
        return "%s B/s" % speed
    elif speed < 1024*1024:
        return "%s KB/s" % (speed*1.0/1024)
    else:
        return "%s MB/s" % (speed*1.0/1024/1024)

def speed_test(geo_info):
    geo_loc, ping_url = geo_info

    output_format = """{
        "speed": %{speed_download}
    }
    """

    cmd = ["curl", "-w", output_format, "-s", "-o", "/dev/null", "-m", "10", ping_url]
    # print " ".join(cmd)
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].strip()
    # print>>sys.stderr, output
    data = json.loads(output)
    info = (geo_loc, fmt_speed(data["speed"]), data["speed"])
    return info


if __name__ == '__main__':
    geo_map = get_geo_link()
    # pool = Pool(10)
    geo_speed = []
    print "="*10 + "start speed testing..." + "="*10
    for geo_info in geo_map:
        print 
        print "testing [%s] by %s" % (geo_info[0], geo_info[1])
        geo_loc, speedstr, speed = speed_test(geo_info)
        print "speed to [%s] is %s" % (geo_loc, speedstr)
        geo_speed.append((geo_loc, speedstr, speed))
    print "="*10 + "end speed testing..." + "="*10

    print 
    print 
    print
    print "+"*20 + "speed rank" + "+"*20
    geo_speed.sort(key=lambda x: x[2], reverse=True)
    for (geo_loc, speedstr, speed) in geo_speed:
        print "[%s]:%s" % (geo_loc, speedstr)
    print "+"*20 + "end speed rank" + "+"*20

    
    
