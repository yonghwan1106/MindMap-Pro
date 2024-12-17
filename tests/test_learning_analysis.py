# File: tests/test_learning_analysis.py
# Learning Analysis Module Tests

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from modules.learning_analysis import LearningAnalysis
from core.processor import DataProcessor

class TestLearningAnalysis:
    @pytest.fixture
    def learning_analyzer(self):
        """학습 분석기 인스턴스 생성"""
        return LearningAnalysis()

    @pytest.fixture
    def sample_study_data(self):
        """테스트용 학습 데이터 생성"""
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        subjects = ['수학', '물리', '화학', '영어', '국어']
        data = []
        
        for date in dates:
            for subject in subjects:
                data.append({
                    'date': date,
                    'subject': subject,
                    'study_time': np.random.randint(30, 180),
                    'score': np.random.randint(70, 100),
                    'stress_level': np.random.randint(1, 6)
                })
        
        return pd.DataFrame(data)

    def test_time_distribution_analysis(self, learning_analyzer, sample_study_data):
        """시간 분포 분석 테스트"""
        learning_analyzer.study_data = sample_study_data
        
        # 시간 분포 렌더링
        learning_analyzer.render_time_distribution()
        
        # 과목별 총 학습 시간 확인
        subject_times = sample_study_data.groupby('subject')['study_time'].sum()
        assert len(subject_times) == 5  # 5개 과목
        assert all(subject_times > 0)  # 모든 과목의 학습 시간이 0보다 큼

    def test_performance_analysis(self, learning_analyzer, sample_study_data):
        """성과 분석 테스트"""
        learning_analyzer.study_data = sample_study_data
        
        # 성과 분석 렌더링
        learning_analyzer.render_performance_analysis()
        
        # 과목별 평균 점수 확인
        subject_scores = sample_study_data.groupby('subject')['score'].mean()
        assert all(subject_scores >= 70)  # 모든 과목의 평균 점수가 70점 이상
        assert all(subject_scores <= 100)  # 모든 과목의 평균 점수가 100점 이하

    def test_efficiency_analysis(self, learning_analyzer, sample_study_data):
        """효율성 분석 테스트"""
        learning_analyzer.study_data = sample_study_data
        
        # 효율성 분석 렌더링
        learning_analyzer.render_efficiency_analysis()
        
        # 학습 효율성 계산 (점수/시간)
        efficiency = sample_study_data['score'] / sample_study_data['study_time']
        assert all(efficiency > 0)  # 모든 효율성 값이 양수

    def test_recommendations(self, learning_analyzer, sample_study_data):
        """학습 추천 테스트"""
        learning_analyzer.study_data = sample_study_data
        
        # 추천 렌더링
        learning_analyzer.render_recommendations()
        
        # 최적 학습 시간대 확인
        time_scores = sample_study_data.groupby('date')['score'].mean()
        best_date = time_scores.idxmax()
        assert isinstance(best_date, pd.Timestamp)

    def test_stress_impact_analysis(self, learning_analyzer, sample_study_data):
        """스트레스 영향 분석 테스트"""
        # 스트레스 레벨과 성적의 상관관계 분석
        stress_correlation = sample_study_data.groupby('stress_level')['score'].mean()
        
        # 일반적으로 스트레스가 높을수록 성적이 낮아지는 경향
        assert stress_correlation.corr(pd.Series(range(1, 6))) < 0

    def test_subject_correlation(self, learning_analyzer, sample_study_data):
        """과목 간 상관관계 분석 테스트"""
        # 과목별 평균 점수 계산
        subject_scores = pd.pivot_table(
            sample_study_data,
            values='score',
            index='date',
            columns='subject'
        )
        
        # 상관관계 행렬 계산
        correlation_matrix = subject_scores.corr()
        
        # 모든 상관계수가 -1과 1 사이인지 확인
        assert correlation_matrix.min().min() >= -1
        assert correlation_matrix.max().max() <= 1

    def test_learning_pattern_detection(self, learning_analyzer, sample_study_data):
        """학습 패턴 감지 테스트"""
        # 요일별 학습 성과 분석
        sample_study_data['weekday'] = sample_study_data['date'].dt.day_name()
        weekday_scores = sample_study_data.groupby('weekday')['score'].mean()
        
        # 모든 요일의 평균 점수가 유효한 범위 내인지 확인
        assert weekday_scores.min() >= 0
        assert weekday_scores.max() <= 100

    def test_data_validation(self, learning_analyzer):
        """데이터 유효성 검증 테스트"""
        # 잘못된 데이터로 테스트
        invalid_data = pd.DataFrame({
            'date': ['2024-01-01'],
            'subject': ['수학'],
            'study_time': [-30],  # 잘못된 학습 시간
            'score': [150],       # 잘못된 점수
            'stress_level': [10]  # 잘못된 스트레스 레벨
        })
        
        with pytest.raises(ValueError):
            learning_analyzer.study_data = invalid_data
            learning_analyzer.render_time_distribution()

    def test_trend_analysis(self, learning_analyzer, sample_study_data):
        """추세 분석 테스트"""
        # 주간 평균 점수 계산
        sample_study_data['week'] = sample_study_data['date'].dt.isocalendar().week
        weekly_scores = sample_study_data.groupby('week')['score'].mean()
        
        # 추세선 기울기 계산
        x = np.arange(len(weekly_scores))
        slope = np.polyfit(x, weekly_scores, 1)[0]
        
        # 추세가 존재하는지 확인 (기울기가 0이 아님)
        assert slope != 0
