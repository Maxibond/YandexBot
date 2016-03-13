# coding=utf-8
import random
from PIL import Image, ImageDraw, ImageFont

import math

# Styles
import datetime

fontHead = ImageFont.truetype("assets/georgia-bold.ttf", 18)
font = ImageFont.truetype("assets/georgia.ttf", 14)
tag_margin = 5
tag_width = 30
pad = 5
background_color = '#EBFFE6'


class Tag:
    name = 'default'
    balance = 0

    def __init__(self, name, balance):
        self.name = name
        self.balance = balance


def convert_tags(tags, add_positive=True):
    res = []
    for i in tags.keys():
        if add_positive:
            res.append(Tag(i.decode('utf8'), -tags[i]))
        else:
            if tags[i] > 0:
                res.append(Tag(i.decode('utf8'), -tags[i]))
    res.sort(key=lambda m: m.balance)
    return res


def drawLines(time, tags):
    tags = convert_tags(tags)
    print tags
    img_w = 310
    img_h = 250 + 15 * len(tags)
    image = Image.new("RGB", (img_w, img_h), '#EBFFE6')

    draw = ImageDraw.Draw(image)

    # Receiving tags
    # time = "March"
    #
    # tags = [Tag(u'Еда', TagType.credit, -230), Tag(u'Транспорт', TagType.credit, -100), Tag(u'Зарплата', TagType.debit, 500) ]
    #
    # tags.sort(key=lambda t: abs(t.balance), reverse=True)

    total_amount = sum(abs(t.balance) for t in tags)
    total_balance = sum(t.balance for t in tags)

    days = datetime.date.today().day

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
    credit_text = str(credit_amount)
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
        draw.text((pad*3, pad+y_pos), str(tag.balance), fill='black', font=font)
        size_name = font.getsize(tag.name)
        size_block_name = (size_name[0] + 2*pad, size_name[1])
        x_pos_name = (img_w - (size_block_name[0] + pad))
        y_pos_name = y_pos + ((tag_width - size_block_name[1]) / 2)
        draw.rectangle([(x_pos_name, y_pos_name), (img_w - pad, y_pos_name + size_block_name[1] + 3)], fill='black')
        draw.text((x_pos_name + pad, y_pos_name), tag.name, fill='white', font=font)
        y_pos += tag_margin + tag_width

    draw.line((pad, y_pos, img_w-pad, y_pos), fill='black')
    y_pos += pad

    average_debit = debit_amount / days
    average_credit = credit_amount / days

    draw.text((pad, y_pos), u'Средний доход в день: ' + str(average_debit), font=font, fill='black')
    y_pos += pad*3
    draw.text((pad, y_pos), u'Средний расход в день: ' + str(average_credit), font=font, fill='black')

    del draw
    image.save("1.png", "PNG")

# Draw Circle Total
def drawCircle(time, tags):
    tags = convert_tags(tags, False)
    img_w = 310
    img_h = 300 + 25 * len(tags)
    image = Image.new("RGB", (img_w, img_h), '#EBFFE6')
    draw = ImageDraw.Draw(image)
    draw.text(((img_w-fontHead.getsize(time)[0])/2, pad), time, fill='black', font=fontHead)
    draw.line([(pad, pad+20), (img_w-pad, pad+20)], fill='black', width=1)
    r = 100
    colors = ['#BFFE9E', '#FEFE9E', '#FFDFA6', '#FEBDA3', '#FE9EB5', '#E49EFE', '#C3B0FF', '#9E9FFE', '#A1CCFF',
              '#9FE5FE', '#9EFECE']
    # random.shuffle(colors)
    x_pos = img_w / 2
    y_pos = x_pos
    total_amount = sum(abs(t.balance) for t in tags)
    tag_gen = (float(abs(t.balance))/total_amount*100 for t in tags)
    colors = (clr for clr in colors)
    value = tag_gen.next()
    color = colors.next()
    pog = 1.0/3.6 # procents on gradus
    used_colors = []
    def drange(start, stop, step):
        q = start
        while q < stop:
            yield q
            q += step
    if tags:
        used_colors.append(color)
    for i in drange(0, 360, 0.1):
        i *= 0.0174533 # grad to rad
        if value <= 0:
            value = tag_gen.next()
            color = colors.next()
            used_colors.append(color)
        draw.line([(x_pos, y_pos), (x_pos+r*math.cos(i), y_pos+r*math.sin(i))], fill=color, width=2)
        value -= pog/10

    # draw legend
    y_pos += r + pad

    legend = zip(used_colors, tags)
    tag_gen = (float(abs(t.balance))/total_amount*100 for t in tags)

    for l in legend:
        draw.rectangle([(pad, y_pos), (pad+45, y_pos + tag_width/2)], fill=l[0])
        text = l[1].name + ' - ' + str(abs(l[1].balance))
        draw.text((2*pad+45, y_pos), text, fill='black', font=font)
        text = '{0:.1f}'.format(tag_gen.next())
        draw.text((pad+(45-font.getsize(text)[0])/2, y_pos), text, fill='black', font=font)
        y_pos += tag_width

    del draw
    image.save("1.png", "PNG")



