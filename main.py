## Different version of the function switcher page in main.py, intended to be more of a splash page with bigger buttons--work in progress
import streamlit as st
import utils.utilities as utl
from streamlit_server_state import server_state
import streamlit_server_state as slss
from views import wiki,handouts, add_article
import sys, os, contextlib,zoneinfo
import pandas as pd
import datetime as dt
#Establishing unique session identifier
ctx = st.runtime.scriptrunner.get_script_run_ctx()
session_id = ctx.session_id

#Featured article (or default if you prefer that term)
featured = 'Honey Charles'
# set webpage icon and layout
st.set_page_config(
    page_title="Echoes of the Past Wiki",
    page_icon="./figs/eldersign.png",#, actual filepath is in navbar_components in utilities.py
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
    }
)
#Used to check in the terminal when the script has run top-down
if 'show_flow' in sys.argv:
    print('---------------------------')
    print('Main Top')
#This CSS hides the 'link anchor' icons that I don't use
st.markdown("""
    <style>
    /* Hide the link button */
    .stApp a:first-child {
        display: none;
    }
    
    .css-15zrgzn {display: none}
    .css-eczf16 {display: none}
    .css-jn99sy {display: none}
    </style>
    """, unsafe_allow_html=True)

#Category filters
# cats = ['people','organizations','droids','objects','planets_and_regions','locations','ships','concepts','other_entities']
routes = ['player_characters','non-player_characters','other','handouts','add_article']#cats + 
# #Dictionary stores last index for non-featured categories, prevents random assignment.
# st.session_state['last_index']={}
# for non_feat in [i.replace('_',' ') for i in cats]:
#     st.session_state['last_index'][non_feat]=None


def navigation():
    #The wiki dataframe has to be held in the memory of the navigation loop, otherwise new articles cannot be added without a complete server refresh. I absolutely cannot find a way to force it to reload in a more efficient way.
    wf = pd.read_csv('wiki.csv',encoding='utf-8',index_col='Entry')
    # #Makes a dataframe of time_locked articles and checks if any of them are ready to go live #TODO Adapt to live button press and CoC environment
    # if os.path.isfile('time_locked.csv'):
    #     time_locked = pd.read_csv('time_locked.csv',encoding='utf-8',index_col='Entry',keep_default_na=False)
    #     going_live = [t < dt.datetime.now().timestamp() for t in time_locked.go_live.values.tolist()]
    #     if True in going_live:
    #         to_merge = time_locked[going_live].drop('go_live',axis=1)
    #         time_locked = time_locked[[t is False for t in going_live]]
    #         if len(time_locked) > 0:
    #             time_locked.to_csv('time_locked.csv',encoding='utf-8',index=True)
    #         else:
    #             os.unlink('time_locked.csv')
    #         wf = wf.reset_index().merge(to_merge.reset_index(),how='outer').set_index('Entry')
    #         wf.to_csv('wiki.csv',encoding='utf-8',index=True)
    wf=wf[['body','expanded_info','img_path','caption','category','alias']]
    #Used to show the main loop is activated--this is for flow control purposes. Only shows in the terminal
    if 'show_flow' in sys.argv:
        print("Nav Loop Init")
    if 'route' not in st.session_state:
        st.session_state.route='player_characters'
    if 'featured' not in st.session_state:
        st.session_state.featured = featured
    route = st.session_state.route
    if 'show_flow' in sys.argv:
        st.write(route)
        print(route)
    with st.sidebar:
        st.subheader('Navigation')
        for route_ in routes:
            route_name = route_.replace('_',' ').title()
            # print(route_name)
            if st.button(label=route_name,key=f'{route_}-sidebar'):
                st.session_state.route=route_
                if route_=='add_article':
                    server_state['open'],server_state['editor'] = True,session_id
                st.rerun()
        if server_state.get('open'):
            tooltip = 'Reset edit state after closing/reloading.'
            if st.button(label='EMERGENCY RESET',help=tooltip,type='primary'):
                st.session_state.route = 'player_characters'
                server_state['open'],server_state['open_article'],server_state['editor'] = False,None,None
                # st.rerun()
        if 'debug' in sys.argv:
            if st.button(label='debug',key='debug'):
                print('---Begin Debug Message----')
                print('filtered session state dict')
                for key in st.session_state:
                    if key.replace('-sidebar','') not in routes+['edit_widget','debug','save_widget','discard_widget']:
                        print(f'{key}: {st.session_state[key]}')
                print('server state dict')
                for key in server_state:
                    print(f'{key}: {server_state[key]}')
                print(f'Session ID: {session_id}')
                print('----End Debug Message-----')
            if st.button(label='whole session dict'):
                print(st.session_state)
            if st.button(label='Wf flow'):
                print(wf.tail(5))
    if route == 'player_characters':
        wiki.main(wf,filter='pcs')
    elif route == 'non-player_characters':
        wiki.main(wf,filter='npcs')
    elif route == 'other':
        wiki.main(wf,filter='other')
    elif route == 'handouts':
        handouts.main()
    else:
        # st.write('Something went wrong. The app seems to have lost your navigation input, so you have been sent back to the main page.')
        st.session_state.route = 'player_characters'
        wiki.main(wf)




with contextlib.suppress(slss.session_info.NoSessionError):
    navigation()