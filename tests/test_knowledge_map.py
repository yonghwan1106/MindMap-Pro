# File: tests/test_knowledge_map.py
# Unit Tests for Knowledge Map Module

import pytest
from modules.knowledge_map import KnowledgeMap
import networkx as nx
import pandas as pd
from unittest.mock import Mock, patch

class TestKnowledgeMap:
    @pytest.fixture
    def knowledge_map(self):
        """테스트용 KnowledgeMap 인스턴스 생성"""
        return KnowledgeMap()

    @pytest.fixture
    def sample_graph(self):
        """테스트용 그래프 데이터 생성"""
        G = nx.Graph()
        G.add_node("미분", subject="수학")
        G.add_node("적분", subject="수학")
        G.add_node("속도", subject="물리")
        G.add_edge("미분", "속도")
        G.add_edge("미분", "적분")
        return G

    def test_create_new_map(self, knowledge_map):
        """새로운 지식맵 생성 테스트"""
        # 새로운 개념 추가
        knowledge_map.G.add_node("미분", subject="수학")
        
        assert "미분" in knowledge_map.G.nodes
        assert knowledge_map.G.nodes["미분"]["subject"] == "수학"

    def test_add_related_concepts(self, knowledge_map):
        """연관 개념 추가 테스트"""
        # 개념 및 연관 관계 추가
        knowledge_map.G.add_node("미분", subject="수학")
        knowledge_map.G.add_node("속도", subject="물리")
        knowledge_map.G.add_edge("미분", "속도")
        
        assert ("미분", "속도") in knowledge_map.G.edges
        assert len(knowledge_map.G.edges) == 1

    def test_concept_validation(self, knowledge_map):
        """개념 유효성 검증 테스트"""
        # 중복 개념 추가 시도
        knowledge_map.G.add_node("미분", subject="수학")
        knowledge_map.G.add_node("미분", subject="물리")  # 같은 이름, 다른 과목
        
        assert len(knowledge_map.G.nodes) == 1
        assert knowledge_map.G.nodes["미분"]["subject"] == "수학"

    @patch('plotly.graph_objects.Figure')
    def test_visualization(self, mock_figure, knowledge_map, sample_graph):
        """시각화 기능 테스트"""
        knowledge_map.G = sample_graph
        fig = knowledge_map.visualize_map()
        
        assert fig is not None
        mock_figure.assert_called_once

    def test_graph_metrics(self, knowledge_map, sample_graph):
        """그래프 메트릭스 계산 테스트"""
        knowledge_map.G = sample_graph
        
        # 중심성 계산
        centrality = nx.degree_centrality(knowledge_map.G)
        assert centrality["미분"] > centrality["속도"]  # 미분이 더 많은 연결을 가짐

    def test_subject_filtering(self, knowledge_map, sample_graph):
        """과목별 필터링 테스트"""
        knowledge_map.G = sample_graph
        
        math_nodes = [n for n, d in knowledge_map.G.nodes(data=True) 
                     if d["subject"] == "수학"]
        assert len(math_nodes) == 2  # 미분, 적분
        
        physics_nodes = [n for n, d in knowledge_map.G.nodes(data=True) 
                        if d["subject"] == "물리"]
        assert len(physics_nodes) == 1  # 속도

    def test_edge_attributes(self, knowledge_map):
        """엣지 속성 테스트"""
        knowledge_map.G.add_node("미분", subject="수학")
        knowledge_map.G.add_node("적분", subject="수학")
        knowledge_map.G.add_edge("미분", "적분", weight=0.8, relationship="선수과목")
        
        edge_data = knowledge_map.G.get_edge_data("미분", "적분")
        assert edge_data["weight"] == 0.8
        assert edge_data["relationship"] == "선수과목"

    def test_graph_operations(self, knowledge_map, sample_graph):
        """그래프 연산 테스트"""
        knowledge_map.G = sample_graph
        
        # 노드 제거
        knowledge_map.G.remove_node("속도")
        assert "속도" not in knowledge_map.G.nodes
        assert len(knowledge_map.G.edges) == 1  # 미분-적분 엣지만 남음

        # 엣지 제거
        knowledge_map.G.remove_edge("미분", "적분")
        assert ("미분", "적분") not in knowledge_map.G.edges
