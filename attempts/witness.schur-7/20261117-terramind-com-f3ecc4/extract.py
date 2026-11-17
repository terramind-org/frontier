"""Extract Rowley's S(7) >= 1696 partition from the arXiv ancillary spreadsheet into Frontier witness JSON."""
import sys, json, xlrd
wb = xlrd.open_workbook(sys.argv[1])
sh = [s for s in wb.sheets() if s.name.strip() == 'S(7) >= 1696'][0]
pairs = []
for r in range(sh.nrows):
    row = sh.row_values(r)
    nums = [v for v in row if isinstance(v, float)]
    if len(nums) >= 2 and float(nums[0]).is_integer():
        pairs.append((int(nums[0]), int(nums[1])))
print(sh.ncols, pairs[:3], file=sys.stderr)
d = dict(pairs)
assert sorted(d) == list(range(1, 1697)), (min(d), max(d), len(d))
cols = [d[i] - 1 for i in range(1, 1697)]
assert set(cols) == set(range(7))
json.dump({'colors': cols}, open(sys.argv[2], 'w'))
print('ok', len(cols))
