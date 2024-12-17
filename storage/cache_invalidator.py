# File: storage/cache_invalidator.py
# Cache Invalidation System for MindMap Pro

from typing import List, Set, Dict, Any
import logging
from datetime import datetime
from storage.cache_manager import CacheManager

class CacheInvalidator:
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.logger = logging.getLogger(__name__)
        self.dependency_graph: Dict[str, Set[str]] = {}
        
    def register_dependency(self, key: str, dependent_keys: List[str]):
        """캐시 키 간의 종속성 등록"""
        if key not in self.dependency_graph:
            self.dependency_graph[key] = set()
        self.dependency_graph[key].update(dependent_keys)
        
    def invalidate_with_dependencies(self, key: str) -> bool:
        """주어진 키와 종속된 모든 캐시 삭제"""
        try:
            keys_to_invalidate = self._get_dependent_keys(key)
            keys_to_invalidate.add(key)
            
            for k in keys_to_invalidate:
                self.cache.redis_client.delete(k)
                self.logger.info(f"Invalidated cache key: {k}")
                
            return True
        except Exception as e:
            self.logger.error(f"Error during cache invalidation: {str(e)}")
            return False
            
    def _get_dependent_keys(self, key: str, visited: Set[str] = None) -> Set[str]:
        """종속된 모든 캐시 키 조회"""
        if visited is None:
            visited = set()
            
        dependent_keys = set()
        if key in self.dependency_graph:
            for dependent_key in self.dependency_graph[key]:
                if dependent_key not in visited:
                    visited.add(dependent_key)
                    dependent_keys.add(dependent_key)
                    dependent_keys.update(self._get_dependent_keys(dependent_key, visited))
                    
        return dependent_keys
        
    def invalidate_pattern(self, pattern: str) -> bool:
        """패턴과 일치하는 모든 캐시 삭제"""
        try:
            keys = self.cache.redis_client.keys(pattern)
            if keys:
                self.cache.redis_client.delete(*keys)
                self.logger.info(f"Invalidated {len(keys)} keys matching pattern: {pattern}")
            return True
        except Exception as e:
            self.logger.error(f"Error during pattern invalidation: {str(e)}")
            return False
            
    def invalidate_user_data(self, user_id: int) -> bool:
        """사용자 관련 모든 캐시 삭제"""
        pattern = f"mindmap_pro:*:{user_id}*"
        return self.invalidate_pattern(pattern)
        
    def invalidate_knowledge_map(self, map_id: int) -> bool:
        """지식맵 관련 캐시 삭제"""
        key = f"mindmap_pro:knowledge_map:{map_id}"
        return self.invalidate_with_dependencies(key)
        
    def invalidate_analysis_cache(self, user_id: int, analysis_type: str = None) -> bool:
        """분석 결과 캐시 삭제"""
        if analysis_type:
            pattern = f"mindmap_pro:analysis:{analysis_type}:{user_id}"
        else:
            pattern = f"mindmap_pro:analysis:*:{user_id}"
        return self.invalidate_pattern(pattern)
