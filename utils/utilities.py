import streamlit as st
import base64
from streamlit.components.v1 import html
import time
from PATHS import NAVBAR_PATHS


import pathlib
from typing import BinaryIO, Union

File = Union[pathlib.Path, str, BinaryIO]


class SessionState:
    def __init__(self, state):
        for key, val in state.items():
            setattr(self, key, val)

    def update(self, state):
        for key, val in state.items():
            try:
                getattr(self, key)
            except AttributeError:
                setattr(self, key, val)


def get_session_id() -> str:
    ctx = st.scriptrunner.add_script_run_ctx()
    session_id: str = ctx.streamlit_script_run_ctx.session_id

    return session_id


def get_session(session_id: str = None):
    if session_id is None:
        session_id = get_session_id()

    session_info = st.server.server.Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise ValueError("No session info found")

    report_session = session_info.session

    return report_session


def session_state(**state):
    session = get_session()

    try:
        session._custom_session_state.update(state)
    except AttributeError:
        session._custom_session_state = SessionState(state)

    return session._custom_session_state


def inject_custom_css():
    with open('assets/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def get_current_route():
    try:
        return st.experimental_get_query_params()['app'][0]
    except:
        return None


def navbar_component():
    with open("./figs/echani_logo.png", "rb") as image_file:
        image_as_base64 = base64.b64encode(image_file.read())

    navbar_items = ''
    for key, value in NAVBAR_PATHS.items():
        navbar_items += (f'<a class="navitem" href="/?app={value}">{key}</a>')

    # settings_items = ''
    # for key, value in SETTINGS.items():
    #     settings_items += (
    #         f'<a href="/?nav={value}" class="settingsNav">{key}</a>')

    component = rf'''
            <nav class="container navbar" id="navbar">
                <ul class="navlist">
                {navbar_items}
                </ul>
                <div class="dropdown" id="settingsDropDown">
                    <img class="dropbtn" src="data:image/png;base64, {image_as_base64.decode("utf-8")}"/>
                </div>
            </nav>
            '''

    st.markdown(component, unsafe_allow_html=True)
    js = '''
    <script>
        // navbar elements
        var navigationTabs = window.parent.document.getElementsByClassName("navitem");
        var cleanNavbar = function(navigation_element) {
            navigation_element.removeAttribute('target')
        }
        
        for (var i = 0; i < navigationTabs.length; i++) {
            cleanNavbar(navigationTabs[i]);
        }
        
        // Dropdown hide / show
        var dropdown = window.parent.document.getElementById("settingsDropDown");
        dropdown.onclick = function() {
            var dropWindow = window.parent.document.getElementById("myDropdown");
            if (dropWindow.style.visibility == "hidden"){
                dropWindow.style.visibility = "visible";
            }else{
                dropWindow.style.visibility = "hidden";
            }
        };
        
        var settingsNavs = window.parent.document.getElementsByClassName("settingsNav");
        var cleanSettings = function(navigation_element) {
            navigation_element.removeAttribute('target')
        }
        
        for (var i = 0; i < settingsNavs.length; i++) {
            cleanSettings(settingsNavs[i]);
        }
    </script>
    '''
    html(js)