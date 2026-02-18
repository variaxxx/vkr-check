import json
import time
from typing import Any, Dict, List


class VKRReport:
    """Генератор отчетов в формате JSON"""

    @staticmethod
    def generate_report(
        info: dict, evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Генерирует структуру отчета"""
        total_scores = [e["score"] for e in evaluations]

        if total_scores:
            avg_score = sum(total_scores) / len(total_scores)
            summary = {
                "average_score": round(avg_score, 2),
                "compliance_percentage": round(avg_score * 10, 1),
                "total_points_analyzed": len(total_scores),
            }
        else:
            summary = {}

        report_data = {
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "info": info,
            "analysis": evaluations,
            "summary": summary,
        }

        return report_data
