import streamlit as st
import pandas as pd
from utils.utils import *
import os,sys
from streamlit_server_state import server_state
import numpy as np


##Instantiating variables
pd.set_option('mode.chained_assignment', None)

#Reference dataframes. These are used to define the lists then discarded, primary refreshing to reflect edits is done in the main wiki loop
if 'show_flow' in sys.argv:
    print('Wiki View Load')
preload_df = pd.read_csv('wiki.csv',encoding='utf-8',index_col='Entry',keep_default_na=False)
preload_df=preload_df[['body','expanded_info','img_path','caption','category','alias']]
skill_df = pd.read_csv('skills.csv',encoding='utf-8',index_col='skill')
success_df = pd.read_csv('successes.csv',encoding='utf-8',index_col='skill')
attribute_df = pd.read_csv('attributes.csv',encoding='utf-8',index_col='attribute')
#Temporary measure until the wiki.csv is totally cleaned
variant_spellings = preload_df[['See ' in bod for bod in  preload_df.body.values.tolist()]].index.tolist()
# preload_df.drop(variant_spellings,axis=0,inplace=True)
# all_topics = preload_df.index.tolist()
highlight_alias = []
for term in preload_df.alias.dropna().tolist():
    for split in term.split(','):
        highlight_alias.append(split)
highlight_names = preload_df.index.tolist()
highlight_names= [t.split(' (')[0] for t in highlight_names]
generic_filters = ['"Sergeant"','Chief Petty Officer','Dr.','Admiral','Senator','Senior','Technician','Inspector','Inquisitor','species','faction','Sergeant','High','Priest','Priestess','Lieutenant','Commander','General','Master','Lord','Moff','née','Lady','Captain','Major','Brothers','ISD','NRS','Colonel','Grand']
for index,raw_name in enumerate(highlight_names):
    replace_terms = [gen_filter for gen_filter in generic_filters if gen_filter in raw_name]
    for term in replace_terms:
        raw_name = raw_name.replace(term,'').strip()
    highlight_names[index]=raw_name
highlight_names = highlight_names + highlight_alias

##TODO: Figure out highlighting priority, currently highlighting last names before full names and blocking them out. Maybe also find source of blanks but lower priority.
def highlight(raw_text):
    to_highlight = []
    for term in highlight_names:
        if term in raw_text:
            to_highlight.append(term)
    to_highlight = [t for t in list(set(to_highlight)) if t != '']
    spaced = [f' {term} ' for term in to_highlight]    
    for term in spaced:
        raw_text = raw_text.replace(term,f' :blue[**{term.strip()}**] ')
    return raw_text



def display_wiki(topic,wf,edit=False,session_id=None):
    img_entries = wf[wf.img_path.isna()==False].index.tolist()
    body = wf.loc[topic].body
    body = highlight(body)
    if edit and server_state['editor']==session_id:
        server_state['open']=True
        st.header('Editing article. Please do not reload or exit the page without discarding or saving your changes.')
        if topic==server_state.get('open_article'):
            og_body = wf.loc[topic].body
            og_expanded = str(wf.loc[topic].expanded_info)
            st.title(topic)
            left_,right_=st.columns(2)
            with left_:
                st.subheader('In our campaign:')
                new_body = st.text_area(label='campaign info',value=og_body,label_visibility='hidden',height=1000)
                st.subheader('Further Information:')
                if og_expanded == 'nan':
                    new_expanded = st.text_area(label='expanded info',label_visibility='hidden',height=1000)
                else:
                    new_expanded = st.text_area(label='expanded info',value=og_expanded,label_visibility='hidden',height=1000)
            with right_:
                if topic in img_entries:
                    img_file_name = wf.loc[topic].img_path.split(',')
                    img_path = []
                    for img_file_path in img_file_name:
                        path_name = os.path.join('figs','wiki_topics',img_file_path)
                        img_path.append(path_name)
                    caption_raw = str(wf.loc[topic].caption).split('{}') #{} is just what I chose to use a separator, since it's not likely to appear in normal captioning
                else:
                    img_path,caption_raw=[],[]
                #Treat everything as a list until proven otherwise
                caption = []
                for cap in caption_raw:
                    caption.append(cap)
                if topic in img_entries:
                    if caption != 'nan':
                        st.image(img_path,caption=caption)
                    else:
                        st.image(img_path)
                new_cap_list = []
                for img_name,cap_ in zip(img_path,caption):
                    shortened_name = img_name.split('\\')[-1]
                    st.write(f'Filename: {shortened_name}')
                    new_cap = st.text_input(label='Caption',value=cap_,key=f'{shortened_name}-{cap_}')
                    new_cap_list.append(new_cap)
                    if st.button(label='Delete Image (No Undo option and will automatically save all changes and force a reload)',key=f'{shortened_name}-del'):
                        if len(img_path)>1:
                            new_img_path = wf.at[topic,'img_path'].replace(shortened_name,'')
                            if new_img_path[0]==',':
                                new_img_path=new_img_path[1:]
                            if new_img_path[-1]==',':
                                new_img_path=new_img_path[:-1]
                            wf.at[topic,'img_path'] = new_img_path
                        else:
                            img_entries.remove(topic)
                            wf.at[topic,'img_path'] = None
                        if len(caption_raw)>1:
                            caption_raw.remove(cap_)
                            new_caption = '{}'.join(caption_raw)
                            wf.at[topic,'caption']= str(new_caption)
                        else:
                            wf.at[topic,'caption'] = 'nan'
                        wf.to_csv('wiki.csv',encoding='utf-8',index='Entry')
                        os.unlink(img_name)
                        st.rerun()
                if 'debug' in sys.argv:
                    if st.button(label='debug',key='debug_captions'):
                        print('-----------')
                        print(f'raw: {caption_raw}')
                        print(f'list: {caption}')
                        print(f'new list: {new_cap_list}')
                        new_captions = '{}'.join(new_cap_list)
                        print(f'new raw: {new_captions}')
                        print(f'og entry: {wf.loc[topic].caption}')
                        print('-----------')
                new_image = st.file_uploader(label='Upload new image',type=['png','jpg'],accept_multiple_files=False)
                if new_image != None:
                    if st.button(label='Upload to server (saves all current changes)',key=f'confirm-upload-{new_image.name}'):
                        cwd = os.getcwd()
                        extant = os.listdir('figs/wiki_topics')
                        if new_image.name in extant:
                            new_image.name = f'{topic}-{new_image.name}'
                        save_path = os.path.join(cwd,'figs','wiki_topics',new_image.name)
                        with open(save_path,'wb') as f:
                            bytes_data = new_image.read()
                            f.write(bytes_data)
                        if str(wf.loc[topic].img_path)=='nan' or wf.loc[topic].img_path==None:
                            if 'show_flow' in sys.argv:
                                print('Upload image, no previous image switch')
                            wf.at[topic,'img_path']=new_image.name
                            wf.at[topic,'caption']=f'Caption for {new_image.name}'
                        else:
                            if 'show_flow' in sys.argv:
                                print('Upload image, existing images switch')
                            new_img_path = ','.join([wf.at[topic,'img_path'],new_image.name])
                            wf.at[topic,'img_path'] = new_img_path
                            caption_placeholder = '{}'.join([wf.at[topic,'caption'],f'Caption for {new_image.name}'])
                            wf.at[topic,'caption']=caption_placeholder
                        wf.to_csv('wiki.csv',encoding='utf-8',index=True)
                        st.rerun()
                if 'debug' in sys.argv:
                    if st.button(label='debug',key='debug_images'):
                        print('-----------')
                        print(f'file uploader object: {new_image}')
                        current_path = wf.at[topic,'img_path']
                        print(f'Current img_path: {current_path}')
                        print('-----------')
        if st.button(label='Discard Changes',key='discard_widget'):
            st.session_state['persist_topic']=topic
            st.session_state['persist_cat']=wf.loc[topic].category
            server_state['open'],server_state['open_article'],server_state['editor'] = False,None,None #This line has to run last in this widget--I don't know why. All loops refresh after this line.
        if st.button(label='Save Changes',key='save_widget'):
            wf.at[topic,'body'] = new_body
            if new_expanded == '':
                wf.at[topic,'expanded_info'] = 'nan'
            else:
                wf.at[topic,'expanded_info'] = new_expanded
            new_captions = '{}'.join(new_cap_list)
            if new_captions != wf.loc[topic].caption:
                wf.at[topic,'caption']=new_captions
            wf.to_csv('wiki.csv',encoding='utf-8',index='Entry')
            st.session_state['persist_topic']=topic
            st.session_state['persist_cat']=wf.loc[topic].category
            server_state['open'],server_state['open_article'],server_state['editor'] = False,None,None
        if 'debug' in sys.argv:
            if st.button(label='debug'):
                print('----------')
                print(f'Editor: {server_state["editor"]}')
                print(f'User: {session_id}')
                print(f'Equal: {server_state["editor"]==session_id}')
                print('----------')
    else:
        if wf.loc[topic].category == 'pcs':
            title_,save_,edit_ = st.columns([9,1,1])
            with title_:
                st.title(topic)
            with edit_:
                edit = st.checkbox('Edit')
            with st.expander(label='Characteristics',expanded=True):
                attributes = attribute_df.index.tolist()
                if edit:
                    l_,cl_,cr_,r_=st.columns(4)
                    indices = list(np.arange(0,int(len(attributes)),round(len(attributes)/4)))
                    for col,i in zip([l_,cl_,cr_,r_],range(len(indices))):
                        with col:
                            if indices[i]!=indices[-1]:
                                attribute_slice = attributes[indices[i]:indices[i+1]]
                            else:
                                attribute_slice = attributes[indices[i]:]
                            for attribute in attribute_slice:
                                with st.container():
                                    if f'{attribute}-input-field' not in st.session_state:
                                        st.session_state[f'{attribute}-input-field']=int(attribute_df.loc[attribute,topic])
                                    if min_max_dict[attribute]['derived']:
                                        if attribute == 'Sanity':
                                            max_value = derive(skill_df[topic],'Sanity','max')                          
                                        else:
                                            max_value = derive(attribute_df[topic],attribute,'max')
                                        min_value = derive(attribute_df,attribute,'min')
                                        if attribute_df[topic][attribute]<min_value:
                                            attribute_df[topic][attribute]=min_value
                                        st.number_input(label=attribute,min_value=min_value,max_value=max_value,key=f'{attribute}-input-field')
                                    else:
                                        if attribute_df[topic][attribute]<min_max_dict[attribute]['min']:
                                            attribute_df[topic][attribute]=min_max_dict[attribute]['min']
                                        st.number_input(label=attribute,min_value=min_max_dict[attribute]['min'],max_value=min_max_dict[attribute]['max'],key=f'{attribute}-input-field')
                else:
                    l_,cl_,cr_,r_=st.columns(4)
                    indices = list(np.arange(0,int(len(attributes)),round(len(attributes)/4)))
                    for col,i in zip([l_,cl_,cr_,r_],range(len(indices))):
                        with col:
                            if indices[i]!=indices[-1]:
                                attribute_slice = attributes[indices[i]:indices[i+1]]
                            else:
                                attribute_slice = attributes[indices[i]:]
                            for attribute in attribute_slice:
                                with st.container():
                                    val = attribute_df.loc[attribute,topic]
                                    if attribute in ['Hit Points','Magic Points']:
                                        attr_,attr_val_,max_ = st.columns([3,1,1])
                                        with attr_:
                                            st.subheader(f'{attribute}:')
                                        with attr_val_:
                                            st.subheader(val)
                                        if attribute == 'Hit Points':
                                            max_val = int(attribute_df[topic][['Strength','Constitution']].sum()/10)
                                        elif attribute == 'Magic Points':
                                            max_val = int(attribute_df[topic].Power/5)
                                        with max_:
                                            st.subheader(f' / {max_val}')
                                    else:
                                        attr_,attr_val_,button_ = st.columns([3,1,1])
                                        with attr_:
                                            st.subheader(f'{attribute}:')
                                        with attr_val_:
                                            st.subheader(val)
                                        with button_:
                                            if st.button('Roll',key=f'{attribute}-button-roll'):
                                                print(f'Rolling {attribute} at {val}. (Would send to Data)')
            with st.expander(label='Skills',expanded=True):
                skills = skill_df.index.tolist()
                if edit:
                    l_,cl_,cr_,r_=st.columns(4)
                    indices = list(np.arange(0,int(len(skills)),round(len(skills)/4)))
                    for col,i in zip([l_,cl_,cr_,r_],range(len(indices))):
                        with col:
                            if indices[i]!=indices[-1]:
                                skill_slice = skills[indices[i]:indices[i+1]]
                            else:
                                skill_slice = skills[indices[i]:]
                            for skill in skill_slice:
                                with st.container():
                                    if f'{skill}-input-field' not in st.session_state:
                                        st.session_state[f'{skill}-input-field']=int(skill_df.loc[skill,topic])
                                    if min_max_dict[skill]['derived']:
                                        if skill == 'Dodge':
                                            min_value = derive(attribute_df[topic],skill,'min')
                                            max_value = derive(attribute_df[topic],skill,'max')
                                        else:
                                            min_value,max_value=0,100
                                            print(f'Something weird happened switching with {skill}')
                                    else:
                                        min_value,max_value = min_max_dict[skill]['min'],min_max_dict[skill]['max']
                                    if skill_df.loc[skill,topic]<min_value:
                                        skill_df.loc[skill,topic]=min_value
                                    st.number_input(label=skill,min_value=min_value,max_value=max_value,key=f'{skill}-input-field')
                else:
                    l_,cl_,cr_,r_=st.columns(4)
                    indices = list(np.arange(0,int(len(skills)),round(len(skills)/4)))
                    for col,i in zip([l_,cl_,cr_,r_],range(len(indices))):
                        with col:
                            if indices[i]!=indices[-1]:
                                skill_slice = skills[indices[i]:indices[i+1]]
                            else:
                                skill_slice = skills[indices[i]:]
                            for skill in skill_slice:
                                with st.container():
                                    val = skill_df.loc[skill,topic]    
                                    skill_,button_,succ_ = st.columns([3,1,1])
                                    with skill_:
                                        st.write(f'{skill}: {val}')
                                    with button_:
                                        if st.button('Roll',key=f'{skill}-button-roll'):
                                            print(f'Rolling {skill} at {val}. (Would send to Data)')
                                    with succ_:
                                        st.checkbox('Succeeded',value=success_df.loc[skill][topic],key=f'{skill}-succ',label_visibility='hidden')
            with st.expander(label='Biographical',expanded=True):
                left_,right_=st.columns(2)
                img_file_name = wf.loc[topic].img_path.split(',')
                if len(img_file_name)==1:
                    img_path = os.path.join('figs','wiki_topics',img_file_name[0])
                else:
                    img_path = []
                    for img_file_path in img_file_name:
                        path_name = os.path.join('figs','wiki_topics',img_file_path)
                        img_path.append(path_name)
                with left_:
                    st.subheader('In our campaign:')
                    st.write(body)
                    if wf.loc[topic].isna().expanded_info == False:
                        expanded_info = wf.loc[topic].expanded_info
                        st.subheader('Further Information:')
                        st.write(expanded_info)
                with right_:
                    caption_raw = str(wf.loc[topic].caption).split('{}') #{} is just what I chose to use a separator, since it's not likely to appear in normal captioning
                    if len(caption_raw)==1:
                        caption=caption_raw[0]
                    else:
                        caption = []
                        for cap in caption_raw:
                            caption.append(cap)
                    if caption != 'nan':
                        st.image(img_path,caption=caption)
                    else:
                        st.image(img_path)
            if edit:
                with save_:
                    if st.button(label='Save Changes'):
                        for attribute in attributes:
                            attribute_df.loc[attribute,topic] = st.session_state[f'{attribute}-input-field']
                        for skill in skills:
                            skill_df.loc[skill,topic] = st.session_state[f'{skill}-input-field']
                        attribute_df.to_csv('attributes.csv',encoding='utf-8',index=True)
                        skill_df.to_csv('skills.csv',encoding='utf-8',index=True)

        else:
            if topic in img_entries:
                st.title(topic)
                left_,right_=st.columns(2)
                img_file_name = wf.loc[topic].img_path.split(',')
                if len(img_file_name)==1:
                    img_path = os.path.join('figs','wiki_topics',img_file_name[0])
                else:
                    img_path = []
                    for img_file_path in img_file_name:
                        path_name = os.path.join('figs','wiki_topics',img_file_path)
                        img_path.append(path_name)
                with left_:
                    st.subheader('In our campaign:')
                    st.write(body)
                    if wf.loc[topic].isna().expanded_info == False:
                        expanded_info = wf.loc[topic].expanded_info
                        st.subheader('Further Information:')
                        st.write(expanded_info)
                with right_:
                    caption_raw = str(wf.loc[topic].caption).split('{}') #{} is just what I chose to use a separator, since it's not likely to appear in normal captioning
                    if len(caption_raw)==1:
                        caption=caption_raw[0]
                    else:
                        caption = []
                        for cap in caption_raw:
                            caption.append(cap)
                    if caption != 'nan':
                        st.image(img_path,caption=caption)
                    else:
                        st.image(img_path)
            else:
                st.title(topic)
                st.subheader('In our campaign:')
                st.write(body)
                if wf.loc[topic].isna().expanded_info == False:
                    expanded_info = wf.loc[topic].expanded_info
                    st.subheader('Further Information:')
                    st.write(expanded_info)
            if st.checkbox(label='Delete Article',value=False):
                st.error('Are you sure you want to delete this article? There is no going back once this is done.')
                if st.button(label='Confirm Delete',type='primary'):
                    wf.drop(topic,axis=0,inplace=True)
                    wf.to_csv('wiki.csv',encoding='utf-8',index=True)
                    # try:
                    #     all_topics.remove(topic)
                    # except ValueError:
                    #     print('Article removed without being added to all_topics')
                    st.rerun()
            if 'debug' in sys.argv:
                if st.button(label='Wf flow',key='wf_flow_wiki_view'):
                    print(wf.tail(5))
            

#Main loop, where most refreshing happens
def main(wf,filter=None):
    #Session ID needs to be in the main loop to avoid defining the same editor for all users
    ctx = st.runtime.scriptrunner.get_script_run_ctx()
    session_id = ctx.session_id
    # if server_state.get('new_topic')!=None:
    #     # all_topics.append(server_state.new_topic)
    #     server_state['new_topic']=None
    #Used to show the wiki loop is activated--this is for flow control purposes. Only shows in the terminal
    if 'show_flow' in sys.argv:
        print("Wiki Main")
    if server_state.get('open') and session_id == server_state.get('editor') and server_state.get('open_article')!=None:
        topic = server_state.get('open_article')
        display_wiki(topic,wf,edit=True,session_id=session_id)
    else:
###TODO double check timezone adjustments with timestamps
        featured = st.session_state.featured
        featured_cat = wf.loc[featured].category
        if filter==None or filter==featured_cat:
            if filter == None:
                topic_list=wf.index.tolist()
                index = wf.index.get_loc(featured)
            else:
                topic_list = wf[wf.category == filter].index.tolist()
                index = wf[wf.category == filter].index.get_loc(featured)
            topic = st.selectbox(label='Topic',options=topic_list,index=index)
        else:
            topic_list = wf[wf.category == filter].index.tolist()
            if st.session_state.get('persist_topic')!=None and filter==st.session_state.get('persist_cat'):
                index = topic_list.index(st.session_state['persist_topic'])
                topic = st.selectbox(label='Topic',options=topic_list,index=index)
            else:
                topic = st.selectbox(label='Topic',options=topic_list)
        display_wiki(topic,wf)
        if server_state.get('open')!=True:
            if st.button(label='Edit entry',key='edit_widget'):
                server_state['open'],server_state['open_article'],server_state['editor']=True,topic,session_id

if __name__ == "__main__":
    main()

