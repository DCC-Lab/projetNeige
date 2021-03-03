
unitIdList = [1,2,3,4,5,6,7,8]
pdIdList = [1,2,3,4]

for uid in unitIdList:
    for pid in pdIdList:
        print(f"t1_{uid}{pid}.detector{uid}{pid}, t1_{uid}{pid}_s.detector{uid}{pid}_s, ")

for uid in unitIdList:
    for pid in pdIdList:
        print(f"JOIN (SELECT t1.timestamp,t1.powerMean AS detector{uid}{pid} FROM PhotodiodeData t1 WHERE t1.unit_id='{uid}' AND t1.pd_id='{pid}' ORDER BY timestamp) t1_{uid}{pid} ON t1a.timestamp = t1_{uid}{pid}.timestamp JOIN (SELECT t1.timestamp,t1.powerSD AS detector{uid}{pid}_s FROM PhotodiodeData t1 WHERE t1.unit_id='{uid}' AND t1.pd_id='{pid}' ORDER BY timestamp) t1_{uid}{pid}_s ON t1a.timestamp = t1_{uid}{pid}_s.timestamp")