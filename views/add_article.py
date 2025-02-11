import streamlit as st
import pandas as pd
from utils.utils import *
import os,sys, zoneinfo, shelve
from datetime import datetime, timedelta
from streamlit_server_state import server_state
pd.set_option('mode.chained_assignment', None)

timezonelist = sorted(list(zoneinfo.available_timezones()))

def get_offset(zone):
    offset = datetime.now(tz=zoneinfo.ZoneInfo(zone)).strftime('%z')
    return offset

sw_zone = zoneinfo.ZoneInfo(key='America/Montreal')
with shelve.open('../discord-bot-live/vars') as f:
    sw_time = datetime.fromtimestamp(f['call of cthulhu']).replace(tzinfo=sw_zone)

def add_article_display(add=False):
    ## The dataframe needs to be as current as possible. Keeping it outside the function makes it overwrite all new articles, only keeping the newest one.
    wf = pd.read_csv('wiki.csv',encoding='utf-8',index_col='Entry')
    wf=wf[['body','expanded_info','img_path','caption','category','alias']]
    if 'show_flow' in sys.argv:
        print("Add Article Display Function")
    if add:
        if 'show_flow' in sys.argv:
            print('Editor add view')
        all_cats = wf.category.unique().tolist()
        st.title('Adding new article.')
        article_name_,alias_,article_cat_=st.columns([4,2,1])
        with article_name_:
            entry = st.text_input(label='Article Name',help='The actual name of the article and primary index. This should be a formal name. Avoid abbreviations even for titles like Doctor or Sergeant.')
        with alias_:
            alias = st.text_input(label='Alias',help='Alternative names, including only first and last names, that might refer to the article. This is for the purposes of searching and highlighting.')
        with article_cat_:
            article_cat = st.selectbox(label='Article Category',options=all_cats,help='The best category fit for the article you are adding.')
        body = st.text_area(label='Article body text',help='The main text for the article. This section is typically used for information that is relevant to our specific campaign.')
        expanded_info = st.text_area(label='Expanded Information',help='This is text that is supplemental to the article topic. Typically this is extra info about a topic given to us by the GM but not necessarily pertinent OR information from outside sources like mainline wikis.')
        st.write('Once the article is written and saved into the database, you may then add photos to it via the edit function in the main wiki view.')
        time_lock = False
        if st.checkbox(label='Time lock article'):
            time_lock = True
            date_,time_,zone_ = st.columns(3)
            with date_:
                livedate = st.date_input(label='Go live when?')
            with time_:
                livetime = st.time_input(label='What time?')
            with zone_:
                tz = st.selectbox(label='Timezone?',options=timezonelist,index=589)
                tz_object=zoneinfo.ZoneInfo(key=tz)
                offset = get_offset(tz)
            golive = datetime(month=livedate.month,day=livedate.day,year=livedate.year,hour=livetime.hour,minute=livetime.minute,tzinfo=zoneinfo.ZoneInfo(tz))
            sw_time_shift = sw_time.astimezone(tz_object)
            twelve_hour,sw_twelve_hour,sw_offset_shift = int(golive.strftime("%I")),int(sw_time_shift.strftime("%I")),get_offset(sw_time_shift.tzinfo.key)
            st.write(f'Going live on {golive.strftime("%A")}, {golive.strftime("%B")} {golive.day}, {golive.year}, at {twelve_hour} {golive.strftime("%p")} (UTC {offset}). Our next game is on {sw_time_shift.strftime("%A")}, {sw_time_shift.strftime("%B")} {sw_time_shift.day}, {sw_time_shift.year}, at {sw_twelve_hour} {sw_time_shift.strftime("%p")} (UTC {sw_offset_shift}).')
        save_,discard_ = st.columns(2)
        with save_:
            if st.button(label='Save Changes',key='save_widget'):
                if entry=='' or body=='':
                    st.error('Cannot add empty value. The minimum requirement to add an entry is the "Article Name" and "Body" fields must not be empty.')
                else:
                    new_df_dict = {}
                    for info_name,info in zip(['Entry','alias','category','body','expanded_info'],[entry,alias,article_cat,body,expanded_info]):
                        new_df_dict[info_name]=info
                    new_df = pd.DataFrame.from_dict(new_df_dict,orient='index').T
                    if new_df.alias.isna().values[0]:
                        new_df.alias = new_df.index.values
                    if time_lock:
                        new_df['go_live'] = golive.timestamp()
                        if os.path.isfile('time_locked.csv'):
                            time_locked_df = pd.read_csv('time_locked.csv',encoding='utf-8',keep_default_na=False)
                            time_locked_merged = time_locked_df.merge(new_df,'outer')
                            time_locked_merged.to_csv('time_locked.csv',encoding='utf-8',index=False)
                        else:
                            new_df.to_csv('time_locked.csv',encoding='utf-8',index=False)
                    else:
                        merge_df = pd.merge(wf,new_df)
                        if wf.index.name == 'Entry':
                            wf.reset_index(inplace=True)
                        merge_df = wf.merge(new_df,'outer').set_index('Entry')
                        merge_df.to_csv('wiki.csv',encoding='utf-8',index=True)
                        server_state['new_topic']=entry
                    server_state['open'],server_state['open_article'],server_state['editor'] = False,None,None
                    st.rerun()
        with discard_:
            if st.button(label='Discard Changes',key='discard_widget'):
                server_state['open'],server_state['open_article'],server_state['editor'] = False,None,None #This line has to run last in this widget--I don't know why. All loops refresh after this line.
    else: 
        if 'show_flow' in sys.argv:
            print('Non-editor add view - surprised')
        st.title('Someone else is adding a new article.')
        st.write('In order to avoid server and database errors, when one person opens the wiki to make edits or add new ones, any changes by other users are blocked. This is to avoid confusion and corrupting files.\n\nYou honestly should not have reached this page. It is possible the sidebar loaded before someone opened the menu to add an article, but it is more likely someone just loaded the add article page while you had it open and took control from you. A simple reload should clear things up!')
    if 'debug' in sys.argv:
        if st.button(label='debug',key='debug_edit_view'):
            for info_name,info in zip(['entry','alias','article_cat','body','expanded_info'],[entry,alias,article_cat,body,expanded_info]):
                print(f'{info_name}:{info}')

#Main loop, where most refreshing happens
def main(add=False):
    #Session ID needs to be in the main loop to avoid defining the same editor for all users
    ctx = st.runtime.scriptrunner.get_script_run_ctx()
    session_id = ctx.session_id
    #Used to show the wiki loop is activated--this is for flow control purposes. Only shows in the terminal
    if 'show_flow' in sys.argv:
        print("Add Article Main")
    #Actual editing interface, only accessible if session_id matches the one who clicked the button.
    if add and server_state.get('open') and session_id == server_state.get('editor'):
        add_article_display(add=True)
    else:
        add_article_display()


if __name__ == "__main__":
    main()

