import ast, configparser
from PIL import Image
import streamlit as st
import pandas as pd

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
    'Sanity': {'min': 0, 'max': 100, 'derived': True}
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
    return val
