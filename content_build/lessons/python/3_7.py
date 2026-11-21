"""Урок 3.7 курса Python: Data Science и ML."""

from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip("\n")


def text(content: str) -> dict:
    return {"type": "text", "content": content.strip()}


def heading(content: str, level: int = 2) -> dict:
    return {"type": "heading", "level": level, "content": content.strip()}


def bullets(*items: str, ordered: bool = False) -> dict:
    return {"type": "list", "ordered": ordered, "items": list(items)}


def numbered(*items: str) -> dict:
    return bullets(*items, ordered=True)


def table(headers: list[str], rows: list[list[str]]) -> dict:
    return {"type": "table", "headers": headers, "rows": rows}


def callout(style: str, title: str, content: str) -> dict:
    return {"type": "callout", "style": style, "title": title, "content": content}


def example(language: str, source: str) -> dict:
    return {"type": "code", "language": language, "content": code(source)}


LESSON = {
    "language": "python",
    "program_order": 3,
    "topic_order": 7,
    "name": "3.7. Data Science и машинное обучение",
    "slug": "python-3-7-data-science-и-машинное-обучение",
    "short_description": (
        "NumPy, Pandas, визуализация (Matplotlib, Seaborn, Plotly), "
        "scikit-learn (pipeline, CV, метрики), основы PyTorch, MLflow, деплой моделей."
    ),
    "topic_name": "Data Science и машинное обучение",
    "topic_description": (
        "Полный цикл Data Science в Python: от загрузки и очистки данных (NumPy, Pandas) "
        "через визуализацию и feature engineering до построения ML моделей (sklearn, PyTorch), "
        "трекинга экспериментов (MLflow) и деплоя."
    ),
    "learning_objectives": [
        "Работать с NumPy массивами: векторизация, броадкастинг, линейная алгебра, статистика",
        "Анализировать данные с Pandas: DataFrame, GroupBy, Time Series, объединение, пропуски",
        "Визуализировать данные: Matplotlib (базовый), Seaborn (статистика), Plotly (интерактивно)",
        "Строить ML пайплайны в scikit-learn: preprocessing, Pipeline, CV, метрики, hyperparameter tuning",
        "Понимать основы PyTorch: тензоры, автоград, nn.Module, DataLoader, Transfer Learning",
        "Вести трекинг экспериментов через MLflow: параметры, метрики, артефакты, модели",
        "Избегать типичных ошибок: data leakage, неправильное масштабирование, небаланс классов",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "python",
        "data science",
        "machine learning",
        "numpy",
        "pandas",
        "scikit-learn",
        "pytorch",
        "mlflow",
        "visualization",
    ],
    "starter_code": code(
        """
        import numpy as np
        import pandas as pd

        # NumPy векторизация
        arr = np.array([1, 2, 3, 4, 5])
        print(arr * 2)  # [2, 4, 6, 8, 10]

        # Pandas DataFrame
        df = pd.DataFrame({
            'name': ['Анна', 'Борис'],
            'age': [25, 30],
            'salary': [80000, 120000]
        })
        print(df.groupby('name')['salary'].mean())
        """
    ),
    "hints": [
        "Всегда делите данные на train/test ДО feature engineering (data leakage).",
        "Pipeline в sklearn гарантирует, что scaler.fit вызывается только на train.",
        "Для несбалансированных классов используйте stratified CV и ROC-AUC/F1.",
        "PyTorch: requires_grad=True включает автоград, .backward() считает градиенты.",
    ],
    "content": [
        text(
            "Data Science — это не просто «обучение моделей». Это цикл: вопрос → данные → "
            "EDA → feature engineering → baseline → итерации → деплой → мониторинг. "
            "Python — lingua franca этой области: NumPy/Pandas для данных, sklearn для "
            "классического ML, PyTorch для Deep Learning, MLflow для экспериментов. "
            "В этом уроке пройдём полный стек: от NumPy массивов до деплоя нейросети.\n\n"
            "Важно понимать: 80% времени Data Scientist тратит на данные (загрузка, очистка, "
            "EDA, feature engineering), и только 20% — на модели. Качественные данные и "
            "правильная валидация важнее сложной архитектуры модели. Грязные данные с "
            "утечкой из теста в обучение дадут красивые метрики, но бесполезную в проде модель."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "работать с NumPy: создание массивов, векторизация, броадкастинг, линейная алгебра, статистика;",
            "анализировать данные в Pandas: чтение/запись, индексация, GroupBy, pivot, Time Series, пропуски;",
            "визуализировать: Matplotlib (база), Seaborn (статистика), Plotly (интерактивно);",
            "строить ML пайплайны в sklearn: ColumnTransformer, Pipeline, CV, метрики, Grid/Random Search;",
            "понимать PyTorch: тензоры, автоград, nn.Module, DataLoader, Transfer Learning;",
            "вести эксперименты в MLflow: параметры, метрики, модели, UI для сравнения;",
            "избегать типичных ошибок: data leakage, неправильное масштабирование, небаланс классов.",
        ),
        heading("NumPy — фундамент вычислений"),
        heading("Массивы vs списки", 3),
        example(
            "python",
            """
            import numpy as np

            # Векторизация — операции над всем массивом без циклов
            arr = np.array([1, 2, 3, 4, 5])
            arr * 2           # [2, 4, 6, 8, 10]
            arr ** 2          # [1, 4, 9, 16, 25]
            arr > 3           # [False, False, False, True, True]

            # Ускорение в 10-100x по сравнению с Python циклами
            """,
        ),
        text(
            "NumPy массив — непрерывный блок памяти с единым типом данных. "
            "Операции векторизованы: выполняются на C-уровне над всей памятью сразу, "
            "без Python-циклов. Это даёт ускорение в 10-100x.\n\n"
            "Типы данных (dtype) важны: `int8`/`int16`/`int32`/`int64`, `float32`/`float64`, "
            "`bool`, `datetime64`. Правильный выбор dtype экономит память: "
            "`float32` вместо `float64` — в 2 раза меньше RAM. Для больших датасетов "
            "используйте `float32` (достаточно точности для ML) и `int32` для индексов."
        ),
        heading("Создание массивов", 3),
        text(
            "Функции создания массивов делятся на категории:\n"
            "- Из существующих данных: `np.array()`, `np.asarray()` (нет копии если уже массив).\n"
            "- Заполненные значениями: `zeros`, `ones`, `full`, `eye` (единичная матрица).\n"
            "- Последовательности: `arange` (как range), `linspace` (равномерные точки), `logspace` (лог. шкала).\n"
            "- Случайные: `random.normal` (Гаусс), `random.uniform`, `random.randint`, `random.choice`.\n"
            "- Из файлов: `np.load` (`.npy`), `np.loadtxt`/`genfromtxt` (текст), `memmap` (большие файлы).\n\n"
            "`memmap` позволяет работать с массивами больше RAM — данные лежат на диске, "
            "NumPy подгружает нужные куски. Критично для датасетов 100GB+."
        ),
        example(
            "python",
            """
            np.zeros((3, 4))           # нули
            np.ones((2, 3))            # единицы
            np.eye(3)                  # единичная матрица
            np.arange(0, 10, 2)        # [0, 2, 4, 6, 8]
            np.linspace(0, 1, 5)       # 5 точек от 0 до 1
            np.random.normal(0, 1, (100, 3))  # нормальное распределение
            np.random.randint(0, 10, (5, 5))  # целые числа
            """,
        ),
        heading("Индексация и броадкастинг", 3),
        example(
            "python",
            """
            mat = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

            mat[0, 1]        # 2 (строка 0, столбец 1)
            mat[1:, :2]      # [[4, 5], [7, 8]] (срезы)
            mat[mat > 5]     # [6, 7, 8, 9] (булева маска)

            # Броадкастинг — автоматическое расширение размерностей
            a = np.array([[1], [2], [3]])  # (3, 1)
            b = np.array([10, 20, 30])     # (3,)
            a + b  # [[11, 21, 31], [12, 22, 32], [13, 23, 33]]
            """,
        ),
        text(
            "Броадкастинг (broadcasting) — автоматическое выравнивание размерностей "
            "по правилам: размерности совместимы, если равны или одна из них равна 1. "
            "Это позволяет писать векторизованные операции без явных циклов и `tile/repeat`.\n\n"
            "Правила броадкастинга:\n"
            "1. Выравниваем справа: (3,1) + (3,) → (3,1) + (1,3) → (3,3).\n"
            "2. Измерение 1 растягивается: (3,1) становится (3,3) копированием строки.\n"
            "3. Если размерности не 1 и не равны — ValueError.\n\n"
            "Пример: центрирование матрицы `X - X.mean(axis=0)` — mean имеет форму (n_features,), "
            "броадкастится к (n_samples, n_features). Это работает быстро и без копий."
        ),
        example(
            "python",
            """
            A = np.array([[1, 2], [3, 4]])
            B = np.array([[5, 6], [7, 8]])

            A @ B                    # матричное умножение
            np.dot(A, B)             # то же
            np.linalg.inv(A)         # обратная матрица
            np.linalg.det(A)         # определитель
            np.linalg.eig(A)         # собственные значения/векторы
            np.linalg.svd(A)         # SVD разложение
            """,
        ),
        heading("Статистика", 3),
        example(
            "python",
            """
            data = np.random.normal(100, 15, 1000)
            data.mean(), data.std(), data.var()
            np.median(data)
            np.percentile(data, [25, 50, 75])  # квартили
            np.corrcoef(x, y)         # корреляция
            """,
        ),
        heading("Pandas — табличные данные"),
        text(
            "Pandas строится на NumPy, добавляет метки (индексы), колонки разного типа, "
            "навигацию по времени, SQL-подобные операции. DataFrame — словарь Series с общим индексом. "
            "Series — массив с индексом. Операции векторизованы через NumPy под капотом.\n\n"
            "Важные концепции:\n"
            "- Индекс — метки строк (можно MultiIndex для иерархических данных).\n"
            "- Колонки — Series с общим индексом, разные dtypes.\n"
            "- Операции: арифметика, сравнение, группировка, оконные функции, ресемплинг.\n"
            "- NaN — missing value (float), работает с `isna()`, `fillna()`, `dropna()`."
        ),
        heading("DataFrame и Series", 3),
        example(
            "python",
            """
            import pandas as pd

            df = pd.DataFrame({
                'name': ['Анна', 'Борис', 'Виктор'],
                'age': [25, 30, 35],
                'city': ['Москва', 'СПб', 'Москва'],
                'salary': [80000, 120000, 95000]
            })

            # Чтение данных
            pd.read_csv('data.csv')
            pd.read_parquet('data.parquet')
            pd.read_json('data.json')
            pd.read_sql('SELECT * FROM users', conn)
            pd.read_excel('data.xlsx')
            """,
        ),
        text(
            "DataFrame — таблица с колонками разного типа. Series — одна колонка. "
            "Pandas поддерживает множество форматов: CSV, Parquet (колончатый, быстрый, сжатый), "
            "JSON, SQL, Excel. Parquet — рекомендуемый формат для больших данных."
        ),
        heading("Индексация", 3),
        example(
            "python",
            """
            df['age']              # Series
            df[['name', 'age']]    # DataFrame
            df.loc[0]              # строка по индексу
            df.iloc[0]             # строка по позиции
            df[df['age'] > 28]     # фильтрация
            df.query('age > 28 and city == "Москва"')
            """,
        ),
        text(
            "`loc` — по метке индекса, `iloc` — по целочисленной позиции. "
            "`query()` — строка-выражение, удобна для сложных фильтров."
        ),
        heading("GroupBy и агрегация", 3),
        example(
            "python",
            """
            # Группировка
            df.groupby('city')['salary'].mean()
            df.groupby('city').agg({'salary': ['mean', 'median', 'std'], 'age': 'max'})

            # Pivot table
            df.pivot_table(values='salary', index='city', columns='age', aggfunc='mean')

            # Crosstab
            pd.crosstab(df['city'], df['age'] > 30)
            """,
        ),
        text(
            "`groupby().agg()` — несколько агрегаций за раз. "
            "`pivot_table` — сводная таблица (Excel-style). "
            "`crosstab` — таблица сопряжённости.\n\n"
            "Продвинутые GroupBy:\n"
            "- `groupby().transform()` — возвращает тот же размер, что исходный (для фичей: z-score, rank).\n"
            "- `groupby().filter()` — отбирает группы по условию (размер группы > N).\n"
            "- `groupby().apply()` — произвольная функция к каждой группе (медленнее, но гибче).\n"
            "- `groupby().rolling()` — скользящие окна внутри групп (time series features).\n"
            "- `as_index=False` — результат как DataFrame, не Series с MultiIndex."
        ),
        heading("Работа с пропусками", 3),
        example(
            "python",
            """
            df.isna().sum()           # количество NaN по колонкам
            df.dropna()               # удалить строки с NaN
            df.fillna({'age': df['age'].mean(), 'city': 'Unknown'})
            df.interpolate()          # интерполяция для временных рядов
            """,
        ),
        heading("Time Series", 3),
        text(
            "Pandas Time Series — мощный инструмент для временных рядов:\n"
            "- `DatetimeIndex` — индекс с метками времени, поддерживает таймзоны.\n"
            "- `resample('W')` — ресемплинг (ап/даунсэмплинг) с агрегацией.\n"
            "- `rolling(window).mean/std/sum` — скользящие окна для сглаживания/признаков.\n"
            "- `shift(n)` — лаги (feature engineering для forecasting).\n"
            "- `diff()` — разности (стационарность для ARIMA).\n"
            "- `ewm(span).mean()` — экспоненциальное сглаживание.\n"
            "- `to_period('M')` / `to_timestamp()` — конвертация период/точка.\n\n"
            "Важно: всегда сортируйте индекс (`ts.sort_index()`) перед операциями."
        ),
        heading("Time Series", 3),
        example(
            "python",
            """
            dates = pd.date_range('2024-01-01', periods=100, freq='D')
            ts = pd.Series(np.random.randn(100).cumsum(), index=dates)

            ts.resample('W').mean()   # ресемплинг по неделям
            ts.rolling(7).mean()      # скользящее среднее
            ts.shift(1)               # лаг
            ts.diff()                 # разность
            """,
        ),
        heading("Объединение данных", 3),
        example(
            "python",
            """
            pd.merge(df1, df2, on='id', how='inner')   # join
            pd.concat([df1, df2], axis=0)              # вертикальное объединение
            df1.join(df2.set_index('id'), on='id')     # join по индексу
            """,
        ),
        heading("Визуализация"),
        heading("Matplotlib (базовый)", 3),
        example(
            "python",
            """
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(2, 2, figsize=(10, 8))
            ax[0, 0].plot(x, y)
            ax[0, 1].scatter(x, y)
            ax[1, 0].hist(data, bins=30)
            ax[1, 1].boxplot([group1, group2])
            plt.tight_layout()
            plt.savefig('plot.png', dpi=300)
            """,
        ),
        heading("Seaborn (статистические графики)", 3),
        example(
            "python",
            """
            import seaborn as sns

            sns.set_style("whitegrid")
            sns.histplot(data=df, x='salary', hue='city', kde=True)
            sns.boxplot(data=df, x='city', y='salary')
            sns.violinplot(data=df, x='city', y='salary')
            sns.scatterplot(data=df, x='age', y='salary', hue='city')
            sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
            sns.pairplot(df, hue='city')
            """,
        ),
        text(
            "Seaborn строится на Matplotlib, даёт красивые статистические графики одной строкой: "
            "`histplot` (гистограмма + KDE), `boxplot`/`violinplot` (распределения по группам), "
            "`heatmap` (корреляции), `pairplot` (парные зависимости)."
        ),
        heading("Plotly (интерактивные)", 3),
        example(
            "python",
            """
            import plotly.express as px

            fig = px.scatter(df, x='age', y='salary', color='city',
                             hover_data=['name'], title='Salary vs Age')
            fig.show()  # открывается в браузере
            fig.write_html('plot.html')
            """,
        ),
        text(
            "Plotly — интерактивные графики (zoom, hover, pan). `fig.show()` открывает в браузере, "
            "`write_html` сохраняет standalone HTML для встраивания в отчёты/дашборды.\n\n"
            "Plotly Express (`px`) — высокоуровневый интерфейс: `px.scatter`, `px.line`, `px.bar`, "
            "`px.histogram`, `px.box`, `px.violin`, `px.heatmap`, `px.choropleth` (карты). "
            "Graph Objects (`go`) — низкоуровневый контроль каждого элемента. "
            "`fig.update_layout()` — тема, заголовки, легенда. "
            "`fig.write_json()` / `fig.read_json()` — сериализация графиков."
        ),
        heading("Scikit-learn — классический ML"),
        heading("Pipeline", 3),
        example(
            "python",
            """
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import StandardScaler, OneHotEncoder
            from sklearn.compose import ColumnTransformer
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split, cross_val_score

            # Preprocessing
            numeric_features = ['age', 'salary']
            categorical_features = ['city']

            preprocessor = ColumnTransformer([
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ])

            # Pipeline
            pipe = Pipeline([
                ('preprocessor', preprocessor),
                ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
            ])

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)
            pipe.fit(X_train, y_train)
            print(pipe.score(X_test, y_test))
            """,
        ),
        text(
            "Pipeline объединяет препроцессинг и модель в один объект:\n"
            "- `ColumnTransformer` — разные трансформеры для числовых/категориальных признаков.\n"
            "- `StandardScaler` — центрирование и масштабирование (fit на train, transform на test).\n"
            "- `OneHotEncoder(handle_unknown='ignore')` — не падает на новых категориях в test.\n"
            "- `pipe.fit/predict/score` работают прозрачно."
        ),
        heading("Cross-validation и метрики", 3),
        example(
            "python",
            """
            from sklearn.model_selection import cross_val_score, StratifiedKFold
            from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            scores = cross_val_score(pipe, X, y, cv=cv, scoring='roc_auc')
            print(f'ROC-AUC: {scores.mean():.3f} ± {scores.std():.3f}')

            y_pred = pipe.predict(X_test)
            print(classification_report(y_test, y_pred))
            """,
        ),
        text(
            "`StratifiedKFold` сохраняет пропорции классов в фолдах. "
            "`scoring='roc_auc'` — площадь под ROC кривой (для бинарной классификации). "
            "`classification_report` — precision, recall, f1 по классам. "
            "Для несбалансированных данных: `f1`, `roc_auc`, `pr_auc` лучше `accuracy`.\n\n"
            "Другие важные метрики:\n"
            "- Регрессия: MAE, MSE, RMSE, R², MAPE.\n"
            "- Ranking: NDCG, MAP, MRR.\n"
            "- Калибровка: Brier score, calibration curve (reliability diagram).\n"
            "- Бизнес-метрики: profit@k, lift, gain chart.\n\n"
            "Всегда смотрите на `confusion_matrix` и `classification_report` — "
            "агрегатные метрики скрывают проблемы на конкретных классах."
        ),
        heading("Hyperparameter tuning", 3),
        example(
            "python",
            """
            from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
            from scipy.stats import randint

            param_dist = {
                'classifier__n_estimators': randint(50, 300),
                'classifier__max_depth': [None, 10, 20, 30],
                'classifier__min_samples_split': randint(2, 20),
            }

            search = RandomizedSearchCV(pipe, param_dist, n_iter=20, cv=3,
                                        scoring='roc_auc', n_jobs=-1, random_state=42)
            search.fit(X_train, y_train)
            print(search.best_params_)
            """,
        ),
        text(
            "`RandomizedSearchCV` эффективнее `GridSearchCV` для больших пространств. "
            "`n_iter=20` — количество проб. `n_jobs=-1` — все ядра. "
            "Параметры в Pipeline доступны через `__` (дублированный подчёркивание): "
            "`classifier__n_estimators`."
        ),
        heading("Feature Engineering", 3),
        example(
            "python",
            """
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.decomposition import PCA
            from sklearn.feature_selection import SelectKBest, mutual_info_classif

            # Текст
            tfidf = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
            X_text = tfidf.fit_transform(df['description'])

            # PCA
            pca = PCA(n_components=0.95)  # 95% дисперсии
            X_pca = pca.fit_transform(X_scaled)

            # Feature selection
            selector = SelectKBest(mutual_info_classif, k=10)
            X_selected = selector.fit_transform(X, y)
            """,
        ),
        text(
            "`TfidfVectorizer` — текст в числовые векторы (n-gramмы). "
            "`PCA(n_components=0.95)` — оставляет компоненты, объясняющие 95% дисперсии. "
            "`SelectKBest` + `mutual_info_classif` — отбор k лучших признаков по взаимной информации.\n\n"
            "Дополнительные техники Feature Engineering:\n"
            "- Полиномиальные признаки: `PolynomialFeatures(degree=2)` — взаимодействия.\n"
            "- Дата/время: год, месяц, день недели, квартал, is_weekend, days_since_epoch.\n"
            "- Текст: TF-IDF, CountVectorizer, HashingVectorizer (для больших корпусов).\n"
            "- Категориальные: Target Encoding (mean target per category), Leave-One-Out Encoding.\n"
            "- Числовые: лог-трансформация (для скошенных), binning (квантили), scaling.\n"
            "- Взаимодействия: `x1 * x2`, `x1 / x2`, domain-specific ratios.\n\n"
            "Важно: все трансформации фитятся ТОЛЬКО на train (Pipeline), иначе data leakage."
        ),
        heading("Основы Deep Learning (PyTorch)"),
        heading("Тензоры и автоград", 3),
        example(
            "python",
            """
            import torch
            import torch.nn as nn
            import torch.optim as optim

            # Тензоры
            x = torch.tensor([1., 2., 3.], requires_grad=True)
            y = x ** 2 + 2 * x + 1
            y.sum().backward()
            print(x.grad)  # градиенты
            """,
        ),
        text(
            "Тензор — многомерный массив (как NumPy), но с поддержкой GPU и автограда. "
            "`requires_grad=True` включает отслеживание операций для градиентов. "
            "`.backward()` вычисляет градиенты по цепочке (автоград)."
        ),
        heading("Простая нейросеть", 3),
        example(
            "python",
            """
            class Net(nn.Module):
                def __init__(self, input_dim, hidden_dim, output_dim):
                    super().__init__()
                    self.layers = nn.Sequential(
                        nn.Linear(input_dim, hidden_dim),
                        nn.ReLU(),
                        nn.Dropout(0.3),
                        nn.Linear(hidden_dim, hidden_dim),
                        nn.ReLU(),
                        nn.Linear(hidden_dim, output_dim)
                    )

                def forward(self, x):
                    return self.layers(x)

            model = Net(20, 64, 2)
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(model.parameters(), lr=0.001)

            # Обучение
            for epoch in range(100):
                model.train()
                optimizer.zero_grad()
                outputs = model(X_train_tensor)
                loss = criterion(outputs, y_train_tensor)
                loss.backward()
                optimizer.step()
            """,
        ),
        text(
            "`nn.Module` — базовый класс модели. `nn.Sequential` — контейнер слоёв. "
            "`nn.Linear` — полносвязный слой. `nn.ReLU` — активация. `nn.Dropout` — регуляризация. "
            "`CrossEntropyLoss` = LogSoftmax + NLLLoss (для классификации). "
            "`Adam` — адаптивный оптимизатор (lr=1e-3 хорошее дефолтное значение). "
            "Цикл: `zero_grad()` → `forward` → `loss` → `backward()` → `step()`.\n\n"
            "Важные детали обучения:\n"
            "- `model.train()` / `model.eval()` — переключает Dropout/BatchNorm режимы.\n"
            "- `torch.no_grad()` — отключает автоград для inference/validation (экономит память).\n"
            "- Gradient clipping: `torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)` — предотвращает взрыв градиентов.\n"
            "- Learning rate scheduling: `StepLR`, `CosineAnnealingLR`, `ReduceLROnPlateau`.\n"
            "- Early stopping: мониторьте val loss, останавливайте когда не улучшается N эпох.\n\n"
            "GPU: `model.to('cuda')`, `data.to('cuda')`. Для multi-GPU: `nn.DataParallel` или `DistributedDataParallel` (DDP)."
        ),
        heading("DataLoader", 3),
        example(
            "python",
            """
            from torch.utils.data import DataLoader, TensorDataset

            dataset = TensorDataset(X_tensor, y_tensor)
            loader = DataLoader(dataset, batch_size=32, shuffle=True)

            for batch_X, batch_y in loader:
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                ...
            """,
        ),
        text(
            "`DataLoader` — батчирование, перемешивание, параллельная загрузка (`num_workers`). "
            "`TensorDataset` оборачивает тензоры в Dataset. Для своих данных наследуйтесь от `Dataset`."
        ),
        heading("Transfer Learning (torchvision)", 3),
        example(
            "python",
            """
            import torchvision.models as models
            import torchvision.transforms as transforms

            resnet = models.resnet18(pretrained=True)
            # Заморозка backbone
            for param in resnet.parameters():
                param.requires_grad = False
            # Замена последнего слоя
            resnet.fc = nn.Linear(resnet.fc.in_features, num_classes)

            # Только fc обучается
            optimizer = optim.Adam(resnet.fc.parameters(), lr=1e-3)
            """,
        ),
        text(
            "Transfer Learning — берём предобученную модель (ImageNet), заморозка backbone, "
            "замена головы (`fc`) под свои классы. Обучается только новый слой — быстро, "
            "качественно, мало данных нужно. `torchvision.models`: resnet, efficientnet, vit, convnext.\n\n"
            "Стратегии fine-tuning:\n"
            "1. Feature extraction: заморозка backbone, обучение только головы (мало данных).\n"
            "2. Full fine-tuning: разморозка всех слоёв, малый lr (1e-4..1e-5) для всего (много данных).\n"
            "3. Gradual unfreezing: сначала голова, потом последние блоки backbone, потом всё.\n"
            "4. Discriminative learning rates: разные lr для разных слоёв (голова — выше, backbone — ниже).\n\n"
            "Аугментации (torchvision.transforms v2): `RandomResizedCrop`, `RandomHorizontalFlip`, "
            "`ColorJitter`, `AutoAugment`, `MixUp`, `CutMix`. Критично для generalisation."
        ),
        heading("Экосистема и инструменты"),
        table(
            ["Задача", "Библиотека"],
            [
                ["NLP", "spaCy, transformers (HuggingFace), nltk"],
                ["Computer Vision", "OpenCV, albumentations, torchvision"],
                ["Time Series", "prophet, statsmodels, sktime"],
                ["Graphs", "networkx, PyTorch Geometric"],
                ["AutoML", "optuna, hyperopt, auto-sklearn"],
                ["Experiment Tracking", "MLflow, Weights & Biases, ClearML"],
                ["Model Serving", "FastAPI + ONNX, TorchServe, Triton"],
            ],
        ),
        heading("MLflow — трекинг экспериментов", 3),
        example(
            "python",
            """
            import mlflow
            import mlflow.sklearn

            mlflow.set_experiment("my-experiment")

            with mlflow.start_run():
                mlflow.log_param("n_estimators", 100)
                mlflow.log_param("max_depth", 10)
                mlflow.log_metric("accuracy", 0.92)
                mlflow.sklearn.log_model(pipe, "model")

            # UI: mlflow ui
            """,
        ),
        text(
            "MLflow трекает: параметры (`log_param`), метрики (`log_metric`), артефакты/модели "
            "(`log_model`). `mlflow ui` запускает веб-интерфейс для сравнения runs. "
            "Интеграция: `mlflow.sklearn`, `mlflow.pytorch`, `mlflow.tensorflow`. "
            "Модель можно задеплоить: `mlflow models serve -m runs:/<run_id>/model`."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Последствия", "Как правильно"],
            [
                ["Data leakage (тест в train)", "Завышенные метрики, модель не работает в проде", "Строгое разделение ДО feature engineering. Pipeline фитит только на train."],
                ["Масштабирование до split", "Среднее/стд теста утекает в train", "Scaler.fit на train, transform на test (Pipeline делает автоматически)."],
                ["Небаланс классов игнорируется", "Модель предсказывает мажоритарный класс", "class_weight='balanced', SMOTE, stratified CV, правильные метрики."],
                ["Метрика accuracy на несбалансированных", "99% accuracy, но 0% recall на минорном", "F1, ROC-AUC, PR-AUC, confusion matrix."],
                ["Нет baseline", "Непонятно, лучше ли модель случайного угадывания", "Сначала простая модель: LogReg / RandomForest /DummyClassifier."],
                ["Overfitting без регуляризации", "100% train accuracy, 50% test", "Dropout, weight decay (L2), early stopping, больше данных/аугментация."],
                ["Feature engineering на всем датасете", "Data leakage через статистики", "Только на train. Pipeline + ColumnTransformer."],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Для PyTorch нужен `pip install torch torchvision`. "
            "Для MLflow — `pip install mlflow` и `mlflow ui` в отдельном терминале."
        ),
        numbered(
            "EDA: загрузите датасет (Titanic / California Housing / Wine Quality из sklearn.datasets). "
            "Сделайте полный анализ: describe, histograms, correlation heatmap, missing values, target distribution.",
            "Baseline: постройте baseline модель (LogisticRegression / RandomForest) для классификации "
            "или LinearRegression для регрессии. Логируйте параметры и метрики в MLflow.",
            "Feature Engineering: создайте новые признаки (полиномиальные, взаимодействия, лог-трансформации). "
            "Попробуйте PCA и feature selection. Улучшите метрику относительно baseline.",
            "NN: реализуйте простую MLP на PyTorch для классификации (3-4 слоя, Dropout, BatchNorm). "
            "Сравните с sklearn моделью. Логируйте loss curves в MLflow.",
            "Deploy: оберните лучшую модель в FastAPI (`/predict` эндпоинт). Сделайте Docker образ. "
            "Протестируйте: `curl -X POST -d '{\"features\": [...]}' http://localhost:8000/predict`.",
        ),
        text("Пример ожидаемого результата для первого задания (Titanic):"),
        example(
            "text",
            "Shape: (891, 12)\n"
            "Survived: 0=549, 1=342\n"
            "Missing: Age=177, Cabin=687, Embarked=2\n"
            "Correlation heatmap: Fare<->Survived (0.26), Pclass<->Survived (-0.34)\n"
            "Baseline LogisticRegression CV ROC-AUC: 0.82 ± 0.03",
        ),
        callout(
            "success",
            "Подсказка к заданию 2",
            "MLflow: `mlflow.set_experiment('titanic')`. Внутри `with mlflow.start_run():` логируйте всё. "
            "`mlflow.sklearn.log_model(pipe, 'model')` сохраняет Pipeline целиком. "
            "Для sklearn моделей `log_model` работает из коробки. Для PyTorch — `mlflow.pytorch.log_model`.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем NumPy массив отличается от Python списка?",
            "Что такое броадкастинг в NumPy и зачем он нужен?",
            "В чём разница между `loc` и `iloc` в Pandas?",
            "Зачем нужен Pipeline в scikit-learn?",
            "Почему `StratifiedKFold` лучше обычного `KFold` для классификации?",
            "Что делает `requires_grad=True` в PyTorch?",
            "Какие метрики использовать для несбалансированной классификации?",
            "Что такое data leakage и как его избежать?",
        ),
        heading("Ответы", 3),
        numbered(
            "NumPy массив — непрерывный блок памяти с единым типом, операции векторизованы на C (10-100x быстрее). Список — массив указателей на объекты Python.",
            "Броадкастинг — автоматическое расширение размерностей массивов для поэлементных операций. Правило: размерности совместимы, если равны или одна равна 1.",
            "`loc` — по метке индекса (можно строки), `iloc` — по целочисленной позиции (всегда int).",
            "Pipeline объединяет препроцессинг и модель. Гарантирует: fit только на train, нет data leakage, удобное CV и деплой.",
            "StratifiedKFold сохраняет пропорции классов в каждом фолде. Важно для несбалансированных данных — иначе фолд может не содержать минорный класс.",
            "Включает отслеживание операций для автограда. Градиенты накапливаются в `.grad` после `.backward()`.",
            "F1, ROC-AUC, PR-AUC, Precision@K, Recall@K. Accuracy бесполезна. Confusion matrix для понимания ошибок.",
            "Data leakage — использование информации из test при обучении. Избегайте: split ДО feature engineering, Pipeline, Scaler.fit только на train.",
        ),
        heading("Итоги"),
        bullets(
            "NumPy: векторизация, броадкастинг, линейная алгебра (`@`, `linalg`), статистика — фундамент всего стека.",
            "Pandas: DataFrame/Series, чтение (CSV/Parquet/SQL), индексация (loc/iloc), GroupBy/agg/pivot, Time Series (resample/rolling), merge/concat.",
            "Визуализация: Matplotlib (база, полный контроль), Seaborn (статистика одной строкой), Plotly (интерактивно, HTML).",
            "Sklearn: Pipeline (ColumnTransformer + Model), CV (StratifiedKFold), метрики (ROC-AUC, F1, PR-AUC), RandomizedSearchCV, Feature Engineering (TF-IDF, PCA, SelectKBest).",
            "PyTorch: тензоры + автоград, nn.Module/Sequential, DataLoader, Transfer Learning (torchvision). GPU: `.to('cuda')`.",
            "MLflow: эксперименты (params, metrics, artifacts, models), UI для сравнения, деплой моделей.",
            "Ошибки: data leakage (split до FE), scaling до split, небаланс классов (class_weight, stratified CV, правильные метрики), overfitting (dropout, weight decay, early stopping).",
        ),
        heading("Что дальше"),
        text(
            "Data Science — огромная область. Следующие шаги: NLP (transformers, BERT, LLM fine-tuning), "
            "Computer Vision (detection, segmentation, diffusion), MLOps (Kubeflow, Feast, model monitoring, "
            "data drift detection), распределённое обучение (DDP, FSDP, DeepSpeed), Generative AI. "
            "В следующем уроке разберём профессиональные инструменты: линтеры, типизация, тестирование, "
            "документация, пакетирование, CI/CD для библиотек."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "NumPy Docs — numpy.org/doc/",
            "Pandas Docs — pandas.pydata.org/docs/",
            "Scikit-learn User Guide — scikit-learn.org/stable/user_guide.html",
            "PyTorch Tutorials — pytorch.org/tutorials/",
            "Paper: \"A Few Useful Things to Know about ML\" — Pedro Domingos",
            "Hands-On ML with Scikit-Learn, Keras & TensorFlow — Aurélien Géron",
            "MLflow — mlflow.org/docs/latest/index.html",
            "Feature Engineering for ML — Kuhn & Johnson",
        ),
    ],
}