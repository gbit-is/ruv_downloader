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

Ef þú ert t.d á mac og ert ekki með ffmpeg í path, þá geturðu búið til [config][ffmpeg_path] til þess að taka fram ffmpeg pathinn og honum er bætt við í os.path 

downloaderinn les [autodownload] kaflann, þar býrðu til "objects" og merkir þau sem True ef þú vilt downloada þeim (getur sett í False eða hvaða annan streng sem er til þess að disable-a það download án þess að eyða skilgreiningunni

fyrir hvert object í [autodownload] kaflanum gerirðu nýjan kafla, sem vísar í show_id (tekið úr ./ruv_downloader.py list) og hvar á að save-a skjölin.
Einnig er hægt að taka fram "plexify", sem að downloadar þá "poster" mynd af þættinum í show.jpg svo að plex sýni þáttinn fallega og gerir filename "${SERÍA} -  S01E${EPISODE} - ${EPISODE_NAME}" 

Rúv api-inn er ekkert æðislegur, stundum er sami þáttur á 2 mismunandi ID's og þættir geta haft kolröng númer (númer hvað þátturinn er í seríunni), til að koma til móts við það bætti ég við "plexify_clash" og þá í staðinn fyrir að eiga 2 þætti sem eru báður "s01e12" þá verður annar þeirra "s01e112", þarf að bæta þessa logík ...... 


held að config.ini_example sé nokkuð solid base fyrir flesta

# Stuff sem ég bæti kannski við, ef ég nenni
.... eða eins og sumir kalla "to do"

- Ekki nota file.exists til að ákveða hvort skjal skuli vera downloadað eða ekki, það er núþegar persistant kvs í forritinu, nota það svo það sé hægt að rename-a skjöl án þess að enda með multiples
- hafa eitthvað error handling
- gera basic search function fyrir þætti
- breyta path handling úr string cat yfir í os.path.join functions 


# Credits:
Hefði aldrei nennt að henda þessu saman ef ég hefði ekki haft hinn fínt kommentaða kóða [ruvsarpur](https://github.com/sverrirs/ruvsarpur) eftir [sverrirs](https://github.com/sverrirs) til að renna yfir og byggja API köllin á 

  
