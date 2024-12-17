# File: core/analysis.py
# Data Analysis Module for MindMap Pro

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class LearningAnalyzer:
    def __init__(self, db_manager):
        self.db = db_manager
        self.scaler = StandardScaler()

    def analyze_study_patterns(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """학습 패턴 종합 분석"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 기본 통계 데이터 수집
        stats = self.db.get_study_statistics(user_id, start_date, end_date)
        patterns = self._identify_study_patterns(stats)
        efficiency = self.db.get_learning_efficiency(user_id)
        
        return {
            'statistics': stats,
            'patterns': patterns,
            'efficiency': efficiency,
            'recommendations': self._generate_recommendations(patterns, efficiency)
        }

    def _identify_study_patterns(self, stats: List[Dict]) -> Dict[str, Any]:
        """학습 패턴 식별"""
        if not stats:
            return {}
            
        df = pd.DataFrame(stats)
        patterns = {
            'most_studied': df.loc[df['total_time'].idxmax()]['subject'],
            'most_efficient': df.loc[df['avg_score'].idxmax()]['subject'],
            'stress_factors': self._analyze_stress_factors(df),
            'optimal_sessions': self._find_optimal_session_length(df)
        }
        
        return patterns

    def _analyze_stress_factors(self, df: pd.DataFrame) -> Dict[str, Any]:
        """스트레스 요인 분석"""
        stress_correlation = df['avg_stress'].corr(df['avg_score'])
        high_stress_subjects = df[df['avg_stress'] > df['avg_stress'].mean()]['subject'].tolist()
        
        return {
            'stress_impact': stress_correlation,
            'high_stress_subjects': high_stress_subjects,
            'optimal_stress_level': self._find_optimal_stress_level(df)
        }

    def _find_optimal_session_length(self, df: pd.DataFrame) -> int:
        """최적 학습 세션 길이 분석"""
        if 'avg_time' in df.columns and 'avg_score' in df.columns:
            scores = df['avg_score'].values.reshape(-1, 1)
            times = df['avg_time'].values.reshape(-1, 1)
            
            if len(scores) > 1:
                kmeans = KMeans(n_clusters=2, random_state=42)
                kmeans.fit(np.column_stack((times, scores)))
                
                cluster_centers = kmeans.cluster_centers_
                optimal_cluster = cluster_centers[cluster_centers[:, 1].argmax()]
                
                return int(optimal_cluster[0])
                
        return 45  # 기본값으로 45분 반환

    def _find_optimal_stress_level(self, df: pd.DataFrame) -> float:
        """최적 스트레스 수준 분석"""
        if 'avg_stress' in df.columns and 'avg_score' in df.columns:
            stress_score_ratio = df['avg_score'] / df['avg_stress']
            return float(df.loc[stress_score_ratio.idxmax()]['avg_stress'])
        return 3.0  # 기본값으로 3.0 반환

    def _generate_recommendations(self, patterns: Dict, efficiency: List[Dict]) -> List[str]:
        """맞춤형 학습 추천사항 생성"""
        recommendations = []
        
        if patterns.get('optimal_sessions'):
            recommendations.append(
                f"최적 학습 세션 길이는 {patterns['optimal_sessions']}분입니다. "
                "이 시간을 기준으로 학습 계획을 수립하세요."
            )
            
        if patterns.get('most_efficient'):
            recommendations.append(
                f"{patterns['most_efficient']} 과목에서 가장 높은 효율을 보이고 있습니다. "
                "이 과목의 학습 방식을 다른 과목에도 적용해 보세요."
            )
            
        stress_factors = patterns.get('stress_factors', {})
        if stress_factors.get('high_stress_subjects'):
            subjects = ', '.join(stress_factors['high_stress_subjects'])
            recommendations.append(
                f"{subjects} 과목에서 스트레스가 높게 나타납니다. "
                "이 과목들의 학습 방식을 재검토하고 필요한 경우 휴식을 취하세요."
            )

        return recommendations

    def get_performance_prediction(self, user_id: int, subject: str) -> Dict[str, Any]:
        """성과 예측 분석"""
        recent_stats = self.db.get_study_statistics(
            user_id,
            start_date=datetime.now() - timedelta(days=30)
        )
        
        if not recent_stats:
            return {
                'predicted_score': None,
                'confidence': 0,
                'factors': []
            }
            
        df = pd.DataFrame(recent_stats)
        subject_data = df[df['subject'] == subject]
        
        if subject_data.empty:
            return {
                'predicted_score': None,
                'confidence': 0,
                'factors': []
            }
            
        # 간단한 선형 예측 모델
        current_score = float(subject_data['avg_score'].iloc[0])
        study_intensity = float(subject_data['total_time'].iloc[0])
        stress_level = float(subject_data['avg_stress'].iloc[0])
        
        predicted_score = current_score * (1 + 0.1 * (study_intensity / df['total_time'].mean()))
        predicted_score *= (1 - 0.05 * (stress_level / df['avg_stress'].mean()))
        
        confidence = min(0.9, 0.5 + 0.1 * (study_intensity / df['total_time'].mean()))
        
        return {
            'predicted_score': round(predicted_score, 2),
            'confidence': round(confidence, 2),
            'factors': [
                {'name': '현재 성적', 'value': current_score},
                {'name': '학습 강도', 'value': study_intensity},
                {'name': '스트레스 수준', 'value': stress_level}
            ]
        }
