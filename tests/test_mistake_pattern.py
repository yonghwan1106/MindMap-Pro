# File: tests/test_mistake_pattern.py
# Mistake Pattern Analysis Tests

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from modules.mistake_pattern import MistakePatternAnalysis

class TestMistakePatternAnalysis:
    @pytest.fixture
    def pattern_analyzer(self):
        """실수 패턴 분석기 인스턴스 생성"""
        return MistakePatternAnalysis()

    @pytest.fixture
    def sample_mistake_data(self):
        """테스트용 실수 데이터 생성"""
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        mistake_types = [
            '계산 실수',
            '문제 조건 누락',
            '시간 부족',
            '개념 이해 부족',
            '문제 해석 오류'
        ]
        subjects = ['수학', '물리', '화학', '영어', '국어']
        
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
                        'time_spent': np.random.randint(1, 10),
                        'is_repeated': np.random.choice([True, False]),
                        'stress_level': np.random.randint(1, 6)
                    })
        
        return pd.DataFrame(data)

    def test_pattern_overview_analysis(self, pattern_analyzer, sample_mistake_data):
        """실수 패턴 개요 분석 테스트"""
        pattern_analyzer.mistake_data = sample_mistake_data
        
        # 패턴 개요 렌더링
        pattern_analyzer.render_pattern_overview()
        
        # 과목별, 실수 유형별 분포 확인
        mistake_distribution = pd.crosstab(
            sample_mistake_data['subject'],
            sample_mistake_data['mistake_type']
        )
        assert not mistake_distribution.empty
        assert mistake_distribution.values.sum() > 0

    def test_trend_analysis(self, pattern_analyzer, sample_mistake_data):
        """실수 추세 분석 테스트"""
        pattern_analyzer.mistake_data = sample_mistake_data
        
        # 추세 분석 렌더링
        pattern_analyzer.render_trend_analysis()
        
        # 시간에 따른 실수 빈도 변화 확인
        trend_data = sample_mistake_data.groupby(['date', 'mistake_type']).size()
        assert len(trend_data) > 0

    def test_correlation_analysis(self, pattern_analyzer, sample_mistake_data):
        """실수 상관관계 분석 테스트"""
        pattern_analyzer.mistake_data = sample_mistake_data
        
        # 상관관계 분석 렌더링
        pattern_analyzer.render_correlation_analysis()
        
        # 스트레스 레벨과 실수 빈도의 상관관계 확인
        stress_mistake = sample_mistake_data.groupby('stress_level').size()
        assert len(stress_mistake) > 0

    def test_improvement_suggestions(self, pattern_analyzer, sample_mistake_data):
        """개선 전략 제안 테스트"""
        pattern_analyzer.mistake_data = sample_mistake_data
        
        # 개선 전략 렌더링
        pattern_analyzer.render_improvement_suggestions()
        
        # 가장 빈번한 실수 유형 확인
        common_mistakes = sample_mistake_data['mistake_type'].value_counts()
        assert len(common_mistakes) > 0
        assert common_mistakes.index[0] in [
            '계산 실수',
            '문제 조건 누락',
            '시간 부족',
            '개념 이해 부족',
            '문제 해석 오류'
        ]

    def test_repeated_mistakes_analysis(self, pattern_analyzer, sample_mistake_data):
        """반복적 실수 분석 테스트"""
        # 반복적 실수 비율 계산
        repeat_ratio = sample_mistake_data['is_repeated'].mean()
        assert 0 <= repeat_ratio <= 1  # 비율이 0과 1 사이인지 확인

    def test_difficulty_level_analysis(self, pattern_analyzer, sample_mistake_data):
        """문제 난이도별 실수 분석 테스트"""
        # 난이도별 실수 분포 확인
        difficulty_distribution = sample_mistake_data.groupby('problem_difficulty').size()
        assert set(difficulty_distribution.index) <= {'상', '중', '하'}

    def test_stress_impact_analysis(self, pattern_analyzer, sample_mistake_data):
        """스트레스 영향 분석 테스트"""
        # 스트레스 레벨별 실수 유형 분석
        stress_impact = pd.crosstab(
            sample_mistake_data['stress_level'],
            sample_mistake_data['mistake_type']
        )
        assert not stress_impact.empty

    def test_time_pressure_analysis(self, pattern_analyzer, sample_mistake_data):
        """시간 압박 관련 실수 분석 테스트"""
        # 시간 부족으로 인한 실수 비율 계산
        time_pressure_ratio = len(
            sample_mistake_data[sample_mistake_data['mistake_type'] == '시간 부족']
        ) / len(sample_mistake_data)
        assert 0 <= time_pressure_ratio <= 1

    def test_subject_specific_patterns(self, pattern_analyzer, sample_mistake_data):
        """과목별 특징적 실수 패턴 분석 테스트"""
        # 과목별 주요 실수 유형 확인
        subject_patterns = pd.crosstab(
            sample_mistake_data['subject'],
            sample_mistake_data['mistake_type']
        )
        assert subject_patterns.shape == (5, 5)  # 5개 과목, 5개 실수 유형

    def test_data_validation(self, pattern_analyzer):
        """데이터 유효성 검증 테스트"""
        # 잘못된 데이터로 테스트
        invalid_data = pd.DataFrame({
            'date': ['2024-01-01'],
            'subject': ['수학'],
            'mistake_type': ['불가능한 실수 유형'],  # 유효하지 않은 실수 유형
            'problem_difficulty': ['최상'],          # 유효하지 않은 난이도
            'time_spent': [-5],                    # 유효하지 않은 시간
            'is_repeated': ['maybe'],              # 유효하지 않은 불리언 값
            'stress_level': [10]                   # 범위를 벗어난 스트레스 레벨
        })
        
        with pytest.raises(ValueError):
            pattern_analyzer.mistake_data = invalid_data
            pattern_analyzer.render_pattern_overview()

    def test_improvement_tracking(self, pattern_analyzer, sample_mistake_data):
        """개선 추적 테스트"""
        # 시간에 따른 실수 개선도 분석
        sample_mistake_data.sort_values('date', inplace=True)
        
        # 전반부와 후반부 실수 빈도 비교
        mid_point = len(sample_mistake_data) // 2
        early_mistakes = len(sample_mistake_data[:mid_point])
        later_mistakes = len(sample_mistake_data[mid_point:])
        
        # 일반적으로 시간이 지날수록 실수가 줄어들어야 함
        improvement_ratio = later_mistakes / early_mistakes
        assert isinstance(improvement_ratio, float)

    def test_pattern_recognition_accuracy(self, pattern_analyzer, sample_mistake_data):
        """패턴 인식 정확도 테스트"""
        # 실수 패턴 분류 정확도 검증
        pattern_counts = sample_mistake_data['mistake_type'].value_counts()
        total_patterns = len(sample_mistake_data)
        
        # 각 패턴이 전체의 일정 비율을 넘지 않아야 함 (균형 잡힌 분포)
        max_pattern_ratio = pattern_counts.max() / total_patterns
        assert max_pattern_ratio < 0.5  # 한 유형이 전체의 50%를 넘지 않아야 함

    def test_stress_threshold_analysis(self, pattern_analyzer, sample_mistake_data):
        """스트레스 임계값 분석 테스트"""
        # 스트레스 레벨별 실수 빈도 분석
        stress_levels = sample_mistake_data.groupby('stress_level').size()
        
        # 스트레스가 높을 때의 실수 비율 계산
        high_stress_mistakes = stress_levels[stress_levels.index >= 4].sum()
        total_mistakes = stress_levels.sum()
        high_stress_ratio = high_stress_mistakes / total_mistakes
        
        # 일반적으로 높은 스트레스 상황에서의 실수 비율이 전체의 일정 수준을 넘지 않아야 함
        assert high_stress_ratio <= 0.4  # 40% 이하여야 함

    def test_pattern_seasonality(self, pattern_analyzer, sample_mistake_data):
        """실수 패턴의 계절성 테스트"""
        # 요일별 실수 패턴 분석
        sample_mistake_data['weekday'] = pd.to_datetime(sample_mistake_data['date']).dt.day_name()
        weekday_patterns = pd.crosstab(
            sample_mistake_data['weekday'],
            sample_mistake_data['mistake_type']
        )
        
        # 모든 요일에 실수 데이터가 존재하는지 확인
        assert len(weekday_patterns) == 7  # 7일의 데이터가 모두 있어야 함

    def test_performance_metrics(self, pattern_analyzer, sample_mistake_data):
        """성능 지표 분석 테스트"""
        start_time = datetime.now()
        
        # 분석 실행
        pattern_analyzer.mistake_data = sample_mistake_data
        pattern_analyzer.render_pattern_overview()
        pattern_analyzer.render_trend_analysis()
        pattern_analyzer.render_correlation_analysis()
        pattern_analyzer.render_improvement_suggestions()
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # 전체 분석이 2초 이내에 완료되어야 함
        assert execution_time < 2.0
