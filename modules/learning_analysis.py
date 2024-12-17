# File: modules/learning_analysis.py
# Learning Analysis Module for MindMap Pro

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from core.processor import DataProcessor

class LearningAnalysis:
    def __init__(self):
        self.processor = DataProcessor()
        self.initialize_sample_data()

    def initialize_sample_data(self):
        """샘플 학습 데이터 초기화"""
        # 학습 시간 데이터
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        subjects = ['수학', '물리', '화학', '영어', '국어']
        
        data = []
        for date in dates:
            for subject in subjects:
                study_time = np.random.randint(0, 180)  # 0-180분
                score = np.random.randint(70, 100)  # 70-100점
                data.append({
                    'date': date,
                    'subject': subject,
                    'study_time': study_time,
                    'score': score
                })
        
        self.study_data = pd.DataFrame(data)

    def render_time_distribution(self):
        """학습 시간 분포 시각화"""
        st.subheader("과목별 학습 시간 분포")
        
        fig = px.bar(
            self.study_data.groupby('subject')['study_time'].sum().reset_index(),
            x='subject',
            y='study_time',
            color='subject',
            title='과목별 총 학습 시간 (분)'
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_performance_analysis(self):
        """성과 분석 시각화"""
        st.subheader("학습 성과 분석")
        
        # 과목별 평균 점수
        fig_scores = px.line(
            self.study_data.groupby(['date', 'subject'])['score'].mean().reset_index(),
            x='date',
            y='score',
            color='subject',
            title='과목별 성적 추이'
        )
        st.plotly_chart(fig_scores, use_container_width=True)

    def render_efficiency_analysis(self):
        """학습 효율성 분석"""
        st.subheader("학습 효율성 분석")
        
        efficiency_data = self.study_data.groupby('subject').agg({
            'study_time': 'sum',
            'score': 'mean'
        }).reset_index()
        
        efficiency_data['efficiency'] = efficiency_data['score'] / (efficiency_data['study_time'] / 60)
        
        fig = px.scatter(
            efficiency_data,
            x='study_time',
            y='score',
            size='efficiency',
            color='subject',
            text='subject',
            title='학습 시간 대비 성과 분석'
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_recommendations(self):
        """학습 추천 제공"""
        st.subheader("맞춤형 학습 추천")
        
        # 효율성이 가장 높은 과목 찾기
        efficiency_data = self.study_data.groupby('subject').agg({
            'study_time': 'sum',
            'score': 'mean'
        })
        efficiency_data['efficiency'] = efficiency_data['score'] / (efficiency_data['study_time'] / 60)
        best_subject = efficiency_data['efficiency'].idxmax()
        
        # 추천 사항 표시
        st.info(f"""
        📊 학습 패턴 분석 결과:
        - 가장 효율적인 과목: {best_subject}
        - 추천 학습 시간: 1회 50분 + 10분 휴식
        - 최적 학습 시간대: 오전 9-11시, 오후 3-5시
        """)

    def render(self):
        """메인 렌더링 함수"""
        st.write("## 학습 현황 분석")
        
        # 기간 선택
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "시작일",
                datetime.now() - timedelta(days=30)
            )
        with col2:
            end_date = st.date_input(
                "종료일",
                datetime.now()
            )

        # 분석 탭
        tab1, tab2, tab3, tab4 = st.tabs([
            "시간 분포",
            "성과 분석",
            "효율성 분석",
            "학습 추천"
        ])
        
        with tab1:
            self.render_time_distribution()
        with tab2:
            self.render_performance_analysis()
        with tab3:
            self.render_efficiency_analysis()
        with tab4:
            self.render_recommendations()

        # 상세 데이터 확인
        if st.checkbox("상세 데이터 보기"):
            st.dataframe(
                self.study_data.sort_values('date', ascending=False),
                use_container_width=True
            )
