import pandas as pd
import networkx as nx
from typing import Dict, List, Any

class DataProcessor:
    def __init__(self):
        self.data_cache = {}

    def process_knowledge_map_data(self, nodes: List[Dict], edges: List[Dict]) -> nx.Graph:
        """
        지식맵 데이터를 처리하여 NetworkX 그래프로 변환
        
        Args:
            nodes: 노드 정보 리스트
            edges: 엣지 정보 리스트
            
        Returns:
            nx.Graph: 처리된 지식맵 그래프
        """
        G = nx.Graph()
        
        # 노드 추가
        for node in nodes:
            G.add_node(
                node['id'],
                subject=node.get('subject', ''),
                concept=node.get('concept', ''),
                level=node.get('level', 1)
            )
            
        # 엣지 추가
        for edge in edges:
            G.add_edge(
                edge['source'],
                edge['target'],
                weight=edge.get('weight', 1),
                relationship=edge.get('relationship', '')
            )
            
        return G

    def analyze_learning_patterns(self, study_data: pd.DataFrame) -> Dict[str, Any]:
        """
        학습 패턴 분석
        
        Args:
            study_data: 학습 데이터 DataFrame
            
        Returns:
            Dict: 분석 결과
        """
        if study_data.empty:
            return {}
            
        analysis = {
            'total_study_time': study_data['duration'].sum(),
            'subject_distribution': study_data.groupby('subject')['duration'].sum().to_dict(),
            'peak_performance_time': self._find_peak_performance_time(study_data),
            'weak_points': self._identify_weak_points(study_data)
        }
        
        return analysis

    def _find_peak_performance_time(self, data: pd.DataFrame) -> Dict[str, str]:
        """
        최적의 학습 시간대 분석
        """
        if 'score' not in data.columns or 'time' not in data.columns:
            return {}
            
        performance_by_time = data.groupby('time')['score'].mean()
        peak_time = performance_by_time.idxmax()
        
        return {
            'peak_time': peak_time,
            'average_score': performance_by_time[peak_time]
        }

    def _identify_weak_points(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        취약점 분석
        """
        if 'score' not in data.columns or 'concept' not in data.columns:
            return []
            
        weak_points = data[data['score'] < data['score'].mean()]
        
        return [
            {
                'concept': concept,
                'average_score': scores['score'].mean(),
                'frequency': len(scores)
            }
            for concept, scores in weak_points.groupby('concept')
        ]

    def cache_data(self, key: str, data: Any) -> None:
        """
        데이터 캐싱
        """
        self.data_cache[key] = data

    def get_cached_data(self, key: str) -> Any:
        """
        캐시된 데이터 조회
        """
        return self.data_cache.get(key)
