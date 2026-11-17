"""Rebuild kernelwalk.c from Greg Egan's KernelFinder.c and kernelwalk_search.c.

KernelFinder.c is AGPL-3.0 (github.com/superpermutators/superperm, commit 1922a3486a1a06040230b3e69f365a46e79ab2f2,
KernelFinder/KernelFinder.c) and is not included in this attempt. kernelwalk.c = KernelFinder.c up to its search()
function (with <math.h> added) + the first part of kernelwalk_search.c + KernelFinder.c's permutation/successor setup
block from main() + the rest of kernelwalk_search.c.

Usage: python3 -I build_kernelwalk.py <KernelFinder.c> <kernelwalk_search.c> <out.c>
Then:  cc -O3 -o kernelwalk <out.c> -lm
"""
import sys

kf, own, out = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(kf).read()
head = src[:src.index('void search()')].replace('#include <string.h>', '#include <string.h>\n#include <math.h>', 1)
setup = src[src.index('//\tSet up permutations, etc.'):src.index('sprintf(outputFile')]
mine = open(own).read()
marker = mine.index('/*@@')
part1, part2 = mine[:marker], mine[mine.index('@@*/\n') + len('@@*/\n'):]
open(out, 'w').write(head + part1 + setup + part2)
