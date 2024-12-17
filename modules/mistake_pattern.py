# File: modules/mistake_pattern.py
# Mistake Pattern Analysis Module for MindMap Pro

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from core.processor import DataProcessor

class MistakePatternAnalysis:
    def __init__(self):
        self.processor = DataProcessor()
        self.initialize_sample_data()
        
    def initialize_sample_data(self):
        """샘플 오답 데이터 초기화"""
        mistake_types = [
            '계산 실수',
            '문제 조건 누락',
            '시간 부족',
            '개념 이해 부족',
            '문제 해석 오류'
        ]
        
        subjects = ['수학', '물리', '화학', '영어', '국어']
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        
        data = []
        for date in dates:
            for subject in subjects:
                # 각 과목별로 1-3개의 실수 생성
                for _ in range(np.random.randint(1, 4)):
                    data.append({
                        'date': date,
                        'subject': subject,
                        'mistake_type': np.random.choice(mistake_types),
                        'problem_difficulty': np.random.choice(['상', '중', '하']),
                        'time_spent': np.random.randint(1, 10),  # 문제 풀이 시간(분)
                        'is_repeated': np.random.choice([True, False]),
                        'stress_level': np.random.randint(1, 6)  # 스트레스 레벨 (1-5)
                    })
        
        self.mistake_data = pd.DataFrame(data)

    def render_pattern_overview(self):
        """실수 패턴 개요 시각화"""
        st.subheader("실수 패턴 분석")
        
        # 과목별, 실수 유형별 히트맵
        pivot_data = pd.crosstab(
            self.mistake_data['subject'],
            self.mistake_data['mistake_type']
        )
        
        fig = px.imshow(
            pivot_data,
            labels=dict(x="실수 유형", y="과목", color="빈도"),
            title="과목별 실수 유형 분포"
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_trend_analysis(self):
        """실수 추세 분석"""
        st.subheader("실수 패턴 추세")
        
        # 시간에 따른 실수 빈도 변화
        trend_data = self.mistake_data.groupby(['date', 'mistake_type']).size().reset_index(name='count')
        
        fig = px.line(
            trend_data,
            x='date',
            y='count',
            color='mistake_type',
            title='실수 유형별 추세'
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_correlation_analysis(self):
        """실수 상관관계 분석"""
        st.subheader("실수 요인 분석")
        
        # 스트레스 레벨과 실수 빈도의 상관관계
        stress_mistake = self.mistake_data.groupby('stress_level').size().reset_index(name='mistake_count')
        
        fig = px.scatter(
            stress_mistake,
            x='stress_level',
            y='mistake_count',
            title='스트레스 레벨과 실수 빈도의 관계',
            trendline="ols"
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_improvement_suggestions(self):
        """개선 전략 제안"""
        st.subheader("맞춤형 개선 전략")
        
        # 가장 빈번한 실수 유형 파악
        common_mistakes = self.mistake_data['mistake_type'].value_counts()
        primary_mistake = common_mistakes.index[0]
        
        # 실수가 가장 많은 과목 파악
        subject_mistakes = self.mistake_data['subject'].value_counts()
        challenging_subject = subject_mistakes.index[0]
        
        # 개선 전략 제시
        st.info(f"""
        📌 분석 결과 기반 개선 전략:
        
        주요 실수 유형: {primary_mistake}
        가장 주의가 필요한 과목: {challenging_subject}
        
        개선 전략:
        1. 문제 풀이 전 체크리스트 활용
        2. 시간 관리 전략 수립
        3. 스트레스 관리 방안 마련
        
        다음 학습 시 중점 사항:
        - 문제 조건을 형광펜으로 표시
        - 중간 계산 과정 한 번 더 검토
        - 시험 종료 5분 전 답안 최종 검토
        """)

    def render(self):
        """메인 렌더링 함수"""
        st.write("## 오답 패턴 분석")
        
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
            "패턴 개요",
            "추세 분석",
            "요인 분석",
            "개선 전략"
        ])
        
        with tab1:
            self.render_pattern_overview()
        with tab2:
            self.render_trend_analysis()
        with tab3:
            self.render_correlation_analysis()
        with tab4:
            self.render_improvement_suggestions()

        # 상세 데이터 확인
        if st.checkbox("상세 데이터 보기"):
            st.dataframe(
                self.mistake_data.sort_values('date', ascending=False),
                use_container_width=True
            )
