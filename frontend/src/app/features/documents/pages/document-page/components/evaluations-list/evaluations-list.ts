import { ChangeDetectionStrategy, Component, input } from "@angular/core";
import { Icon } from "@shared/components/icon/icon";

import { EvaluationItem, EvaluationSection } from "../../../../dto";

@Component({
  selector: "app-evaluations-list",
  imports: [Icon],
  templateUrl: "./evaluations-list.html",
  styleUrl: "./evaluations-list.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EvaluationsList {
  public evaluations = input.required<EvaluationItem[]>();

  protected readonly evaluationColumns: string[] = ["Раздел", "Оценка", "Пояснение"];
  protected readonly evaluationSectionsMap: Record<EvaluationSection, string> = {
    application: "Приложение",
    introduction: "Введение",
    literature: "Список литературы",
    conclusion: "Вывод",
    annotation: "Аннотация",
  };
}
