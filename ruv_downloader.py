import time
import requests
import json
import dbm
import os
import sys
import configparser

try:
    import m3u8_To_MP4
except:
    print("Install m3u8_To_MP4")
    print("pip install m3u8_To_MP4")
    exit()








script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
dbm_file = script_dir + "/.ruvdata"
config_file = script_dir + "/config.ini"
kvs = dbm.open(dbm_file, 'c')
cache_expiry = 3600


config = configparser.ConfigParser()
config.read(config_file)

DEBUG = False
#DEBUG = True

def pprint(msg):
    try:
        print(json.dumps(msg,indent=2))
    except:
        print(msg)

def debug(msg):
    if DEBUG:
        print(msg)


def fetchShowList():

    url = "https://api.ruv.is/api/programs/tv/all"
    response = requests.request("GET", url)

    if response.status_code == 200:

        ruv_data = response.json()

        data = { "time" : int(time.time()),
                "data" : ruv_data
                }

        kvs["showList"] = json.dumps(data)
    else:
        print("fetchShowList() unsuccessfull")
        print("http response code was: " + str(response.status_code))
        print("Exiting")
        exit(1)


def listShowIds():

    showList = json.loads(kvs["showList"])
    showList_age = time.time() - showList["time"]

    if showList_age > cache_expiry:
        debug("Showlist is old, fetching new list")
        fetchShowList()
        showList = json.loads(kvs["showList"])
    else:
        debug("Using cached showlist")

    showList_data = showList["data"]

    showList_pad = [ 10, 70, 10 ]

    print("ID".ljust(showList_pad[0]) + "TITLE".ljust(showList_pad[1]) + "AVAIL".ljust(showList_pad[2]))

    for entry in showList_data:
        id = str(entry["id"])
        title = entry["title"]
        avail = str(entry["web_available_episodes"])
        print(id.ljust(showList_pad[0]) + title.ljust(showList_pad[1]) + avail.ljust(showList_pad[2]))

def fetchEpisodeList(show_id):

    show_id = str(show_id)

    #base_url = "https://api.ruv.is/api/programs/get_ids/"
    #url = base_url + show_id

    base_url = "https://api.ruv.is/api/programs/program/SHOW_ID/all"
    url = base_url.replace("SHOW_ID",show_id)

    response = requests.request("GET", url)

    if response.status_code == 200:
        show_data = response.json()

        data = { "time" : int(time.time()),
                 "data" : show_data
        }

        key = "show_" + show_id

        kvs[key] = json.dumps(data)



def listEpisodes(show_id):

    show_id = str(show_id)

    show_kvs_key = "show_" + show_id


    if show_kvs_key in kvs:

        debug("show list exists")
        show_data = json.loads(kvs[show_kvs_key])
        show_list_age = time.time() - show_data["time"]

        if show_list_age > cache_expiry:
            debug("Episode list is old, getting new one")
            fetchEpisodeList(show_id)
            show_data = json.loads(kvs[show_kvs_key])
        else:
            debug("Using cached episode list")

    else:
        debug("Show list does not exist, downloading list")
        fetchEpisodeList(show_id)
        show_data = json.loads(kvs[show_kvs_key])

    
    return show_data["data"]


def downloadIfNotExist(url,directory,filename,friendly_name):

    if not os.path.isdir(directory):
        print("Directory: " + directory + " does not exist")
        return
    if directory.endswith("/"):
        directory = directory[:-1]


    output_file = directory + "/" + filename + ".mp4"

    dl_msg_pad = 35

    if os.path.isfile(output_file):
        print("[Episode already downloaded]".ljust(dl_msg_pad) + friendly_name)
    else:
        #print("Downloading episode")
        m3u8_To_MP4.multithread_download(url,mp4_file_dir=directory,mp4_file_name=filename)
        print("[Downloaded episode]".ljust(dl_msg_pad) + friendly_name)


def autoDownload():

    if "autodownload" not in config:
        print("autodownload not configured")
        exit(1)


    print("Status".ljust(35) + "Show".ljust(25) + "Episode".ljust(30))
    print("|-------------------------------|---------------------|-------------------------|")

    for entry in config["autodownload"]:
        active = config["autodownload"][entry]
        if active.lower() == "true":
            
            entry_config = config[entry]
            show_id = entry_config["show_id"]
            dl_dir = entry_config["dl_dir"]
            
            show_data = listEpisodes(show_id)
            
            show_name_slug = show_data["slug"]
            show_name = show_data["title"]

            episodes = show_data["episodes"]
            for episode in episodes:
                episode_name_slug = episode["slug"]
                episode_name = episode["title"]
                episode_url = episode["file"]

                friendly_name = show_name.ljust(25)  + episode_name.ljust(30)


                file_name = show_name_slug + "_" + episode_name_slug

                downloadIfNotExist(episode_url,dl_dir,file_name,friendly_name)




def parseArgs():

    help_msg="how to use this"

    if len(sys.argv) == 1:
        print(help_msg)
        exit(0)

    if "help" in str(sys.argv).lower():
        print(help_msg)
        exit(0)

    action = sys.argv[1]

    if "auto" in action.lower():
        autoDownload()
        exit(0)

    if "list" in action.lower():
        listShowIds()
        exit(0)

    print("Action: " + action + " is not defined")
    print(help_msg)
    exit(1)
    



parseArgs()

