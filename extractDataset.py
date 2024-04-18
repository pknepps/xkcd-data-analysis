import json;
import urllib.request

with urllib.request.urlopen("https://xkcd.com/info.0.json",) as request:
    current_comic_json = request.read()
current_comic = json.loads(current_comic_json)
MAX_COMIC = current_comic['num']

attributes = ["num", "year", "month", "day", "title", "safe_title", "transcript", "alt", 
              "img", "link", "news"]


csv = open("xkcd.csv", "w", encoding="utf-8")
for i in attributes:
    csv.write(i + ", ")
csv.write("extra_parts\n")

for i in range(1, MAX_COMIC + 1):
    if (i == 404):
        print(i)
        continue 
    noSuccess = True
    while(noSuccess):
        try:
            with urllib.request.urlopen("https://xkcd.com/" + str(i) + "/info.0.json") as request:
                comic_json = request.read()
            noSuccess = False
        except KeyboardInterrupt:
            exit(1)
        except:
            print("error, retrying..")
    comic = json.loads(comic_json)
    for attr in attributes:
        if (isinstance(comic[attr], str)):
            if (comic[attr] == ""):
                comic[attr] = "NA"
            else:
                comic[attr] = '"' + comic[attr].replace("\n", "\\n").replace('"', "\"").replace(",", "(COMMA)") + '"'
        csv.write(str(comic[attr]) + ", ")
    csv.write(("NA" if "extra_parts" not in comic else str(next(iter(comic["extra_parts"])))) + "\n")
    print(str(comic["num"]))

csv.close()