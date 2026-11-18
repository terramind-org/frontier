from bases import *
row = read("baseline.json")["colors"][:536]
anchor = read("inputs/base14.json")["colors"]
data = {}
for p in sorted(Path("inputs").glob("b1_00*.json")):
    colors = read(p)["colors"]
    assert len(colors)==536 and valid(colors,6)
    data[p.stem] = features(colors,row,anchor)
data["anchor"] = features(anchor,row,anchor)
data["rowley"] = features(row,row,anchor)
save("logs/initial-features.json",data)
