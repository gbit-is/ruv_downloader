# ruv_downloader

# About
Hugbúnaður til að sjálfvirkt búa til öryggisafrit af þáttum á rúv og save-ar sem mp4
Ath: Ennþá mjög hrátt, ekkert error handling t.d

# Install

Á linux/wsl:

- Install ffmpeg however you want to
- git clone git@github.com:gbit-is/ruv_downloader.git
- cd ruv_downloader
- python3 -m venv ./venv
- source venv/bin/activate
- pip install requests
- pip install m3u8_To_MP4

Á windows:
..... nota wsl bara ?

# How to use

./ruv_downloader.py list  
Skilar lista af ID's á þáttum og nafni þáttana

./ruv_downloader.py auto
les config.ini skjalið, lúppar gegnum configured þætti, athugar hvort það sé búið að downloada þeim og downloadar þeim ef ekki

-- config.ini skjalið

downloaderinn les [autodownload] kaflann, þar býrðu til "objects" og merkir þau sem True ef þú vilt downloada þeim (getur sett í False eða hvaða annan streng sem er til þess að disable-a það download án þess að eyða skilgreiningunni

fyrir hvert object í [autodownload] kaflanum gerirðu nýjan kafla, sem vísar í show_id (tekið úr ./ruv_downloader.py list) og hvar á að save-a skjölin.

held að config.ini_example sé nokkuð solid 

# Stuff sem ég bæti kannski við, ef ég nenni
.... eða eins og sumir kalla "to do"

- Ekki nota file.exists til að ákveða hvort skjal skuli vera downloadað eða ekki, það er núþegar persistant kvs í forritinu, nota það svo það sé hægt að rename-a skjöl án þess að enda með multiples
- hafa eitthvað error handling
- gera basic search function fyrir þætti
- breyta path handling úr string cat yfir í os.path.join functions 




  
