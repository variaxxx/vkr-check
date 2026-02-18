from typing import List, Dict

def run_evaluation(section_key, check_dict, eval_func, **kwargs):
    """
    Универсальная обертка для оценки секций документа.
    """
    if check_dict.get(section_key):
        score, report, tech_details = eval_func(**kwargs)
        return {
            "section": section_key,
            "score": score,
            "details": report,
            "tech_details": tech_details,
            "found": 1
        }
    
    return {
        "section": section_key,
        "score": 0,
        "details": "Section not found",
        "tech_details": {},
        "found": 0
    }
    

def check_structure(final_structure: List[Dict]) -> Dict:
    categories = {
        'annotation_ru': 0,
        'annotation_en': 0, 
        'intro': 0,
        'main': 0,
        'conclusion': 0,
        'biblio': 0,
        'application': 0
    }
    
    for cat in categories:
        for header in final_structure:
            if header["category"] == cat:
                categories[cat] = 1
                break
            
    evaluations = {
        "application": categories["application"],
        "literature": categories["biblio"],
        "introduction": categories["intro"],
        "conclusion": categories["conclusion"]
    }
            
    return evaluations