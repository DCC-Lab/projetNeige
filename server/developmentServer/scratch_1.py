if __name__ == "__main__":
    import csv

    with open('candle_calibration_info.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        next(csvreader, None)
        calibrationList = []
        for row in csvreader:
            calibrationList.append(row)

        print(calibrationList)