"""Parse the Lille Maple tensor as data, never execute it. Run from repo root."""
import ast, bz2, json, pathlib, re
root=pathlib.Path('.terramind/scratch/matmul5')
s=bz2.decompress((root/'lille/tensor.mpl.bz2').read_bytes()).decode().split('Tensor:=',1)[1]
mat=[ast.literal_eval(x) for x in re.findall(r'Matrix\(5, 5, (\[\[.*?\]\])\)',s)]
assert len(mat)==279, len(mat)
terms=[]; masks=[]
for k in range(0,len(mat),3):
 a,b,d=mat[k:k+3]
 terms.append(dict(a=a,b=b,c=list(map(list,zip(*d)))))
 masks.append([sum((v%2)<<i for i,v in enumerate(sum(m,[]))) for m in (a,b,d)])
(root/'baseline.json').write_text(json.dumps(dict(terms=terms)))
(root/'baseline.mask').write_text('93\n'+'\n'.join(' '.join(map(str,t)) for t in masks)+'\n')
terms[0]['a'][0][0]+=1
(root/'broken.json').write_text(json.dumps(dict(terms=terms)))
print('Parsed 93 terms; c transposed from trace convention.')
