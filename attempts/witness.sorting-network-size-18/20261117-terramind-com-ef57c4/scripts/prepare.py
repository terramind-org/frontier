import json, pathlib, subprocess
S=pathlib.Path(__file__).resolve().parent
U=S/'upstream/SorterHunter'
for stem,src in [('baseline','Sort_18_77_12.json'),('depth11','Sort_18_78_11.json'),('optimal8','Sort_8_19_6.json')]:
    x=json.loads((U/'Networks/Sorters'/src).read_text())
    (S/f'{stem}.json').write_text(json.dumps({'comparators':x['nw']}))
old=pathlib.Path('attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f/logs/network_77_found_by_SorterHunter_seedB.json')
if old.exists():
    (S/'round1.json').write_text(old.read_text())
else:
    import urllib.request, hashlib
    download=S/'round1-download';download.mkdir(exist_ok=True)
    data=urllib.request.urlopen('https://raw.githubusercontent.com/terramind-org/frontier/09ffd987b038ff0b0ea37967e0eee1e83375c5f4/attempts/witness.sorting-network-size-18/20261117-terramind-com-666b8f/logs/network_77_found_by_SorterHunter_seedB.json',timeout=30).read()
    assert hashlib.sha256(data).hexdigest()=='f740691f07fd453621ef92273a314ef50a18f8002d8c84c7598271d0e2d54a20'
    (download/'network.json').write_bytes(data)
    (S/'round1.json').write_bytes(data)
(S/'provenance.json').write_text(json.dumps({'upstream':'https://github.com/bertdobbelaere/SorterHunter','commit':subprocess.check_output(['git','-C',str(U),'rev-parse','HEAD'],text=True).strip(),'python':subprocess.check_output([str(S/'.venv/bin/python'),'--version'],text=True).strip(),'dependencies':subprocess.check_output(['uv','pip','freeze','--python',str(S/'.venv/bin/python')],text=True)},indent=2))
p=U/'SorterHunter.cpp'
x=subprocess.check_output(['git','-C',str(U),'show','HEAD:SorterHunter.cpp'],text=True)
# Instrumentation adds no RNG calls and does not change acceptance or mutation.
x='''#include <unordered_set>
#include <string>
#include <cmath>
static unsigned char registers_hll[65536]={0};
static uint64_t candidate_observations=0;
static void count_candidate(const Network_t &network);
'''.replace('static void count_candidate(const Network_t &network);','')+x
# Network_t is defined by upstream includes, so place implementations before main.
anchor='int main(int argc, char *argv[])'
instrument='''static void count_candidate(const Network_t &network) {
 uint64_t h=14695981039346656037ull;
 for(const auto &p: network) { h^=p.lo; h*=1099511628211ull; h^=p.hi; h*=1099511628211ull; }
 h^=h>>33; h*=0xff51afd7ed558ccdull; h^=h>>33; h*=0xc4ceb9fe1a85ec53ull; h^=h>>33;
 uint64_t index=h&65535u; uint64_t tail=h>>16;
 unsigned char rank=tail ? __builtin_clzll(tail)-15 : 49;
 if(rank>registers_hll[index]) registers_hll[index]=rank;
 ++candidate_observations;
}
static double cardinality_estimate() {
 double inv=0; unsigned zeros=0;
 for(unsigned char r:registers_hll) { inv+=std::ldexp(1.,-r); if(r==0) ++zeros; }
 double m=65536.; double estimate=(0.7213/(1.+1.079/m))*m*m/inv;
 if(estimate<=2.5*m && zeros) estimate=m*std::log(m/zeros);
 return estimate;
}
'''
x=x.replace(anchor,instrument+anchor)
x=x.replace('int main(int argc, char *argv[])\n{','int main(int argc, char *argv[])\n{\n setvbuf(stdout, NULL, _IOLBF, 0);\n std::unordered_set<std::string> sampled_candidates;\n uint64_t samples=0, max_distance=0;\n Network_t initial_expanded;')
x=x.replace('checkImproved(totalnw);\n\n\t\tfor(;;)', 'checkImproved(totalnw);\n        initial_expanded=se;\n\n\t\tfor(;;)')
needle='printf("Iteration %lu  t=%.3lf s     %.1lf it/s\\n", itercount, t,  (iter_next_report-iter_last_report)/dt );'
x=x.replace(needle,needle+'\n printf("HLLDistinctEstimate %.1f CandidateObservations %llu RelativeStandardError 0.0040625\\n",cardinality_estimate(),(unsigned long long)candidate_observations);\n printf("SampledCandidates %llu DistinctSampled %lu MaxPositionDistance %llu\\n", (unsigned long long)samples, sampled_candidates.size(), (unsigned long long)max_distance);')
needle='/* Test whether the new postfix network yields a valid sorter when combined with the prefix */'
x=x.replace(needle,'''count_candidate(se);
 if ((itercount & 65535u)==0) {
 std::string key; uint64_t dist=0;
 for(size_t z=0;z<se.size();++z) { key.push_back(se[z].lo); key.push_back(se[z].hi); if(z>=initial_expanded.size() || se[z]!=initial_expanded[z]) ++dist; }
 if(initial_expanded.size()>se.size()) dist+=initial_expanded.size()-se.size();
 sampled_candidates.insert(key); ++samples; if(dist>max_distance) max_distance=dist;
 }
 '''+needle)
assert 'initial_expanded=se' in x
p.write_text(x)
