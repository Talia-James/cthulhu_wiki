import streamlit as st
import os
import pandas as pd
from io import StringIO

cwd = os.getcwd()
hfpath = os.path.join(cwd,'figs/handouts/handouts.csv')
if os.path.exists(hfpath):
    initialized = True
else:
    initialized=False


def main():
    if initialized==False:
        st.write("There don't seem to be any handouts uploaded yet. Try adding one!")
    else:
        hf = pd.read_csv(hfpath,encoding='utf-8',index_col='name')
        handout_list = hf.index.tolist()
        handout = st.selectbox(label='Handout',options=handout_list)
        handout_name,fp = hf.loc[handout].name,hf.loc[handout].filepath
        handout_fp = os.path.join(cwd,'figs',fp)
        st.title(handout_name)
        st.image(handout_fp)
    upload_,delete_ = st.columns(2)
    with upload_:
        if st.checkbox(label='Upload New Handout'):
            new_handout_name = st.text_input(label='Give it a name first')
            if new_handout_name != '':
                uploaded_file = st.file_uploader("Choose a file")
                if uploaded_file is not None:
                    bytes_data = uploaded_file.getvalue()
                    save_path = os.path.join(cwd,'figs/handouts',uploaded_file.name)
                    with open(save_path,'wb') as f:
                        f.write(bytes_data)
                    new_hf = pd.DataFrame({'name':new_handout_name,'filepath':os.path.join('handouts',uploaded_file.name)},index=['name'],columns=['name','filepath'])
                    hf.reset_index(inplace=True)
                    hf = pd.merge(hf,new_hf,how='outer')
                    hf.to_csv(hfpath,encoding='utf-8',index=False)
    with delete_:
        if st.checkbox(label='Delete Handout'):
            if st.button(label='Confirm Delete',type='primary'):
                hf.drop(handout,axis=0,inplace=True)
                hf.to_csv(hfpath,encoding='utf-8',index=True)
                os.unlink(handout_fp)
                st.rerun()






if __name__ == "__main__":
    main()

