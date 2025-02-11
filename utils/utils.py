import ast, configparser
from PIL import Image
import streamlit as st
import pandas as pd
from random import randint

def load_bool(bool_):
    if bool_=='True':
        return True
    else:
        return False
    
def dic_load(dic_):
    dic = ast.literal_eval(dic_)
    return dic

def load_resize_image(img):
    new_img = Image.open(img)
    new_img.thumbnail((500,200))
    return new_img

def space_check(check):
    if '_' in check:
        check = check.replace('_',' ')
    else:
        check = check
    return check

min_max_dict = {
    'Strength': {'min': 15, 'max': 100, 'derived': False}, 
    'Constitution': {'min': 15, 'max': 100, 'derived': False}, 
    'Size': {'min': 40, 'max': 100, 'derived': False}, 
    'Dexterity': {'min': 15, 'max': 100, 'derived': False}, 
    'Appearance': {'min': 15, 'max': 100, 'derived': False}, 
    'Education': {'min': 15, 'max': 100, 'derived': False}, 
    'Intelligence': {'min': 40, 'max': 100, 'derived': False}, 
    'Power': {'min': 15, 'max': 100, 'derived': False}, 
    'Luck': {'min': 0, 'max': 100, 'derived': False}, 
    'Hit Points': {'min': 0, 'max': 100, 'derived': True}, 
    'Magic Points': {'min': 0, 'max': 100, 'derived': True}, 
    'Sanity': {'min': 0, 'max': 100, 'derived': True},
    'Accounting': {'min': 5, 'max': 100, 'derived': False},
    'Animal Handling': {'min': 1, 'max': 100, 'derived': False},
    'Anthropology': {'min': 1, 'max': 100, 'derived': False},
    'Appraise': {'min': 5, 'max': 100, 'derived': False},
    'Archaeology': {'min': 1, 'max': 100, 'derived': False},
    'Charm': {'min': 15, 'max': 100, 'derived': False},
    'Climb': {'min': 20, 'max': 100, 'derived': False},
    'Computer Use': {'min': 5, 'max': 100, 'derived': False},
    'Credit Rating': {'min': 0, 'max': 100, 'derived': False},
    'Cthulhu Mythos': {'min': 0, 'max': 100, 'derived': False},
    'Disguise': {'min': 5, 'max': 100, 'derived': False},
    'Dodge': {'min': 0, 'max': 100, 'derived': True},
    'Drive Auto': {'min': 20, 'max': 100, 'derived': False},
    'Electrical Repair': {'min': 1, 'max': 100, 'derived': False},
    'Electronics': {'min': 1, 'max': 100, 'derived': False},
    'Fast Talk': {'min': 5, 'max': 100, 'derived': False},
    'Brawl': {'min': 25, 'max': 100, 'derived': False},
    'Firearms (Small Arms)': {'min': 20, 'max': 100, 'derived': False},
    'Firearms (Rifle/Shotgun)': {'min': 25, 'max': 100, 'derived': False},
    'First Aid': {'min': 30, 'max': 100, 'derived': False},
    'History': {'min': 5, 'max': 100, 'derived': False},
    'Intimidate': {'min': 15, 'max': 100, 'derived': False},
    'Jump': {'min': 20, 'max': 100, 'derived': False},
    'English': {'min': 20, 'max': 100, 'derived': False},
    'French': {'min': 1, 'max': 100, 'derived': False},
    'Law': {'min': 5, 'max': 100, 'derived': False},
    'Library Use': {'min': 20, 'max': 100, 'derived': False},
    'Listen': {'min': 20, 'max': 100, 'derived': False},
    'Locksmith': {'min': 1, 'max': 100, 'derived': False},
    'Mechanical Repair': {'min': 10, 'max': 100, 'derived': False},
    'Medicine': {'min': 1, 'max': 100, 'derived': False},
    'Natural World': {'min': 10, 'max': 100, 'derived': False},
    'Navigate': {'min': 10, 'max': 100, 'derived': False},
    'Occult': {'min': 5, 'max': 100, 'derived': False},
    'Operate Heavy Machinery': {'min': 1, 'max': 100, 'derived': False},
    'Persuade': {'min': 10, 'max': 100, 'derived': False},
    'Pilot': {'min': 1, 'max': 100, 'derived': False},
    'Psychoanalysis': {'min': 1, 'max': 100, 'derived': False},
    'Psychology': {'min': 10, 'max': 100, 'derived': False},
    'Read Lips': {'min': 1, 'max': 100, 'derived': False},
    'Ride': {'min': 5, 'max': 100, 'derived': False},
    'Sleight of Hand': {'min': 10, 'max': 100, 'derived': False},
    'Spot Hidden': {'min': 25, 'max': 100, 'derived': False},
    'Stealth': {'min': 20, 'max': 100, 'derived': False},
    'Survival': {'min': 1, 'max': 100, 'derived': False},
    'Swim': {'min': 1, 'max': 100, 'derived': False},
    'Throw': {'min': 20, 'max': 100, 'derived': False},
    'Track': {'min': 10, 'max': 100, 'derived': False}
}

def derive(df,func,limit):
    if func == 'Hit Points':
        if limit == 'max':
            val = int(df[['Size','Constitution']].sum()/10)
        elif limit == 'min':
            val = 0
    elif func == 'Magic Points':
        if limit == 'max':
            val = int(df['Power']/5)
        if limit == 'min':
            val = 0
    elif func == 'Sanity':
        if limit == 'max':
            val = int(99 - df['Cthulhu Mythos'])
        elif limit == 'min':
            val = 0
    elif func == 'Dodge':
        if limit == 'min':
            val = round(df['Dexterity']/2)
        elif limit == 'max':
            val = 100
    return val

success_thresholds = {
    'fumble': lambda x: (94 if x<50 else 99,100),
    'failure':lambda x: (x,94 if x<50 else 100),
    'success':lambda x: (int(x/2),x),
    'hard success':lambda x: (int(x/5),int(x/2)),
    'critical success':lambda x: (0,1)
    }

def roll(val):
    die_result = randint(0,100)
    calc_thresh = {key:success_thresholds[key](val) for key in success_thresholds}
    for key in calc_thresh:
        if calc_thresh[key][0]<die_result<=calc_thresh[key][1]:
            result_desc = key
    return die_result,result_desc
        
