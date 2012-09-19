import epub
import os
from PIL import Image, ImageFont, ImageDraw
import StringIO
import math
import re

target_file = "/home/nic/Desktop/Ebooks/RH_Conversion/howbrit/FILE-copy.epub"
image_output_dir = "/home/nic/Desktop/Ebooks/RH_Conversion/howbrit/test"
font_size = 12

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
                             "portrait": True,
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
        member["x"] = x
        member["y"] = y
        if x > y:
            member["portrait"] = False

        if member["on_x"] == None and member["on_y"] == None:
            if member["portrait"]:
                member["on_ratio"] = ratio = float(default_y) / float(member["y"])
                member["on_y"] = default_y
                member["on_x"] = int(float(member["x"]) * float(ratio))
            else:
                member["on_ratio"] = ratio = float(default_x) / float(member["x"])
                member["on_x"] = default_x
                member["on_y"] = int(float(member["y"]) * float(ratio))
        else:
            member["on_ratio"] = 1

    #for member in horizontal:
    #    print member['x'], member['y']
    #print "----------------------"
    #for member in portrait:
    #    print member['x'], member['y']
    data = sorted(data, key=lambda member: member['on_y'])

    lowest_x = data[0]["x"]
    lowest_y = data[0]["y"]

    for member in data:
        #print member['on_x'], member['on_y'], member['x'], member['y']
        member["ratio"] = float(member['y']) / float(lowest_y)
        #print member["ratio"], float(member["ratio"])*float(member["on_ratio"])
        im = Image.open(StringIO.StringIO(member["item"].read()))
        f = ImageFont.truetype("/home/nic/Desktop/Ebooks/RH_Conversion/howbrit/Bitter-Regular.otf", int(float(font_size) * float(member["ratio"])))
        fi = ImageFont.truetype("/home/nic/Desktop/Ebooks/RH_Conversion/howbrit/Bitter-Italic.otf", int(float(font_size) * float(member["ratio"])))
        width_pew, git = f.getsize(member["caption"])
        lines = [""]
        turnips = member["caption"].split(" ")
        for twats in turnips:
            line_width, line_height = f.getsize(lines[-1] + twats)
            if line_width > (member["x"] - (10 * member["ratio"])):
                lines.append(twats)
            else:
                lines[-1] = lines[-1] + " " + twats

        line_height = int(font_size * member["ratio"])
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
                    catfish = match.group(0)
                    newline = line.split(catfish)
                    line_width, line_height = f.getsize(newline[0] + " " + match.group(2) + " " + newline[1])
                    x_loc = int((member["x"] - line_width) / 2)
                    d.text((x_loc, y_loc), newline[0].decode('utf-8'), font=f, fill=(0, 0, 0))
                    ital_x, ital_y = fi.getsize(match.group(2))
                    fish1_w, fish1_h = f.getsize(newline[0].decode('utf-8'))
                    space_w, space_y = f.getsize(" ")
                    d.text((x_loc + fish1_w + space_w, int(float(y_loc) - math.ceil(float(font_size * member["ratio"]) * 0.1))), match.group(2).decode('utf-8'), font=fi, fill=(0, 0, 0))
                    d.text((x_loc + fish1_w + space_w + ital_x, y_loc), newline[1].decode('utf-8'), font=f, fill=(0, 0, 0))
            else:
                d.text((x_loc, y_loc), line.decode('utf-8'), font=f, fill=(0, 0, 0))
        #lines = math.ceil(float(width_pew) / float(member["x"]))
        #d.text((0, member["y"]), caption.decode('utf-8'), font=f, fill=(0, 0, 0))
        newimg.save(os.path.join(image_output_dir, member["item"].opfRelLoc), "JPEG")

