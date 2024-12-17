# File: main.py
# Main Application File for MindMap Pro

import streamlit as st
import pandas as pd
import networkx as nx
from modules.auth import check_authentication
from modules.knowledge_map import KnowledgeMap
from modules.learning_analysis import LearningAnalysis
from core.processor import DataProcessor
from core.visualizer import Visualizer

# Page configuration
st.set_page_config(
    page_title="MindMap Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'knowledge_map' not in st.session_state:
    st.session_state.knowledge_map = None

def main():
    # Sidebar
    with st.sidebar:
        st.title("MindMap Pro")
        st.subheader("상위권 학습 컴패니언")
        
        if not st.session_state.authenticated:
            with st.form("login_form"):
                username = st.text_input("사용자명")
                password = st.text_input("비밀번호", type="password")
                submit = st.form_submit_button("로그인")
                
                if submit:
                    if check_authentication(username, password):
                        st.session_state.authenticated = True
                        st.session_state.current_user = username
                        st.success("로그인 성공!")
                        st.rerun()
        else:
            st.write(f"환영합니다, {st.session_state.current_user}님!")
            if st.button("로그아웃"):
                st.session_state.authenticated = False
                st.session_state.current_user = None
                st.rerun()

    # Main content
    if st.session_state.authenticated:
        tabs = st.tabs(["지식맵", "학습현황", "오답노트"])
        
        with tabs[0]:
            st.header("지식맵")
            knowledge_map = KnowledgeMap()
            knowledge_map.render()
            
        with tabs[1]:
            st.header("학습현황")
            learning_analysis = LearningAnalysis()
            learning_analysis.render()
            
        with tabs[2]:
            st.header("오답노트")
            st.write("오답 패턴 분석 기능 구현 예정")
    else:
        st.title("MindMap Pro에 오신 것을 환영합니다")
        st.write("로그인하여 서비스를 이용해주세요.")

if __name__ == "__main__":
    main()
