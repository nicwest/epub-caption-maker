import epub
import os
from PIL import Image, ImageFont, ImageDraw
import StringIO
import math
import re

target_file = "D:\CLIENTS\Random House\_CONVERSIONS\howbrit\New/final.epub"
image_output_dir = "D:\CLIENTS\Random House\_CONVERSIONS\howbrit\New/bakedcaptions"
font_size = 20
fontdir = "C:/Windows/Fonts/"
italicfont = "Bitter-Italic.otf"
regularfont = "Bitter-Regular.otf"
fontcolor = '#36250b'

default_x = 600
default_y = 800

data = []

with epub.epubFile(target_file) as pew:
    #pew.info.findIDreferences(r"(page[0-9]*)")
    imagefinder = re.compile("<div class=\"image\">[\s]*<img alt=\"\" class=\"image-fix\"( height=\"[0-9]*\")? src=\"(.*?)\"( width=\"[0-9]*\")? />[\s]*<p class=\"caption\">(.*?)</p>[\s]*</div>")
    for spine_item in pew.info.opf.spine:
        contents = spine_item.read()
        for match in re.finditer(imagefinder, contents):
            proto_data = {
                            "src": None,
                             "caption": None,
                             "location": spine_item.opfRelLoc,
                             "item": None,
                             "match": None,
                             "x": None,
                             "y": None,
                             "on_x": None,
                             "on_y": None,
                             "landscape": False,
                             "ratio": None
                        }
            proto_data["src"] = match.group(2)
            if match.group(1):
                proto_data["on_y"] = int(re.search("\"(.*?)\"", match.group(1)).group(1))
            if match.group(3):
                proto_data["on_x"] = int(re.search("\"(.*?)\"", match.group(3)).group(1))
            proto_data["caption"] = match.group(4)
            proto_data["match"] = match.group(0)
            data.append(proto_data)

    for member in data:
        member["item"] = pew.info.contents.getItemFromOpf(member["src"][3:])
        im = Image.open(StringIO.StringIO(member["item"].read()))
        x, y = im.size
        del im
        member["x"] = x
        member["y"] = y
        if x > y:
            member["landscape"] = True

        if member["on_x"] == None and member["on_y"] == None:
            if member["landscape"]:
                if default_x < member["x"]:
                    member["on_ratio"] = ratio = float(default_x) / float(member["x"])
                    member["on_x"] = default_x
                    member["on_y"] = int(float(member["y"]) * float(ratio))
                else:
                    member["on_ratio"] = 1
                    member["on_y"] = member["y"]
                    member["on_x"] = member["x"]

            else:
                if default_y < member["y"]:
                    member["on_ratio"] = ratio = float(default_y) / float(member["y"])
                    member["on_y"] = default_y
                    member["on_x"] = int(float(member["x"]) * float(ratio))
                    #print member["x"], member["y"], member["on_x"], member["on_y"]
                else:
                    member["on_ratio"] = 1
                    member["on_y"] = member["y"]
                    member["on_x"] = member["x"]
        else:
            member["on_ratio"] =  float(member["on_y"]) / float(member["y"])
            print member["landscape"], member["on_ratio"], member["src"]

    #for member in horizontal:
    #    print member['x'], member['y']
    #print "----------------------"
    #for member in landscape:
    #    print member['x'], member['y']
    data = sorted(data, key=lambda member: member['on_y'])
    #print data
    lowest_x = data[0]["on_x"]
    lowest_y = data[0]["on_y"]
    #print lowest_y, lowest_x

    for member in data:
        #if member["landscape"] == True and member["on_ratio"] < 1 and member["x"] < 600:
            #member["on_ratio"] = member["on_ratio"] + 1
        member["ratio"] = float(member['on_y']) / float(lowest_y)
        #print member["src"], member["landscape"], member['on_x'], member['x'], member['on_y'], member['y'], member["ratio"], member["on_ratio"]
        #print member["ratio"], float(member["ratio"])*float(member["on_ratio"])
        im = Image.open(StringIO.StringIO(member["item"].read()))
        #print member["landscape"], float(member["ratio"]) / float(member["on_ratio"])
        f = ImageFont.truetype(fontdir + regularfont, int(float(font_size) / float(member["on_ratio"])))
        fi = ImageFont.truetype(fontdir + italicfont, int(float(font_size) / float(member["on_ratio"])))
        width_pew, git = f.getsize(member["caption"])
        lines = [""]
        turnips = member["caption"].split(" ")
        carryon = ""
        beast = []
        for word in turnips:
            if word.startswith("<em>") or not carryon == "":
                carryon = carryon + word + " "
                if word.endswith("</em>"):
                    beast.append(carryon[:-1])
                    carryon = ""
            else:
                beast.append(word)

        for twats in beast:
            line_width, line_height = f.getsize(lines[-1] + twats)
            if line_width > (member["x"] - (10 * member["ratio"])):
                lines.append(twats)
            else:
                lines[-1] = lines[-1] + " " + twats

        line_height = int(float(font_size) / float(member["on_ratio"]))
        spacing = int(line_height / 2)
        y_h = member["y"] + int(((len(lines) * line_height) + (len(lines) * spacing)) + line_height)
        newimg = Image.new("RGBA", (member["x"], y_h), (255, 255, 255, 0))
        newimg.paste(im, (0, 0, member["x"], member["y"]))
        d = ImageDraw.Draw(newimg)
        lineno = 0
        for line in lines:

            if line.startswith(" "):
                line = line[1:]
            lineno = lineno + 1
            line_width, line_height = f.getsize(line)
            x_loc = int((member["x"] - line_width) / 2)
            y_loc = member["y"] + (lineno * line_height) + (lineno * spacing) - line_height
            #print member["y"], y_loc, line_height, spacing
            if re.search(r'<(em|i)>(.*?)</\1>', line):
                for match in re.finditer(r'<(em|i)>(.*?)</\1>', line):
                    print member["src"]
                    catfish = match.group(0)
                    newline = line.split(catfish)
                    line_width, line_height = f.getsize(newline[0] + " " + match.group(2) + " " + newline[1])
                    x_loc = int((member["x"] - line_width) / 2)
                    if newline[0] == "":
                        newline[0] = " "
                    d.text((x_loc, y_loc), newline[0].decode('utf-8'), font=f, fill=fontcolor)
                    ital_x, ital_y = fi.getsize(match.group(2))
                    fish1_w, fish1_h = f.getsize(newline[0].decode('utf-8'))
                    space_w, space_y = f.getsize(" ")
                    d.text((x_loc + fish1_w + space_w, int(float(y_loc) - math.ceil(float(font_size * member["ratio"]) * 0.1))), match.group(2).decode('utf-8'), font=fi, fill=fontcolor)
                    if newline[1] == "":
                        newline[1] = " "
                    d.text((x_loc + fish1_w + space_w + ital_x, y_loc), newline[1].decode('utf-8'), font=f, fill=fontcolor)
            else:
                d.text((x_loc, y_loc), line.decode('utf-8'), font=f, fill=fontcolor)
        #lines = math.ceil(float(width_pew) / float(member["x"]))
        #d.text((0, member["y"]), caption.decode('utf-8'), font=f, fill=(0, 0, 0))
        newimg.save(os.path.join(image_output_dir, member["item"].opfRelLoc), "JPEG")
        del newimg, im
