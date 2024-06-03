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

# def career_check(skill,char_gen=False):
#     if char_gen:
#        config.read('character_gen/char_config_blank.ini') 
#     if config['CAREER'][f'{skill}_ca'] =='True':
#         skill = skill.title()
#         skill = f':blue[{skill}]'
#         return skill
#     else:
#         skill = skill.title()
#         return skill
    
# def career_skill_check(spec_skill,car_skills):
#     if spec_skill in car_skills:
#         skill = skill.title()
#         skill = f':red[{skill}]'
#         return skill
#     else:
#         skill = skill.title()
#         return skill
    
# def load_tal(cat):
#     tal_list = [tal.strip()[1:-1].title().replace("'S","'s") for tal in config['AB_T'][cat].replace('[','').replace(']','').split(',')] 
#     tal_list.sort()
#     return tal_list

# def del_tal(tal,type,tlist):
#     tlist.remove(tal)
#     config.set('AB_T',type,str(tlist))
#     with open('char_config.ini','w') as f:
#         config.write(f)
#     st.experimental_rerun()


# def show_tal(tal,lookup=False):
#     entry = tal_df.loc[tal]
#     st.write(f'Activation: {entry.Activation}')
#     if lookup==True:
#         st.write(f'Ranked: {entry.Ranked}')
#     st.write(f'Description: {entry.Description}')
#     st.write(f'Wiki Link: {entry.link}')