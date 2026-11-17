// GF(2) flip walks in trace convention: a_ij b_jk d_ki.
// Compile clang++ -O3 -std=c++17 -pthread search.cpp -o search
#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <mutex>
#include <random>
#include <set>
#include <stdexcept>
#include <thread>
#include <vector>
using T=std::array<uint32_t,3>; using S=std::vector<T>;
std::mutex io; std::atomic<bool> found{false};
using Clock=std::chrono::steady_clock;
T rot(T t){return {t[1],t[2],t[0]};}
bool valid(const S&s){
 std::array<uint32_t,625> z{};
 for(auto t:s) for(uint32_t a=t[0];a;a&=a-1) for(uint32_t b=t[1];b;b&=b-1)
  z[__builtin_ctz(a)*25+__builtin_ctz(b)]^=t[2];
 for(int i=0;i<5;i++)for(int j=0;j<5;j++)for(int k=0;k<5;k++)z[(i*5+j)*25+j*5+k]^=1u<<(k*5+i);
 return std::all_of(z.begin(),z.end(),[](auto x){return x==0;});
}
bool symmetric(const S&s){auto v=s;std::sort(v.begin(),v.end());for(auto t:s)if(!std::binary_search(v.begin(),v.end(),rot(t)))return false;return true;}
void normalize(S&s){
 s.erase(std::remove_if(s.begin(),s.end(),[](T t){return !t[0]||!t[1]||!t[2];}),s.end());
 std::sort(s.begin(),s.end()); S out;
 for(size_t i=0;i<s.size();){size_t j=i+1;while(j<s.size()&&s[j]==s[i])j++;if((j-i)&1)out.push_back(s[i]);i=j;}
 s.swap(out);
}
void reduce(S&s){
 normalize(s);bool changed=true;
 while(changed){changed=false;
 for(size_t i=0;i<s.size()&&!changed;i++)for(size_t j=i+1;j<s.size();j++){
  int eq=0,other=-1;for(int k=0;k<3;k++){if(s[i][k]==s[j][k])eq++;else other=k;}
  if(eq==2){s[i][other]^=s[j][other];s.erase(s.begin()+j);normalize(s);changed=true;break;}
 }}
}
// Pair transform: plus replaces x,y by three terms, otherwise flip requires x[k]==y[k].
std::vector<T> transform(T x,T y,int k,bool plus){
 int b=(k+1)%3,c=(k+2)%3;
 if(plus){T z=x;z[k]^=y[k];T u=y;u[b]^=x[b];u[c]=x[c];T v=y;v[c]^=x[c];return {z,u,v};}
 T u=x,v=y;u[b]^=y[b];v[c]^=x[c];return {u,v};
}
std::vector<int> indices(const S&s,T x,T y,bool sym){
 std::vector<int> ids;int n=sym?3:1;
 for(int r=0;r<n;r++){
  for(T t:{x,y}){auto it=std::find(s.begin(),s.end(),t);if(it==s.end())return {};ids.push_back(int(it-s.begin()));}
  x=rot(x);y=rot(y);
 }
 auto copy=ids;std::sort(copy.begin(),copy.end());if(std::adjacent_find(copy.begin(),copy.end())!=copy.end())return {};return ids;
}
bool move(S&s,int i,int j,int k,bool plus,bool sym){
 T x=s[i],y=s[j];auto ids=indices(s,x,y,sym);if(ids.empty())return false;
 auto out=transform(x,y,k,plus);std::sort(ids.rbegin(),ids.rend());for(int at:ids)s.erase(s.begin()+at);
 for(T t:out){s.push_back(t);if(sym){s.push_back(rot(t));s.push_back(rot(rot(t)));}}
 if(sym)normalize(s);else reduce(s);return true;
}
struct Pair{int i,j,k;};
std::vector<Pair> pairs(const S&s){
 std::vector<Pair> out;std::vector<std::pair<uint32_t,int>> v;v.reserve(s.size());
 for(int k=0;k<3;k++){
 v.clear();for(int i=0;i<int(s.size());i++)v.push_back({s[i][k],i});std::sort(v.begin(),v.end());
 for(size_t a=0;a<v.size();){size_t b=a+1;while(b<v.size()&&v[b].first==v[a].first)b++;
 for(size_t i=a;i<b;i++)for(size_t j=i+1;j<b;j++)out.push_back({v[i].second,v[j].second,k});a=b;}}
 return out;
}
void save(const S&s,const std::string&path){std::ofstream f(path);f<<s.size()<<'\n';for(auto t:s)f<<t[0]<<' '<<t[1]<<' '<<t[2]<<'\n';}
void selftest(const S&base){
 if(!valid(base)||!symmetric(base))throw std::runtime_error("baseline must pass and be C3 invariant");
 auto broken=base;broken[0][0]^=1;if(valid(broken))throw std::runtime_error("broken baseline passed");
 for(int sy=0;sy<2;sy++){
 auto s=base;std::mt19937_64 rng(8123+sy);int flips=0,plus=0;
 for(int step=0;step<2000;step++){
  bool ok=false;if(step%19==0&&s.size()<110){for(int t=0;t<100&&!ok;t++)ok=move(s,rng()%s.size(),rng()%s.size(),rng()%3,true,sy);if(ok)plus++;}
  else {auto p=pairs(s);std::shuffle(p.begin(),p.end(),rng);for(auto q:p)if(move(s,q.i,q.j,q.k,false,sy)){ok=true;flips++;break;}}
  if(!valid(s)||(sy&&!symmetric(s)))throw std::runtime_error("transition selftest failed");
 }
 std::cout<<"SELFTEST mode="<<(sy?"C3":"ordinary")<<" baseline=ACCEPT broken=REJECT flips="<<flips<<" plus="<<plus<<" all_transition_tensors=ACCEPT\n";
 }
}
void worker(const S&base,int id,int seconds,const std::string&dir){
 bool sy=id==1;uint64_t seed=2026111700+id;std::mt19937_64 rng(seed);auto start=Clock::now();auto next=start;
 S s=base,reservoir=base;uint64_t flips=0,pluses=0,restarts=0,steps=0,checks=0,reductions=0;int best=base.size();uint64_t runsteps=0;
 int periods[]={256,2048,16384};uint64_t period=periods[0];uint64_t restartLimit=100000;
 {std::lock_guard<std::mutex> l(io);std::cout<<"START worker="<<id<<" mode="<<(sy?"C3":"ordinary")<<" seed="<<seed<<" seconds="<<seconds<<" rank_cap=102 periods=256,2048,16384 restart_limits=100000,300000,500000\n"<<std::flush;}
 while(!found){
 auto now=Clock::now();double elapsed=std::chrono::duration<double>(now-start).count();if(elapsed>=seconds)break;
 if(now>=next){std::lock_guard<std::mutex> l(io);std::cout<<"PROGRESS worker="<<id<<" elapsed="<<elapsed<<" rank="<<s.size()<<" best_GF2="<<best<<" flips="<<flips<<" plus="<<pluses<<" restarts="<<restarts<<" reductions="<<reductions<<" tensor_checks="<<checks<<'\n'<<std::flush;next=now+std::chrono::seconds(60);}
 size_t old=s.size();bool ok=false;
 if(runsteps&&runsteps%period==0&&s.size()+(sy?3:1)<=102){
  for(int a=0;a<100&&!ok;a++)ok=move(s,rng()%s.size(),rng()%s.size(),rng()%3,true,sy);if(ok)pluses++;
 }else{
  auto p=pairs(s);std::shuffle(p.begin(),p.end(),rng);
  for(auto q:p){if(rng()&1)std::swap(q.i,q.j);if(move(s,q.i,q.j,q.k,false,sy)){ok=true;flips++;break;}}
 }
 steps++;runsteps++;if(s.size()<old)reductions++;
 if(s.size()<size_t(best)){
  if(!valid(s)||(sy&&!symmetric(s)))throw std::runtime_error("invalid candidate");checks++;best=s.size();save(s,dir+"/best-"+std::to_string(id)+".mask");
  {std::lock_guard<std::mutex> l(io);std::cout<<"NEW_BEST worker="<<id<<" rank="<<best<<" flips="<<flips<<'\n'<<std::flush;}
  if(best<=92){found=true;break;}
 }
 if((steps&65535)==0){checks++;if(!valid(s)||(sy&&!symmetric(s)))throw std::runtime_error("checkpoint invalid");save(s,dir+"/checkpoint-"+std::to_string(id)+".mask");}
 if(s.size()<=93)reservoir=s;
 if(!ok||runsteps>=restartLimit){checks++;if(!valid(s))throw std::runtime_error("restart invalid");restarts++;rng.seed(seed+1000003*restarts);s=(rng()&1)?base:reservoir;runsteps=0;period=periods[restarts%3];restartLimit=100000+200000*(restarts%3);}
 }
 if(!valid(s))throw std::runtime_error("final invalid");save(s,dir+"/final-"+std::to_string(id)+".mask");
 std::lock_guard<std::mutex> l(io);std::cout<<"FINISH worker="<<id<<" elapsed="<<std::chrono::duration<double>(Clock::now()-start).count()<<" best_GF2="<<best<<" rank="<<s.size()<<" flips="<<flips<<" plus="<<pluses<<" restarts="<<restarts<<" reductions="<<reductions<<" tensor_checks="<<checks+1<<" final_tensor=ACCEPT\n"<<std::flush;
}
int main(int argc,char**argv){try{
 if(argc!=4)throw std::runtime_error("usage: search baseline.mask seconds output_dir");
 std::ifstream f(argv[1]);int n;f>>n;S s(n);for(auto&t:s)for(auto&v:t)f>>v;if(!f)throw std::runtime_error("bad input");
 selftest(s);int seconds=std::stoi(argv[2]);std::thread a(worker,std::cref(s),0,seconds,argv[3]),b(worker,std::cref(s),1,seconds,argv[3]);a.join();b.join();return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
