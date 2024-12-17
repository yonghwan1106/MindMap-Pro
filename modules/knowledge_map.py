import streamlit as st
import networkx as nx
import pandas as pd
import plotly.graph_objects as go
from core.processor import DataProcessor
from core.visualizer import Visualizer

class KnowledgeMap:
    def __init__(self):
        self.processor = DataProcessor()
        self.visualizer = Visualizer()
        self.G = nx.Graph()

    def create_new_map(self):
        st.subheader("새로운 지식맵 만들기")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            subject = st.selectbox(
                "과목 선택",
                ["수학", "물리", "화학", "생물", "지구과학", "국어", "영어"]
            )
            
            concept = st.text_input("새로운 개념 추가")
            related_concepts = st.multiselect(
                "연관 개념 선택",
                self.G.nodes() if self.G.nodes() else ["아직 추가된 개념이 없습니다"]
            )
            
            if st.button("개념 추가"):
                if concept:
                    self.G.add_node(concept, subject=subject)
                    for related in related_concepts:
                        self.G.add_edge(concept, related)
                    st.success(f"'{concept}' 개념이 추가되었습니다!")

        with col2:
            st.write("### 빠른 도움말")
            st.info("""
            1. 과목을 선택하세요
            2. 새로운 개념을 입력하세요
            3. 기존 개념과의 연관성을 선택하세요
            4. '개념 추가' 버튼을 클릭하세요
            """)

    def visualize_map(self):
        if not self.G.nodes():
            st.warning("아직 추가된 개념이 없습니다. 새로운 개념을 추가해주세요.")
            return

        # 노드 색상 설정
        color_map = {
            "수학": "#FF6B6B",
            "물리": "#4ECDC4",
            "화학": "#45B7D1",
            "생물": "#96CEB4",
            "지구과학": "#FFEEAD",
            "국어": "#D4A5A5",
            "영어": "#9FA4C4"
        }

        # 노드 위치 계산
        pos = nx.spring_layout(self.G)
        
        # Plotly 그래프 생성
        edge_trace = go.Scatter(
            x=[], y=[], 
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        for edge in self.G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += (x0, x1, None)
            edge_trace['y'] += (y0, y1, None)

        node_trace = go.Scatter(
            x=[], y=[],
            text=[],
            mode='markers+text',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=20,
                line_width=2))

        for node in self.G.nodes():
            x, y = pos[node]
            node_trace['x'] += (x,)
            node_trace['y'] += (y,)
            node_trace['text'] += (node,)

        fig = go.Figure(data=[edge_trace, node_trace],
                     layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                      )

        st.plotly_chart(fig, use_container_width=True)

    def render(self):
        st.write("## 지식맵 관리")
        
        tab1, tab2 = st.tabs(["지식맵 생성", "지식맵 보기"])
        
        with tab1:
            self.create_new_map()
            
        with tab2:
            self.visualize_map()
