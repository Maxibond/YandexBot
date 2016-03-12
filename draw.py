# coding=utf-8
import random
from PIL import Image, ImageDraw, ImageFont

import math

# Styles
fontHead = ImageFont.truetype("assets/georgia-bold.ttf", 18)
font = ImageFont.truetype("assets/georgia.ttf", 14)
tag_margin = 5
tag_width = 30
pad = 5


class Tag:
    name = 'default'
    balance = 0

    def __init__(self, name, balance):
        self.name = name
        self.balance = balance


def convert_tags(tags):
    res = []
    for i in tags.keys():
        res.append(Tag(i, tags[i]))
    res.sort(key=lambda m: m.balance, reverse=True)
    return res


def drawLines(time, tags):
    tags = convert_tags(tags)
    print tags
    img_w = 310
    img_h = 500
    image = Image.new("RGBA", (img_w, img_h), (0,0,0,0))

    draw = ImageDraw.Draw(image)

    # Receiving tags
    # time = "March"
    #
    # tags = [Tag(u'Еда', TagType.credit, -230), Tag(u'Транспорт', TagType.credit, -100), Tag(u'Зарплата', TagType.debit, 500) ]
    #
    # tags.sort(key=lambda t: abs(t.balance), reverse=True)

    total_amount = sum(abs(t.balance) for t in tags)
    total_balance = sum(t.balance for t in tags)

    # Header
    draw.text((pad, pad), time, fill='black', font=fontHead)

    str_total = str(total_balance)

    if total_amount > 0:
        str_total = '+' + str_total
    else:
        str_total = '-' + str_total
    total_balance_size = fontHead.getsize(str_total)

    draw.text((img_w - pad - total_balance_size[0], pad), str_total, fill='black', font=fontHead)

    # Drawing tags
    y_pos = 10 + fontHead.getsize(time)[1] + tag_margin

    draw.line([(pad, y_pos), (img_w-pad, y_pos)], fill='black', width=1)

    # draw total balance
    y_pos += pad

    debit_amount = sum(abs(t.balance) for t in tags if t.balance > 0)
    credit_amount = total_amount - debit_amount
    debit_procent = float(debit_amount)/total_amount
    debit_w = (img_w - 2*pad) * debit_procent

    draw.rectangle([(pad, y_pos), (debit_w + pad, y_pos + tag_width)], fill='green')
    draw.rectangle([(debit_w + pad, y_pos), (img_w - pad, y_pos + tag_width)], fill='red')

    debit_text = '+' + str(debit_amount)
    credit_text = '-' + str(credit_amount)
    debit_size = font.getsize(debit_text)
    credit_size = font.getsize(credit_text)
    draw.rectangle([(pad, y_pos + pad), (pad+debit_size[0], y_pos+tag_width-pad)], fill='black')
    draw.rectangle([(img_w - pad - credit_size[0], y_pos + pad), (img_w - pad, y_pos+tag_width-pad)], fill='black')
    draw.text((pad, y_pos + pad), debit_text, font=font)
    draw.text((img_w - pad - credit_size[0], y_pos + pad), credit_text, font=font)

    y_pos += pad + tag_width

    draw.line([(pad, y_pos), (img_w-pad, y_pos)], fill='black', width=1)

    y_pos += tag_margin

    m = 1
    for idx, tag in enumerate(tags):
        if idx == 0:
            m = (img_w / 100) / (float(abs(tag.balance))/total_amount)
        if tag.balance == 0:
            continue
        fill = 'green' if tag.balance > 0 else 'red'
        draw.rectangle([(pad, y_pos), (float(abs(tag.balance))/total_amount*100*m, y_pos+tag_width)], fill=fill)
        draw.text((pad*3, pad+y_pos), str(tag.balance), fill='white', font=font)
        size_name = font.getsize(tag.name)
        size_block_name = (size_name[0] + 2*pad, size_name[1])
        x_pos_name = (img_w - (size_block_name[0] + pad))
        y_pos_name = y_pos + ((tag_width - size_block_name[1]) / 2)
        draw.rectangle([(x_pos_name, y_pos_name), (img_w - pad, y_pos_name + size_block_name[1] + 3)], fill='black')
        draw.text((x_pos_name + pad, y_pos_name), tag.name, fill='white', font=font)
        y_pos += tag_margin + tag_width

    del draw
    image.save("test.png", "PNG")

# Draw Circle Total
def drawCircle(time, tags):
    tags = convert_tags(tags)
    img_w = 310
    img_h = 300 + 25 * len(tags)
    image = Image.new("RGBA", (img_w, img_h), (0,0,0,0))
    draw = ImageDraw.Draw(image)
    draw.text((pad, pad), time, fill='black', font=fontHead)
    draw.line([(pad, pad+20), (img_w-pad, pad+20)], fill='black', width=1)
    r = 100
    colors = ['#73BF43', '#F48221', '#0065B3', '#CF3734', '#FEF330', '#f1c40f', '#e67e22', '#e74c3c', '#95a5a6']
    random.shuffle(colors)
    x_pos = img_w / 2
    y_pos = x_pos
    draw.ellipse((x_pos-r-1, y_pos-r-1, x_pos+r+1, y_pos+r+1), fill='black', outline='black')
    total_amount = sum(abs(t.balance) for t in tags)
    tag_gen = (float(abs(t.balance))/total_amount*100 for t in tags)
    colors = (clr for clr in colors)
    value = tag_gen.next()
    color = colors.next()
    pog = 1.0/3.6 # procents on gradus
    used_colors = []
    if tags:
        used_colors.append(color)
    for i in xrange(0, 360, 0.25):
        i *= 0.0174533/4 # grad to rad
        if value <= 0:
            value = tag_gen.next()
            color = colors.next()
            used_colors.append(color)
        draw.line([(x_pos, y_pos), (x_pos+r*math.cos(i), y_pos+r*math.sin(i))], fill=color, width=1)
        value -= pog

    # draw legend
    y_pos += r + pad

    legend = zip(used_colors, tags)
    tag_gen = (float(abs(t.balance))/total_amount*100 for t in tags)

    for l in legend:
        draw.rectangle([(pad, y_pos), (pad+30, y_pos + tag_width/2)], fill=l[0])
        text = l[1].name + ' - ' + str(abs(l[1].balance)) + ' (%.2f %)' % str(tag_gen.next())
        draw.text((2*pad+30, y_pos), text, fill='black', font=font)
        y_pos += tag_width

    del draw
    image.save("1.png", "PNG")



