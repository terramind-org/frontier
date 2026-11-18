#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <limits>
#include <random>
#include <vector>

struct Edge {
    std::array<int,3> vertices;
    int count;
};

int main(int argc,char** argv) {
    if (argc!=6) return 2;
    std::ifstream input(argv[1]);
    int n,k;
    if (!(input>>n>>k) || n<1 || k<2 || k>7) return 2;
    std::vector<int> cols(n+1);
    for (int i=1;i<=n;++i) {
        if (!(input>>cols[i]) || cols[i]<0 || cols[i]>=k) return 2;
    }
    std::mt19937_64 rng(std::stoull(argv[3]));
    auto deadline=std::chrono::steady_clock::now()+std::chrono::seconds(std::stoi(argv[4]));
    uint64_t step_limit=std::stoull(argv[5]);
    std::vector<Edge> edges;
    std::vector<std::vector<int>> incident(n+1);
    for (int x=1;2*x<=n;++x) {
        for (int y=x;x+y<=n;++y) {
            int e=static_cast<int>(edges.size());
            if (x==y) edges.push_back({{x,x+y,0},2});
            else edges.push_back({{x,y,x+y},3});
            for(int j=0;j<edges.back().count;++j) incident[edges.back().vertices[j]].push_back(e);
        }
    }
    auto mono=[&](const Edge& e) {
        int c=cols[e.vertices[0]];
        return cols[e.vertices[1]]==c && (e.count==2 || cols[e.vertices[2]]==c);
    };
    std::vector<int> active, position(edges.size(),-1), weight(edges.size(),1);
    auto flag=[&](int id,bool present){
        if (present && position[id]<0) {
            position[id]=static_cast<int>(active.size());
            active.push_back(id);
        } else if (!present && position[id]>=0) {
            int last=active.back();
            active[position[id]]=last;
            position[last]=position[id];
            active.pop_back();
            position[id]=-1;
        }
    };
    for (size_t e=0;e<edges.size();++e) if(mono(edges[e])) flag(static_cast<int>(e),true);
    std::vector<std::array<uint64_t,7>> zobrist(n+1);
    uint64_t hash=0;
    for (int x=1;x<=n;++x) {
        for(int c=0;c<k;++c) zobrist[x][c]=rng();
        hash^=zobrist[x][cols[x]];
    }
    std::array<int,1024> registers{};
    auto seen=[&]{
        unsigned slot=hash&1023u;
        uint64_t tail=(hash>>10)|(uint64_t{1}<<54);
        int zeroes=0;
        while ((tail&1)==0) { ++zeroes; tail>>=1; }
        registers[slot]=std::max(registers[slot],zeroes+1);
    };
    auto persist=[&] {
        std::string tmp=std::string(argv[2])+".part";
        std::ofstream out(tmp);
        out<<"{\"colors\":[";
        for(int x=1;x<=n;++x) out<<(x==1?"":",")<<cols[x];
        out<<"]}\n";
        out.close();
        return static_cast<bool>(out) && std::rename(tmp.c_str(),argv[2])==0;
    };
    uint64_t steps=0, stalls=0;
    int best=static_cast<int>(active.size());
    if (!persist()) return 3;
    std::vector<uint64_t> tabu(n+1);
    while (!active.empty() && steps<step_limit && std::chrono::steady_clock::now()<deadline) {
        seen();
        int e=active[rng()%active.size()];
        int chosen_x=0, chosen_color=0;
        int64_t best_delta=std::numeric_limits<int64_t>::max();
        int ties=0;
        for(int i=0;i<edges[e].count;++i) {
            int x=edges[e].vertices[i];
            std::array<int64_t,7> cost{};
            for(int f:incident[x]) {
                int a=-1;
                bool same=true;
                for(int j=0;j<edges[f].count;++j) {
                    int v=edges[f].vertices[j];
                    if(v==x) continue;
                    if(a>=0 && a!=cols[v]) { same=false; break; }
                    a=cols[v];
                }
                if(same) cost[a]+=weight[f];
            }
            for(int c=0;c<k;++c) {
                if(c==cols[x]) continue;
                int64_t d=cost[c]-cost[cols[x]];
                if(steps<tabu[x]) d+=2;
                if(d<best_delta) {
                    best_delta=d;
                    chosen_x=x;
                    chosen_color=c;
                    ties=1;
                } else if(d==best_delta && rng()%(++ties)==0) {
                    chosen_x=x;
                    chosen_color=c;
                }
            }
        }
        if(best_delta>=0) {
            ++stalls;
            for(int f:active) ++weight[f];
            if(stalls%2048==0) {
                for(int& w:weight) w=std::max(1,w/2);
            }
        }
        if (rng()%1000<6) {
            chosen_x=edges[e].vertices[rng()%edges[e].count];
            do { chosen_color=rng()%k; } while (chosen_color==cols[chosen_x]);
        }
        hash^=zobrist[chosen_x][cols[chosen_x]]^zobrist[chosen_x][chosen_color];
        cols[chosen_x]=chosen_color;
        tabu[chosen_x]=steps+1+rng()%7;
        for(int f:incident[chosen_x]) flag(f,mono(edges[f]));
        ++steps;
        if (static_cast<int>(active.size())<best) {
            best=static_cast<int>(active.size());
            if (!persist()) return 3;
            std::cout<<"best "<<steps<<" "<<best<<std::endl;
        }
    }
    seen();
    double inverse=0;
    int empty=0;
    constexpr double m=1024;
    for(int r:registers) { inverse+=std::ldexp(1.,-r); empty+=r==0; }
    double estimate=(0.7213/(1+1.079/m))*m*m/inverse;
    if(estimate<2.5*m && empty>0) estimate=m*std::log(m/empty);
    std::cout<<"summary "<<steps<<" "<<best<<" "<<stalls<<" "<<estimate<<std::endl;
    return best==0?10:0;
}
