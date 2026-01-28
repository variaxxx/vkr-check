import json
import time
from typing import Dict, List, Any

class VKRReport:
    """Генератор отчетов в формате JSON"""
    
    @staticmethod
    def generate_report(info: dict, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Генерирует структуру отчета"""
        total_scores = [e["score"] for e in evaluations]
        
        if total_scores:
            avg_score = sum(total_scores) / len(total_scores)
            summary = {
                "average_score": round(avg_score, 2),
                "compliance_percentage": round(avg_score * 10, 1),
                "total_points_analyzed": len(total_scores)
            }
        else:
            summary = {}
        
        report_data = {
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "info": info,
            "analysis": evaluations,
            "summary": summary
        }
        
        return json.dumps(report_data)
    
    # @staticmethod
    # def save_report(report_data: Dict[str, Any], filepath: str = None):
    #     """Сохраняет отчет в JSON файл"""
    #     if filepath is None:
    #         filepath = config.Config.JSON_REPORT_PATH
            
    #     with open(filepath, 'w', encoding='utf-8') as f:
    #         json.dump(report_data, f, ensure_ascii=False, indent=4)