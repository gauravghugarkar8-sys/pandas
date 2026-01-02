from django.shortcuts import render
from .forms import CSVUploadForm
import pandas as pd
import numpy as np

def upload_csv(request):
    preview = None
    operations = {}
    df_dropped=None

    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES) #select the file
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_csv(file)

            # =============================
            # BASIC INFO
            # =============================
            operations['shape'] = df.shape
            operations['columns'] = list(df.columns)

            # =============================
            # MISSING VALUES
            # =============================
            operations['missing_before'] = df.isnull().sum().to_dict()

            # fillna
            df_filled = df.fillna(0)

            # dropna

            df_dropped = df.dropna().to_html()

            operations['missing_after_fill'] = df_filled.isnull().sum().to_dict()

            # =============================
            # TYPE CONVERSION
            # =============================
            for col in df_filled.select_dtypes(include='object'):
                try:
                    df_filled[col] = df_filled[col].astype(str)
                except:
                    pass

            # =============================
            # COLUMN OPERATIONS
            # =============================
            df_filled.columns = [c.lower() for c in df_filled.columns]  # rename

            # =============================
            # SORTING
            # =============================
            sorted_df = df_filled.sort_values(by=df_filled.columns[0])

            # =============================
            # FILTERING
            # =============================
            numeric_cols = df_filled.select_dtypes(include=np.number)
            filtered_df = numeric_cols[numeric_cols > numeric_cols.mean()]

            # =============================
            # AGGREGATION
            # =============================
            operations['sum'] = numeric_cols.sum().to_dict()
            operations['mean'] = numeric_cols.mean().to_dict()
            operations['min'] = numeric_cols.min().to_dict()
            operations['max'] = numeric_cols.max().to_dict()

            # =============================
            # GROUP BY (if possible)
            # =============================
            if len(df_filled.columns) >= 2:
                group_col = df_filled.columns[0]
                num_col = numeric_cols.columns[0] if not numeric_cols.empty else None

                if num_col:
                    operations['groupby'] = (
                        df_filled.groupby(group_col)[num_col].sum().to_dict()
                    )

            # =============================
            # PREVIEW
            # =============================
            preview = df_filled.head(10).to_html() #CSV मधल्या पहिल्या 10 rows घेते आणि त्या HTML table मध्ये बदलते

    else:
        form = CSVUploadForm()

    return render(request, "panda/upload.html", {
        "form": form,
        "preview": preview,
        "operations": operations,
        "df_dropped":df_dropped
    })
