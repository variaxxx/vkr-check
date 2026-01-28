from llm_service import LLMService
from rag import RAGEngine
from pdf_processor import PDFProcessor
from task_parser import TaskParser
from info_parser import InfoParser
from vkr_analyzer import VKRAnalyzer
from vkr_report import VKRReport


class Pipeline:
    def __init__(self):    
        self.llm_service = LLMService()
        self.rag_engine = RAGEngine()
        self.pdf_processor = PDFProcessor()
        
        self.task_parser = TaskParser(self.llm_service, self.pdf_processor)
        self.info_parser = InfoParser(self.llm_service, self.pdf_processor)
        self.vkr_analyzer = VKRAnalyzer(self.llm_service, self.rag_engine)
        
    def pipeline(self, pdf_path: str):
        task_points = self.task_parser.get_task_points(pdf_path)
        info = self.info_parser.get_info(pdf_path)

        full_text = self.pdf_processor.extract_text_from_pdf(pdf_path)
        vector_db = self.rag_engine.create_vector_db(full_text)
        
        evaluations = []
        
        for point in task_points:
            print(point)
            score, reason = self.vkr_analyzer.evaluate_point(point, vector_db)
            
            evaluations.append({
                "task_point": point,
                "score": score,
                "justification": reason
            })
        
        report_data = VKRReport.generate_report(info, evaluations)
        
        return report_data

if __name__ == "__main__":
    pipe = Pipeline()
    res = pipe.pipeline(r"D:\projects\task_check\new_pdfs\doc10.pdf")
    print(res)