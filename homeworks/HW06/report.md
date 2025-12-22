# HW06 – Report

> Файл: `homeworks/HW06/report.md`  
> Важно: не меняйте названия разделов (заголовков). Заполняйте текстом и/или вставляйте результаты.

## 1. Dataset

- Какой датасет выбран: `S06-hw-dataset-02.csv`
- Размер: (18000, 39)
- Целевая переменная: `target` (класс 0 - доля 0.737389, класс 1 - доля 0.262611)
- Признаки: числовые (int64 и float64)

## 2. Protocol

- Разбиение: train/test (test_size=0.2, random_state=42)
- Подбор: CV на train (5 фолдов, оптимизировалось ROC-AUC)
- Метрики: accuracy, F1, ROC-AUC - именно эти метрики, так как задача является бинарной классификацией. Accuracy дает общее представление, F1 учитывает баланс между precision и recall, а ROC-AUC оценивает качество ранжирования вероятностей независимо от порога

## 3. Models

- DummyClassifier (baseline, стратегия most_frequent) - без подбора гиперпараметров
- LogisticRegression - использована в Pipeline со StandardScaler, logreg__C ([0.01, 0.1, 1.0, 10.0, 100.0, 1000.0])
- DecisionTreeClassifier - max_depth ([3, 5, 7, 10, None]) и min_samples_leaf ([1, 2, 5, 10])
- RandomForestClassifier - n_estimators ([100, 200]), max_depth ([5, 10, None]), min_samples_leaf ([1, 2, 5]), max_features (['sqrt', 'log2'])
- GradientBoostingClassifier - n_estimators ([100, 200]), learning_rate ([0.05, 0.1, 0.2]), max_depth ([3, 5]), subsample ([0.8, 1.0])
- StackingClassifier - базовые модели: DecisionTree и RandomForest (лучшие из подобранных), метамодель: LogisticRegression, cv=5 (соблюдена CV-логика)

## 4. Results

- DummyClassifier: Accuracy = 0.7375, F1 = 0.0000, ROC-AUC = 0.5000
- LogisticRegression: Accuracy = 0.8119, F1 = 0.5607, ROC-AUC = 0.7977
- DecisionTreeClassifier: Accuracy = 0.8383, F1 = 0.6576, ROC-AUC = 0.8371
- RandomForestClassifier: Accuracy = 0.8908, F1 = 0.7579, ROC-AUC = 0.9281
- GradientBoostingClassifier: Accuracy = 0.9039, F1 = 0.8009, ROC-AUC = 0.9253
- StackingClassifier: Accuracy = 0.9047, F1 = 0.8070, ROC-AUC = 0.9281

Победитель - StackingClassifier, так как показал наивысший F1-скор (0.8070) при максимальном ROC-AUC (0.9281, совместно с RandomForest). StackingClassifier оказался лучшим, потому что он объединил предсказания DecisionTree и RandomForest с помощью логистической регрессии, что позволило использовать их сильные стороны


## 5. Analysis

- Устойчивость: при 5 прогонах с разными random_state (1,2,3,4,5) метрики DecisionTree и RandomForest показали низкое стандартное отклонение (+-0.01), что указывает на хорошую устойчивость моделей к случайным разбиениям данных. RandomForest оказался стабильнее по ROC-AUC (+-0.005 против +-0.011), а по F1 отклонения примерно одинаковые
- Ошибки: confusion matrix для StackingClassifier показывает низкое число ошибок false positive и false negative (115 и 228) при достаточно большом количестве верно предсказанных ответов (2540 и 717), что согласуется с высоким F1
- Интерпретация: permutation importance выявила, что сильнее всего модель зависит от признака f16 (влияние около 0.045), далее от f01, f19, f12 (влияние 0.015–0.018)

## 6. Conclusion

Ансамбли (RandomForest, GradientBoosting, Stacking) значительно превосходят одиночные модели и линейные подходы по всем метрикам. Stacking с CV-логикой позволяет безопасно комбинировать модели и добиваться лучших результатов