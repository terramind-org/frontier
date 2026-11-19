#include <cstdint>
#include <vector>
#include <cmath>
#include <cstdio>
#include <cassert>
struct Pair_t { uint8_t lo,hi; };
using Network_t=std::vector<Pair_t>;
static unsigned char registers_hll[65536]={0};
static uint64_t candidate_observations=0;
static void count_candidate(const Network_t &network) {
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
int main() {
 std::vector<Pair_t> pairs;
 for(uint8_t i=0;i<18;i++) for(uint8_t j=i+1;j<18;j++) pairs.push_back({i,j});
 for(size_t k=0;k<10000;k++) count_candidate({pairs[k/153],pairs[k%153]});
 double first=cardinality_estimate();
 for(size_t k=0;k<10000;k++) count_candidate({pairs[k/153],pairs[k%153]});
 double second=cardinality_estimate();
 printf("Known distinct 10000; estimate %.3f; after duplicates %.3f; observations %llu\n",first,second,(unsigned long long)candidate_observations);
 assert(first==second && std::abs(first-10000)<300);
}
