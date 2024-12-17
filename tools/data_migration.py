# File: tools/data_migration.py
# Data Migration Tool for MindMap Pro

import json
import csv
from typing import Dict, List, Any
from datetime import datetime
import logging
from pathlib import Path
from storage.database import DatabaseManager

class DataMigrationTool:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def export_user_data(self, user_id: int, output_dir: str = None) -> Dict[str, Any]:
        """사용자 데이터 내보내기"""
        try:
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(exist_ok=True)
            else:
                output_path = self.backup_dir
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_path / f"user_{user_id}_data_{timestamp}.json"
            
            # 사용자 데이터 수집
            data = {
                "user_info": self.db.get_user_by_id(user_id),
                "knowledge_maps": self._export_knowledge_maps(user_id),
                "study_records": self._export_study_records(user_id),
                "mistake_records": self._export_mistake_records(user_id),
                "export_timestamp": timestamp
            }
            
            # JSON 파일로 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Successfully exported data for user {user_id} to {filename}")
            return {"success": True, "filename": str(filename)}
            
        except Exception as e:
            self.logger.error(f"Error exporting user data: {str(e)}")
            return {"success": False, "error": str(e)}
            
    def import_user_data(self, filepath: str) -> Dict[str, Any]:
        """사용자 데이터 가져오기"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            user_id = data["user_info"]["user_id"]
            
            # 기존 데이터 백업
            self.export_user_data(user_id)
            
            # 데이터 가져오기
            self._import_knowledge_maps(user_id, data["knowledge_maps"])
            self._import_study_records(user_id, data["study_records"])
            self._import_mistake_records(user_id, data["mistake_records"])
            
            self.logger.info(f"Successfully imported data for user {user_id}")
            return {"success": True, "user_id": user_id}
            
        except Exception as e:
            self.logger.error(f"Error importing user data: {str(e)}")
            return {"success": False, "error": str(e)}
            
    def _export_knowledge_maps(self, user_id: int) -> List[Dict]:
        """지식맵 데이터 내보내기"""
        maps = self.db.get_user_knowledge_maps(user_id)
        for map_data in maps:
            map_id = map_data["map_id"]
            map_data["nodes"] = self.db.get_map_nodes(map_id)
            map_data["edges"] = self.db.get_map_edges(map_id)
        return maps
        
    def _export_study_records(self, user_id: int) -> List[Dict]:
        """학습 기록 내보내기"""
        return self.db.get_study_records(user_id)
        
    def _export_mistake_records(self, user_id: int) -> List[Dict]:
        """실수 기록 내보내기"""
        return self.db.get_mistake_records(user_id)
        
    def _import_knowledge_maps(self, user_id: int, maps: List[Dict]):
        """지식맵 데이터 가져오기"""
        for map_data in maps:
            map_id = self.db.add_knowledge_map(
                user_id,
                map_data["subject"]
            )
            
            # 노드 추가
            node_id_mapping = {}
            for node in map_data["nodes"]:
                new_node_id = self.db.add_concept_node(
                    map_id,
                    node["concept"],
                    node["subject"],
                    node["level"]
                )
                node_id_mapping[node["node_id"]] = new_node_id
                
            # 엣지 추가
            for edge in map_data["edges"]:
                self.db.add_concept_edge(
                    map_id,
                    node_id_mapping[edge["source_node_id"]],
                    node_id_mapping[edge["target_node_id"]],
                    edge["relationship_type"],
                    edge["strength"]
                )
                
    def _import_study_records(self, user_id: int, records: List[Dict]):
        """학습 기록 가져오기"""
        for record in records:
            self.db.add_study_record(
                user_id,
                record["subject"],
                record["study_time"],
                record["score"],
                record["stress_level"]
            )
            
    def _import_mistake_records(self, user_id: int, records: List[Dict]):
        """실수 기록 가져오기"""
        for record in records:
            self.db.add_mistake_record(
                user_id,
                record["subject"],
                record["mistake_type"],
                record["problem_difficulty"],
                record["time_spent"],
                record["is_repeated"],
                record["stress_level"]
            )
            
    def export_to_csv(self, user_id: int, data_type: str, output_dir: str = None) -> Dict[str, Any]:
        """데이터를 CSV 형식으로 내보내기"""
        try:
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(exist_ok=True)
            else:
                output_path = self.backup_dir
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_path / f"user_{user_id}_{data_type}_{timestamp}.csv"
            
            if data_type == "study_records":
                data = self._export_study_records(user_id)
            elif data_type == "mistake_records":
                data = self._export_mistake_records(user_id)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
                
            if data:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                    
                return {"success": True, "filename": str(filename)}
            return {"success": False, "error": "No data found"}
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {str(e)}")
            return {"success": False, "error": str(e)}
