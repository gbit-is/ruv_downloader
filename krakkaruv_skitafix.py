import time
import requests
import json
import dbm
import os
import pathlib
import sys
import configparser
import urllib.request



class colors:


    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strikethrough = '\033[09m'
    invisible = '\033[08m'

    class fg:
        black = '\033[30m'
        red = '\033[31m'
        green = '\033[32m'
        orange = '\033[33m'
        blue = '\033[34m'
        purple = '\033[35m'
        cyan = '\033[36m'
        lightgrey = '\033[37m'
        darkgrey = '\033[90m'
        lightred = '\033[91m'
        lightgreen = '\033[92m'
        yellow = '\033[93m'
        lightblue = '\033[94m'
        pink = '\033[95m'
        lightcyan = '\033[96m'

    class bg:
        black = '\033[40m'
        red = '\033[41m'
        green = '\033[42m'
        orange = '\033[43m'
        blue = '\033[44m'
        purple = '\033[45m'
        cyan = '\033[46m'
        lightgrey = '\033[47m'







script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
dbm_file = script_dir + "/.ruvdata"
config_file = script_dir + "/config.ini"
kvs = dbm.open(dbm_file, 'c')
cache_expiry = 3600


config = configparser.ConfigParser()
config.read(config_file)


COLOR_PRINT = False
PLEXIFY = False
PLEXIFY_CLASHES = False

DEBUG = False
DISABLE_M3U8_OUTPUT = False


if "config" in config:
    if "colors" in config["config"]:
        if config["config"]["colors"].lower() == "true":
            COLOR_PRINT = True
    if "plexify" in config["config"]:
        if config["config"]["plexify"].lower() == "true":
            PLEXIFY = True
    if "plexify_clashes" in config["config"]:
        if config["config"]["plexify_clashes"].lower() == "true":
            PLEXIFY_CLASHES = True

    if "debug" in config["config"]:
        if config["config"]["debug"].lower() == "true":
            DEBUG = True
        elif config["config"]["debug"].lower() == "false":
            DEBUG = False
        else:
            print("!! debug in [config] has an invalid value")

    if "disable_m3u8_output" in config["config"]:

        if config["config"]["disable_m3u8_output"].lower() == "true":
            DISABLE_M3U8_OUTPUT = True
        elif config["config"]["disable_m3u8_output"].lower() == "false":
            DISABLE_M3U8_OUTPUT = False

        else:
            print("!!  disable_m3u8_output in [config] has an invalid value")


if sys.platform in [ "linux", "darwin" ]:
    import shutil
    if "config" in config:
        if "ffmpeg_path" in config["config"]:
            ffmpeg_path = config["config"]["ffmpeg_path"]
            if os.path.isdir(ffmpeg_path):
                #sys.path.append(ffmpeg_path)
                os.environ['PATH'] += ':' + ffmpeg_path
            else:
                print("Error: ffmpeg path defined but is not a directory")
                exit()



    ffmpeg_which = shutil.which("ffmpeg")
    if ffmpeg_which == None:
        print("Error: can not find ffmpeg in path")
        exit()




try:
    import m3u8_To_MP4
except:
    print("Install m3u8_To_MP4")
    print("pip install m3u8_To_MP4")
    exit()


if not DEBUG:
    m3u8_To_MP4.logging.disable()

def pprint(msg):
    try:
        print(json.dumps(msg,indent=2))
    except:
        print(msg)

def debug(msg):
    if DEBUG:
        print(msg)


def colorPrint(status,show,episode,underline=False):

    pad = [ 35, 35, 35 ]

    if COLOR_PRINT:

        if underline:
            ul = colors.underline
        else:
            ul = colors.reset

        if status == "Line":
            print(colors.bg.lightgrey,colors.fg.black,"|".ljust(pad[0],"-"),"|".ljust(pad[1],"-"),"|".ljust(pad[2],"-"),colors.reset)
            return

        rs = colors.reset

        if status == "[Episode already downloaded]":
            bg = colors.bg.blue
            fg = colors.fg.lightgrey
        elif status == "[Downloading episode]":
            bg = colors.bg.green
            fg = colors.fg.black
        elif status == "[Downloaded episode]":
            bg = colors.bg.green
            fg = colors.fg.black
        elif status == "[Not Downloading episode]":
            bg = colors.bg.red
            fg = colors.fg.lightgrey
        elif status == "Status":
            bg = colors.bg.lightgrey
            fg = colors.fg.black
        else:
            bg = colors.bg.black
            fg = colors.fg.orange

        print(ul,bg,fg,status.ljust(pad[0]),show.ljust(pad[1]),episode.ljust(pad[2]),rs)


def fetchShowList():

    #url = "https://api.ruv.is/api/programs/tv/all"


    temp_file = ".tmp_file"

    file_age = os.path.getmtime(temp_file)
    time_now = time.time()

    file_delta = time_now - file_age

    if file_delta > 3600:


        url = "https://pico-server.spilari.ruv.is/programs/featured/krakkaruv"
        response = requests.request("GET", url)


        f = open(temp_file,"wb")
        f.write(response.content)

    x = open(temp_file).read()
    y = json.loads(x)
    pprint(y)



def listShowIds():

    if "showList" not in kvs:
        fetchShowList()


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
        print(id.ljust(showList_pad[0]) + "|" +  title.ljust(showList_pad[1]) + "|" + avail.ljust(showList_pad[2]))

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



def checkIfFileExists(url,directory,filename,friendly_name,plexify,force=False,dryrun=False,underline=False):


    if not os.path.isdir(directory):
        print("Directory: " + directory + " does not exist")
        return

    file_name_mp4 = filename + ".mp4"

    output_file = os.path.join(directory,file_name_mp4)

    dl_msg_pad = 35

    if os.path.isfile(output_file):
        file_exists = True
    else:
        file_exists = False


    if force:
        file_exists = False

    return file_exists

def downloadEpisode(url,directory,filename,friendly_name,plexify,force=False,dryrun=False,underline=False):


    success = True

    if dryrun:
        colorPrint("[Not Downloading episode]",friendly_name[0],friendly_name[1],underline)
    else: 
        if DISABLE_M3U8_OUTPUT:
            colorPrint("[Downloading episode]",friendly_name[0],friendly_name[1],underline)
            sys.stdout = open(os.devnull, 'w')

        try:
            m3u8_To_MP4.multithread_download(url,mp4_file_dir=directory,mp4_file_name=filename)
        except:
            success = False


        if DISABLE_M3U8_OUTPUT:
            sys.stdout = sys.__stdout__
        else:
            colorPrint("[Downloaded episode]",friendly_name[0],friendly_name[1],underline)

    return success

def kvsCheckIfDownloaded(show_id,episode_id):


    if show_id in kvs:
        show_kvs_data = json.loads(kvs[show_id])

        if episode_id in show_kvs_data:
            return True
        else:
            return False

    else:
        return False

def kvsRegisterDownload(show_id,episode_id):

    if show_id in kvs:
        show_kvs_data = json.loads(kvs[show_id])
    else:
        show_kvs_data = { }

    show_kvs_data[episode_id] = True

    kvs[show_id] = json.dumps(show_kvs_data)




def autoDownload():

    force = False
    dryrun = False
    underline = False

    if "autodownload" not in config:
        print("autodownload not configured")
        exit(1)


    colorPrint("Status","Show","Episode")
    colorPrint("Line","","")

    for entry in config["autodownload"]:
        active = config["autodownload"][entry]
        if active.lower() == "true":
            
            entry_config = config[entry]
            show_id = entry_config["show_id"]
            dl_dir = entry_config["dl_dir"]
            path = pathlib.Path(dl_dir)
            path.mkdir(parents=True, exist_ok=True)

            
            show_data = listEpisodes(show_id)
            
            show_name_slug = show_data["slug"]
            show_name = show_data["title"]



            episodes = show_data["episodes"]

            if "plexify" in config[entry]:
                if config[entry]["plexify"].lower() == "true":
                    plexify = True
                else:
                    plexify = False
            else:
                plexify = PLEXIFY

            if "plexify_clashes" in config[entry]:
                if config[entry]["plexify"].lower() == "true":
                    plexify_clashes = True
                else:
                    plexify_clashes = False
            else:
                plexify_clashes = PLEXIFY_CLASHES



            if plexify:

                plex_image_path = os.path.join(dl_dir, "show.jpg")
                if not os.path.isfile(plex_image_path):
                    base_image_url = show_data["image"]
                    image_url_hq = base_image_url.replace("480x","1920x").replace("quality(65)","quality(100)")
                    data = urllib.request.urlretrieve(image_url_hq,plex_image_path)





             
            for episode in episodes:

                episode_name_slug = episode["slug"]
                episode_name = episode["title"]
                episode_url = episode["file"]


                episode_number = episode["number"]


                kvs_show_id = show_name_slug + "-" + show_id
                kvs_episode_id = episode_name_slug


                if plexify_clashes:
                    files_in_dir = os.listdir(dl_dir)


                    for entry in files_in_dir:
                        if episode_name not in entry:
                            if "s01e" + str(episode_number) + " " in entry:
                                episode_number = "1" + str(episode_number)




                friendly_name = [show_name,episode_name]


                if plexify:
                    file_name = show_name + " - s01e" + str(episode_number) + " - " + episode_name

                else:
                    file_name = show_name_slug + "_" + episode_name_slug

                show_downloaded = False


                if kvsCheckIfDownloaded(kvs_show_id,kvs_episode_id):
                    colorPrint("[Episode already downloaded]",friendly_name[0],friendly_name[1],underline)

                elif checkIfFileExists(episode_url,dl_dir,file_name,friendly_name,plexify,force,dryrun,underline):
                    colorPrint("[Episode already downloaded]",friendly_name[0],friendly_name[1],underline)

                    # til að samræma downloads áður en KVS management dótið kom í gagnið
                    kvsRegisterDownload(kvs_show_id,kvs_episode_id)

                else:
                    success = downloadEpisode(episode_url,dl_dir,file_name,friendly_name,plexify,force,dryrun,underline)
                    if success:
                        kvsRegisterDownload(kvs_show_id,kvs_episode_id)
                    
                underline = not underline





def manage_show_kvs(action,show_name="null",episode_name="null"):



    if action == "list_shows":

        for entry in kvs.keys():
            entry = entry.decode()

            if entry == "showList":
                pass
            elif entry.startswith("show_"):
                pass
            else:
                print(entry)

    elif action == "list_episodes":
        if show_name not in kvs:
            print("Show not found in kvs")
        else:
            episode_list = json.loads(kvs[show_name])
            print("KVS entries for show: " + show_name)
            for episode in episode_list:
                print(episode)

    
    elif action == "delete_show":

        if show_name not in kvs:
            print("Show not found in kvs")
        else:
            print("Deleting kvs entries for: " + show_name)
            del kvs[show_name]

    elif action == "delete_episode":
        if show_name not in kvs:
            print("Show not found in kvs")
        else:
            episode_list = json.loads(kvs[show_name])

            if episode_name not in episode_list:
                print("Episode not found in kvs")
            else:
                print("Removing episode: " + episode_name + " from show: " + show_name)
                del episode_list[episode_name]
                kvs[show_name] = json.dumps(episode_list)
        

    elif action == "delete_all":
        for entry in kvs.keys():
            entry = entry.decode()

            if entry == "showList":
                pass
            elif entry.startswith("show_"):
                pass
            else:
                del kvs[entry]



    




def parseArgs():


    help_msg="\n usage is: \n " + sys.argv[0] + " <auto|list|kvs|help> \n\n  list: Lists all show names and their ID \n  auto: downloads files according to config.ini \n\n\n The KVS command manages the list of downloaded files, it only deals with the download records, not the files themselves\n kvs [list_shows|list_episodes|delete_show|delete_episode|delete_all] <show_name> <episode_name>\n  kvs list_shows # lists shows \n  kvs list_episodes {show_name} # lists episodes of a show\n  kvs delete_show {show_name} # Delete all records of a show \n  kvs delete_episode {show_name} {episode_name} # delete the record of a single episode \n  kvs delete_all # .... deletes all records \n\n\n  help: prints this not-great help message\n"

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

    if "kvs" in action.lower():

        kvs_args = { 
            "kvs_action"    :   "none",
            "show_name"     :   "none",
            "episode_name"  :   "none"
        }

        kvs_options = [ "script", "action","kvs_action","show_name","episode_name" ]

        if len(sys.argv) == 2:
            print(help_msg)
            exit()

        arg_counter = 0
        for entry in sys.argv:
            kvs_args[kvs_options[arg_counter]] = entry
            arg_counter += 1



        manage_show_kvs(kvs_args["kvs_action"],kvs_args["show_name"],kvs_args["episode_name"])

        


        exit(0)




    print("Action: " + action + " is not defined")
    print(help_msg)
    exit(1)
    


#if __name__ == '__main__':
     #parseArgs()

fetchShowList()
