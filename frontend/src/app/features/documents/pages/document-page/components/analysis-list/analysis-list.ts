import { ChangeDetectionStrategy, Component, input } from "@angular/core";

import { AnalysisPoint } from "../../../../dto";

@Component({
  selector: "app-analysis-list",
  imports: [],
  templateUrl: "./analysis-list.html",
  styleUrl: "./analysis-list.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AnalysisList {
  public analysisPoints = input.required<AnalysisPoint[]>();

  protected readonly analysisColumns: string[] = ["Пункт задания", "Оценка", "Пояснение"];
}
