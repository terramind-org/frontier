#!/usr/bin/env python3
"""Convert the catalogue's exact Maple triads at l=1 to Frontier JSON.

The catalogue's final expression subtracts its tensor contribution from AB.
Its TriadSet therefore encodes the negative of the displayed correction; the
Frontier coefficient convention is consequently (T1,T2,T3^T).
"""
import json
import re
from pathlib import Path

SOURCE = Path("source/laderman-3x3x3_tensor.mpl")
text = SOURCE.read_text().replace("-l", "-1").replace("1/l", "1").replace("l", "1")
triads = re.findall(r"Triad\(\[Matrix\(3, 3, \[\[(.*?)\]\]\), Matrix\(3, 3, \[\[(.*?)\]\]\), Matrix\(3, 3, \[\[(.*?)\]\]\)\]\)", text)
assert len(triads) == 23, len(triads)

def matrix(raw):
    rows = raw.split("],[")
    assert len(rows) == 3, raw
    out = [[int(x) for x in row.split(",")] for row in rows]
    assert all(len(row) == 3 for row in out)
    return out

def transpose(m):
    return [[m[j][i] for j in range(3)] for i in range(3)]

terms = [{"a": matrix(a), "b": matrix(b), "c": transpose(matrix(c))}
         for a, b, c in triads]
Path("laderman-frontier-witness.json").write_text(json.dumps({"terms": terms}, indent=2) + "\n")
print(json.dumps({"terms": len(terms), "conversion": "(T1,T2,transpose(T3))", "parameter": "l=1"}))
