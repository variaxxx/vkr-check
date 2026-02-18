import time
from typing import Any, Dict, List


class VKRReport:
    """Генератор отчетов в формате JSON для ВКР"""

    @staticmethod
    def _calculate_summary(task_evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Интеркапсулированная логика формирования оценки.
        Вычисляет средний балл и процент соответствия на основе анализа пунктов задания.
        """
        total_scores = [e.get("score", 0) for e in task_evaluations]

        if not total_scores:
            return {
                "average_score": 0,
                "compliance_percentage": 0,
                "total_points_analyzed": 0,
            }

        avg_score = sum(total_scores) / len(total_scores)
        
        return {
            "average_score": round(avg_score, 2),
            "compliance_percentage": round(avg_score * 10, 1),
            "total_points_analyzed": len(total_scores),
        }

    @classmethod
    def generate_report(
        cls,
        info: dict, 
        task_evaluations: List[Dict[str, Any]],
        signs_verification: dict, 
        evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Генерирует финальную структуру отчета"""
        
        summary = cls._calculate_summary(task_evaluations)

        report_data = {
            "info": info,
            "summary": summary,
            "analysis": task_evaluations,
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "evaluations": evaluations,
            "signs_verification": signs_verification,
        }

        return report_data
