// Exact monochromatic x+y=z objective; x=y contributes once. One CPU thread.
#include <algorithm>
#include <array>
#include <chrono>
#include <fstream>
#include <iostream>
#include <random>
#include <vector>
using namespace std;
struct Tri{array<int,3> v;int m;};
int main(int argc,char**argv){
 int seconds=stoi(argv[1]);string dir=argv[2];mt19937 rng(7301698);const int n=1697;
 vector<int> base;{ifstream f(dir+"/baseline.txt");int x;while(f>>x)base.push_back(x);}if(base.size()!=1696)return 2;
 vector<Tri> ts;vector<vector<int>> inc(n);for(int x=1;x<=n/2;x++)for(int y=x;y<=n-x;y++){
  Tri t=x==y?Tri{{x-1,x+y-1,0},2}:Tri{{x-1,y-1,x+y-1},3};int id=ts.size();ts.push_back(t);for(int j=0;j<t.m;j++)inc[t.v[j]].push_back(id);
 }
 vector<int>a(n),bad,pos(ts.size(),-1);vector<array<int,7>>cost(n),tabu(n);int total=0,best=1000000;long long moves=0;
 auto isbad=[&](int id){auto&t=ts[id];for(int j=1;j<t.m;j++)if(a[t.v[j]]!=a[t.v[0]])return false;return true;};
 auto adjust=[&](int id,int sign){auto&t=ts[id];for(int j=0;j<t.m;j++){int c=-1;bool ok=true;for(int k=0;k<t.m;k++)if(k!=j){int d=a[t.v[k]];if(c>=0&&c!=d){ok=false;break;}c=d;}if(ok)cost[t.v[j]][c]+=sign;}};
 auto update=[&](int id){bool b=isbad(id);if(b&&pos[id]<0){pos[id]=bad.size();bad.push_back(id);}else if(!b&&pos[id]>=0){int p=pos[id];pos[bad.back()]=p;bad[p]=bad.back();bad.pop_back();pos[id]=-1;}};
 auto score=[&](){int t=0;for(int id=0;id<(int)ts.size();id++)t+=isbad(id);return t;};
 auto save=[&](){ofstream f(dir+"/local-best.json");f<<"{\"colors\":[";for(int i=0;i<n;i++)f<<(i?",":"")<<a[i];f<<"]}\n";};
 auto begin=chrono::steady_clock::now();auto elapsed=[&](){return chrono::duration<double>(chrono::steady_clock::now()-begin).count();};
 cout<<"START seed 7301698 budget "<<seconds<<" triples "<<ts.size()<<endl;
 int restart=0;while(elapsed()<seconds){
  copy(base.begin(),base.end(),a.begin());a[n-1]=rng()%7;
  if(restart%3==1&&best<1000000){ifstream f(dir+"/local-best.txt");for(int&i:a)f>>i;for(int j=0;j<5+restart%31;j++)a[rng()%n]=rng()%7;}
  for(auto&c:cost)c.fill(0);for(auto&t:tabu)t.fill(0);bad.clear();fill(pos.begin(),pos.end(),-1);
  for(int id=0;id<(int)ts.size();id++){adjust(id,1);update(id);}total=bad.size();
  if(restart==0){a[n-1]=a[n-1];cout<<"SELFTEST baseline_prefix_valid checked by Python; initial score "<<score()<<endl;}
  for(int step=1;step<=100000&&elapsed()<seconds;step++,moves++){
   if(total<best){best=total;save();ofstream f(dir+"/local-best.txt");for(int c:a)f<<c<<' ';cout<<"BEST "<<best<<" seconds "<<elapsed()<<" moves "<<moves<<" restart "<<restart<<endl;}
   if(!total){cout<<"VALID zero objective"<<endl;return 0;}
   int id=bad[rng()%bad.size()];auto&t=ts[id];int bv=-1,bc=-1,delta=100000,choices=0;
   for(int j=0;j<t.m;j++){int v=t.v[j];for(int c=0;c<7;c++)if(c!=a[v]){int d=cost[v][c]-cost[v][a[v]];if(tabu[v][c]>step&&total+d>=best)continue;if(d<delta){delta=d;choices=0;}if(d==delta&&rng()%++choices==0){bv=v;bc=c;}}}
   if(bv<0)continue;
   if(rng()%100<2){bv=t.v[rng()%t.m];bc=rng()%7;}
   int old=a[bv];for(int q:inc[bv])adjust(q,-1);a[bv]=bc;for(int q:inc[bv]){adjust(q,1);update(q);}total=bad.size();tabu[bv][old]=step+7+rng()%17;
   if(step%10000==0){int exact=score();if(exact!=total){cerr<<"BUG objective mismatch";return 3;}cout<<"PROGRESS seconds "<<elapsed()<<" moves "<<moves<<" current "<<total<<" best "<<best<<endl;}
  }restart++;
 }
 cout<<"END seconds "<<elapsed()<<" moves "<<moves<<" restarts "<<restart<<" best "<<best<<" exit 0"<<endl;
}
