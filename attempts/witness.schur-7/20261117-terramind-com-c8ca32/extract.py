import json, pathlib, xlrd, hashlib
p=pathlib.Path(__file__).resolve().parent
b=xlrd.open_workbook(str(p/'ancillary/specimens.xls'))
s=b.sheet_by_name('S(7) >= 1696')
a=[]
for r in range(5,1701):
 assert s.cell_value(r,3)==len(a)+1
 a.append(int(s.cell_value(r,4))-1)
assert len(a)==1696
(p/'baseline.json').write_text(json.dumps({'colors':a})+'\n')
(p/'baseline.txt').write_text(' '.join(map(str,a)))
bad=a.copy();bad[1]=bad[0]
(p/'broken.json').write_text(json.dumps({'colors':bad})+'\n')
s=b.sheet_by_name('S(7) >= 1664')
a=[int(s.cell_value(r,5))-1 for r in range(5,1669)]
(p/'template1664.json').write_text(json.dumps({'colors':a})+'\n')
print('Extracted baseline1696 and template1664; spreadsheet SHA256',hashlib.sha256((p/'ancillary/specimens.xls').read_bytes()).hexdigest())
