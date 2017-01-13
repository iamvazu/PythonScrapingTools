#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Lord Azu
#
# Created:     11/07/2016
# Copyright:   (c) Lord Azu 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import urllib
import requests
import os
import time
from bs4 import BeautifulSoup
from requests.exceptions import ReadTimeout
import random
import queue

max_depth = 2

class Proxygenerator():

    def __init__(self):
        self.proxy_list = []
        self.proxy_dictionary = dict()
        self.user_agents = []
        #self.generate_euproxy()
        self.generate_usproxy()
        #self.generate_wordldwideproxy()
        agent_file = 'user_agents.txt'
        self.load_user_agents(agent_file)
        self.crawled_list = dict()

        #self.generate_proxy_list_org()


    def store_proxies(self, filename):
        """@params:
        filename:text file to store list"""
        with open(filename, 'w') as out:
            for item in self.proxy_list:
                out.write(item,"\n")


    def generate_usproxy(self):
        """ Add to proxy_list using proxy-list.org"""
        proxylistUrl= "http://www.us-proxy.org/"
        templs = []
        proxies = []
        try:
            print("Grabbing: ",proxylistUrl)
            response = requests.get(proxylistUrl,timeout = 20)
            #html = response.read()
           # print(response.text)
          #  break
            soup = BeautifulSoup(response.text, 'html.parser')
            proxylinks = soup.find('tbody')#.find_all({"role" : "row","class" : "odd"}):
            rows = proxylinks.findAll('tr')
            for tr in rows:
               td = tr.find_all('td')
               ip = td[0].text
               port = td[1].text
               #generate ssl proxies
               if td[4].text is not 'transparent' and td[6].text == r'yes' and ip not in self.proxy_dictionary:

                   self.proxy_list.append(ip + ":" + port)
                   self.proxy_dictionary[ip]=port

        except Exception as e:
            print(e)
            pass
        print(self.proxy_list)
        print(len(self.proxy_list))

    def generate_wordldwideproxy(self):
        """add global proxies to dictionary list"""
        proxylistUrl= 'http://free-proxy-list.net'

        try:
            print("Grabbing: ",proxylistUrl)
            response = requests.get(proxylistUrl,timeout = 20)
            #html = response.read()
           # print(response.text)
          #  break
            soup = BeautifulSoup(response.text, 'html.parser')
            proxylinks = soup.find('tbody')#.find_all({"role" : "row","class" : "odd"}):
            rows = proxylinks.findAll('tr')
            for tr in rows:
               td = tr.find_all('td')
               ip = td[0].text
               port = td[1].text
               #generate ssl proxies
               if td[4].text is not 'transparent' and td[6].text == r'yes' and ip not in self.proxy_dictionary:
                   self.proxy_list.append(ip + ":" + port)
                   self.proxy_dictionary[ip]=port

        except Exception as e:
            print(e)
            pass
        print(self.proxy_list)
        print(len(self.proxy_list))

    def generate_euproxy(self):
        """Add proxies specifically from europe"""
        proxylistUrl= 'http://proxyfor.eu/geo.php'

        try:
            print("Grabbing: ",proxylistUrl)
            response = requests.get(proxylistUrl,timeout = 20)

            soup = BeautifulSoup(response.text, 'html.parser')
            proxylinks = soup.find('table',attrs =  {"class":"proxy_list"})#'tbody')#.find_all({"role" : "row","class" : "odd"}):
            rows = proxylinks.findAll('tr')
            for tr in rows:
               td = tr.find_all('td')
               if len(td)>=6:
                   ip = td[0].text
                   port = td[1].text
                   #generate ssl proxies.High and can have cookies
                   if td[3].text is not 'HIGH' and  r'Yes' not in td[6] and ip not in self.proxy_dictionary:
                       self.proxy_list.append(ip + ":" + port)
                       self.proxy_dictionary[ip] = port

        except Exception as e:
            print(e)
            #print(proxylinks)
            pass
        print(self.proxy_list)

    """ Handle user agents source: doc.ic"""




    def load_user_agents(self, useragentsfile):
        """
        useragentfile : string
            path to text file of user agents, one per line
        """

        with open(useragentsfile, 'rb') as uaf:
            for ua in uaf.readlines():
                if ua:
                    self.user_agents.append(ua.strip()[1:-1-1])
        random.shuffle(self.user_agents)
        return self.user_agents

    def get_random_user_agent(self):
        """
        useragents : string array of different user agents
        :param useragents:
        :return random agent:
        """
        user_agent = random.choice(self.user_agents)
        return user_agent

    def generate_random_request_headers(self):
        headers = {
            "Connection": "close",  # another way to cover tracks
            "User-Agent": self.get_random_user_agent()
        }  # select a random user agent
        return headers

    #add a decorator to retry later
    def proxy_request(self,url,params = {}, req_timeout = 10):
        """generate a request with random headers/ip. returns the request. use the .text function to receive html
        @param url= website url
        params=post/get data
        timeout= seconds until timeout"""

        random.shuffle(self.proxy_list)
        #generate a random request
        req_headers = dict( self.generate_random_request_headers().items())
        request = None
        try:
            rand_proxy = random.choice(self.proxy_list)#get a random ip:port from the proxylist

            request = requests.get(url, proxies={"http": rand_proxy},
                                   headers=req_headers, timeout=req_timeout)
            print(rand_proxy)
        except ConnectionError:
            self.proxy_list.remove(rand_proxy)
            print("invalid connection")

        except ReadTimeout:
            self.proxy_list.remove(rand_proxy)
            print ("Bad timeout")
            pass
        return request

def main():
    pg = Proxygenerator()
    print((pg.proxy_list))

if __name__ == '__main__':
    main()
