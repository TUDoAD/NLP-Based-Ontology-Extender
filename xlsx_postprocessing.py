import pandas as pd


def postprocessing(df, name):
    # function to split "_" token, delete duplicate and store into xlsx file
    classes_df = df[1]

    # deleting "_"
    classes_del_ = []
    for i in classes_df:
        classes_del_.append(i.replace("_", " "))

    # deleting duplicates
    df_class = pd.DataFrame(classes_del_)
    df_classes = df_class.drop_duplicates()

    # storing into xlsx file
    df_classes.to_excel(str(name) + ".xlsx")
