import pandas as pd


def make_pivot_csv_file(filePath):
    pivot_df = pd.DataFrame(columns=["timestamp", "11_avg", "11_sd", "12_avg", "12_sd", "13_avg", "13_sd"
, "14_avg", "14_sd", "21_avg", "21_sd", "22_avg", "22_sd", "23_avg", "23_sd", "24_avg", "24_sd", "31_avg", "31_sd", "32_avg", "32_sd",
"33_avg", "33_sd", "34_avg", "34_sd", "41_avg", "41_sd"
, "42_avg", "42_sd", "43_avg", "43_sd", "44_avg", "44_sd", "51_avg", "51_sd", "52_avg", "52_sd", "53_avg", "53_sd", "54_avg", "54_sd"
, "61_avg", "61_sd", "62_avg", "62_sd", "63_avg", "63_sd", "64_avg", "64_sd", "71_avg", "71_sd", "72_avg", "72_sd", "73_avg", "73_sd"
, "74_avg", "74_sd", "81_avg", "81_sd", "82_avg", "82_sd", "83_avg", "83_sd", "84_avg", "84_sd"])

    df = pd.read_csv(filePath, index_col=False, header=0)
    # with pd.option_context('display.max_columns', None):  # more options can be specified also
        # print(df)
    last = None
    toPush = {}

    for index, row in df.iterrows():
        current = row[" timeStamp"]

        if last is None:
            last = current

        if current != last:
            toPush["timestamp"] = last
            # print(toPush)
            pivot_df = pivot_df.append(pd.Series(toPush), ignore_index=True)
            toPush = {}

            i = row[" unitID"]
            j = row[" photodiodeID"]
            avg = row[" powerMean"]
            sd = row[" powerSD"]

            toPush[f"{i}{j}_avg"] = avg
            toPush[f"{i}{j}_sd"] = sd

        elif current == last:
            i = row[" unitID"]
            j = row[" photodiodeID"]
            avg = row[" powerMean"]
            sd = row[" powerSD"]

            toPush[f"{i}{j}_avg"] = avg
            toPush[f"{i}{j}_sd"] = sd

        if index % 10000 == 0:
            a = index * 100 / df.shape[0]
            print(f"{a:.2f}%")

        last = current

    print(pivot_df)
    df.to_csv('pivotted_all_data.csv', index=False)

make_pivot_csv_file("C:/Users/dcclab/Documents/Github/projetNeige/server/developmentServer/data/2020-12-04-2021-04-10.csv")