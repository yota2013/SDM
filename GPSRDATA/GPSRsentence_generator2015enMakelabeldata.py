#!/usr/bin/python
# -*- coding: utf-8 -*-
#######################################################
# GPSR sentence generator
# version: 15.05
#
# Programmed by:
# Tijn van der Zant, Komei Sugiura
# email: tijn@ieee.org, komei.sugiura@gmail.com
#
#######################################################

# imports
import random
import sys
import copy
import os
import pandas as pd
import string
import base64
import json
import wave
import math


# service URL
tts_url ='http://rospeex.ucri.jgn-x.jp/nauth_json/jsServices/VoiceTraSS'

# read the locations, objects and sentences files
# and clean up the lists from the files
rooms           = []
locations       = []
items           = []
class_items     = []
cat1Sentences   = []
cat2Sentences   = []
cat3Situations  = []
names           = []
# get rid of empty lines and do not use anything that starts with a '#'
# '#'はコメントアウトの飛ばす.
for room in [line.strip('\n') for line in open('rooms.txt', 'r').readlines()]:
    if room != '': #データないなら飛ばす
        if room[0] != '#':
            room = room.replace(' ', '_')
            rooms.append(room)


for loc in [location.strip('\n') for location in open('locations.txt', 'r').readlines()]:
    if loc != '':
        if loc[0] != '#':
            loc = loc.replace(' ', '_')
            locations.append(loc)

for it  in [item.strip('\n')     for item     in open('items.txt',   'r').readlines()]: #改行で配列に入れる
    if it  != '':
        if it[0] != '#':
            it = it.replace(' ', '_')
            items.append(it)

for ci  in [class_item.strip('\n')     for class_item     in open('class_items.txt',   'r').readlines()]:
    if ci  != '':
        if ci[0] != '#':
            ci = ci.replace(' ', '_')
            class_items.append(ci)

#====================0906=============================================#
"""
for sentence in [str(sent).strip('\n') for sent in open('cat1Sentences.txt' , 'r').readlines()]:
    if sentence != '':
        if sentence[0] != '#':
            cat1Sentences.append(sentence)
"""
filename = "cat1Sentences0126.en.xlsx"
df = pd.read_excel(filename, sheet_name='Sheet1')
for sentence in df['Sentence']:
    if sentence != '':
        if sentence[0] != '#':
            cat1Sentences.append(sentence)

labeldatas =[]
labelSetdatas = []
ndata = len(cat1Sentences)

for label in df['label']:
    if label != '':
            labeldatas.append(label)

for i in range(ndata):
    labelSetdatas.append([cat1Sentences[i],labeldatas[i]])


for sentence in [str(sent).strip('\n') for sent in open('cat2Sentences.txt' , 'r').readlines()]:
    if sentence != '':
        if sentence[0] != '#':
            cat2Sentences.append(sentence)

situations  = []
questions   = []
for sit in [str(sent).strip('\n') for sent in open('cat3Situations.txt' , 'r').readlines()]:
    if sit != '':
        if sit[0] != '#':
            if sit.split()[0] == 'situation:':
                situations.append( sit )
            if sit.split()[0] == 'question:':
                questions.append( sit )
cat3Situations = zip( situations, questions )

for name in [nam.strip('\n')     for nam     in open('names.txt',   'r').readlines()]:
    if name  != '':
        if name[0] != '#':
            names.append(name)

# are there at least two locations?
if len(locations) < 2: #ロケーションが２つ以上ないとダメ
    print ('Not enough locations. Exiting program')
    sys.exit(1)
# are there at least two items?
if len(items) < 2: #アイテムが２つ以上ないとダメ
    print ('Not enough items. Exiting program')
    sys.exit(1)
#-----------------------------------ここまでデータ宣言している．----------------------------------#

# the function 'fillIn' takes a sentence and replaces
# the word 'location' for an actual location
# and replaces the word 'item' for an actual item
# as defined in the files:
# locations.txt
# and items.txt
#random.shuffle(

def fillIn(labelSetdatas):
    sentences = labelSetdatas[0]

    labels = labelSetdatas[1]
    #shuffle the items and the locations
    random.shuffle(rooms)#リストをランダムソート
    random.shuffle(items)
    random.shuffle(class_items)
    random.shuffle(locations)
    random.shuffle(names)
    #fill in the locations and items in the sentence
    # the counters are used so an item or location is not used twice
    # hence the shuffeling for randomization
    roomCounter         = 0
    itemCounter         = 0
    class_itemCounter   = 0
    locationCounter     = 0
    nameCounter         = 0
    finalSentence       = []

    roomLabel = []
    itemLabel = []
    classLabel = []
    locationLabel = []
    nameLabel = []
    finalLabel =[]

    #センテンスとラベる;;
    #wordとsentenceどっちも長さが違うループをからカテゴリ保管
#２個前がFindなら

    for word in sentences.split(' '):#センテンスを
#	print word
        # fill in a room
        if word == 'ROOM':
            finalSentence.append( rooms[roomCounter] )
            roomLabel.append(rooms[roomCounter])
            roomCounter += 1
        # or fill in a location
        elif word == 'LOCATION':
            finalSentence.append( locations[locationCounter])
            locationLabel.append(locations[locationCounter])
            locationCounter += 1
        # or an item
        elif word == 'ITEM':
            finalSentence.append( items[itemCounter] )
            itemLabel.append(items[itemCounter])
            itemCounter += 1
        # or an item class
        elif word == 'CLASS_ITEM':
            finalSentence.append( class_items[class_itemCounter] )
            classLabel.append(class_items[class_itemCounter])
            class_itemCounter += 1
        # is it a name?
        elif word == 'NAME':
            finalSentence.append(names[nameCounter])
            nameLabel.append(names[nameCounter])
            nameCounter += 1
        # perhaps a location with a comma or dot?
        elif word[:-1] == 'LOCATION':
            #print(word[:-1])
            finalSentence.append( locations[locationCounter] + word[-1])
            locationLabel.append(locations[locationCounter] + word[-1])
            locationCounter += 1
        # or an item with a comma or dot or whatever
        elif word[:-1] == 'ITEM':
            finalSentence.append( items[itemCounter] + word[-1])
            itemLabel.append(items[itemCounter] + word[-1])
            itemCounter += 1
        # is it a namewith a comma, dot, whatever?
        elif word[:-1] == 'NAME':
            finalSentence.append( names[nameCounter] + word[-1])
            nameLabel.append(names[nameCounter] + word[-1])
            nameCounter += 1
        # or else just the word
        else:
            finalSentence.append( word )

    if (roomCounter  > 3 or
    itemCounter  > 3 or
    class_itemCounter > 3 or
    locationCounter  > 3 or
    nameCounter    > 3):
        print("--------------------おわり------------------------")

#Find と Place
#それぞれ二回の場合を考える．数が違うからそこが問題です
#A.その組み合わせを探す．
    roomLabelCounter    = 0
    itemLabelCounter    = 0
    class_itemCounter   = 0
    locationLabelCounter     = 0
    nameCounter         = 0
    #placeとFindがきたら　一つへらすその前のROOM ,location の値を一つどっちか減らす

    if(str(labels) !="nan"):
        #print (labels)
        for label in labels.split(' '):#センテンスを
                if label.find(u',') > -1:
                    continue
                #print(label)
                if label.find(u'Find') > -1 or label.find(u'Place') > -1 :
                    if roomLabelCounter >= 1:
                        roomLabelCounter -=1
                    elif locationLabelCounter >= 1:
                        locationLabelCounter -=1
                if label.find(u'ROOM') > -1:
                    label = label.replace(u'ROOM',roomLabel[roomLabelCounter])
                    if(roomCounter >= 2 and roomLabelCounter  < 1):
                        roomLabelCounter += 1
                elif label.find(u'LOCATION') > -1:
                    label = label.replace(u'LOCATION',locationLabel[locationLabelCounter])
                    if(locationCounter >= 2 and locationLabelCounter  < 1):
                        locationLabelCounter += 1
                elif label.find(u'ITEM') > -1:
                    label = label.replace('ITEM',itemLabel[itemLabelCounter])
                    if(itemCounter >= 2 and itemLabelCounter  < 1):
                        itemLabelCounter +=1
                elif label.find(u'CLASS_ITEM') > -1:
                    label = label.replace('CLASS_ITEM',classLabel[class_itemCounter])
                    class_itemCounter += 1
                elif label.find(u'NAME') > -1:
                    label = label.replace('NAME',nameLabel[nameCounter])
                    nameCounter +=1
                finalLabel.append(label)
        outfinalLabel  = ' '.join(finalLabel)
        outfinalLabel = outfinalLabel.replace('\"[','')
        outfinalLabel = outfinalLabel.replace(']\"','')
    else:
        outfinalLabel = "NULL"
    # then make a sentence again out of the created list
#	    print finalSentence
    out = ' '.join(finalSentence)
    #print(out)
    out = out.replace('    ', ' ')
    out = out.replace('   ', ' ')
    out = out.replace('   ', ' ')
    outfinalLabel =''.join(outfinalLabel)
    outfinalLabel = outfinalLabel.replace('    ', ' ')
    outfinalLabel = outfinalLabel.replace('   ', ' ')
    outfinalLabel = outfinalLabel.replace('   ', ' ')

    # return ' '.join(finalSentence)
    print(outfinalLabel)
    return out,outfinalLabel


# the tests are defined here
#cat1Sentences で

def testOne():

    df = pd.DataFrame([],columns=["data","labeldata"])
    #100sentence
    #for i in range(100):

    #print(random.choice(labelSetdatas))
    for i in range(15000):
        random.shuffle(labelSetdatas)
        #print("shfffle"+str(labelSetdatas[0]))
        sentence = pd.DataFrame([fillIn(labelSetdatas[0])],columns=["data","labeldata"])
        df = df.append(sentence)
    #yotaコメントアウト
    #print('\n%s\n\n' % sentence)
    df.drop_duplicates(["data"])
    df.to_csv("GPSRSentenceJP.csv",index=False,mode='a',header=True,encoding="cp932")



# ask the user which test this program should generate
def mainLoop():

    #answer = raw_input('Which category do you want to do?\nPossible answers are: 1,or q(uit)')
    answer = '1'
    if answer == 'q':
        print ('Exiting program.')
        sys.exit(1)
    elif answer == '1':
        print ('Category 1:\n',
        testOne())
    else:
        print ('\nNot a valid input, please try 1, 2, 3 or q(uit)\n')

if __name__ == "__main__":
    mainLoop()
