#include <algorithm>
#include <array>
#include <iostream>
#include <vector>

struct Outcome {
    int status;   // 20 contradiction, 10 complete, 0 open
    int assigned;
    int position;
    std::vector<unsigned> domains;
};

Outcome propagate(int n,int colors,const std::vector<unsigned>& masks,bool mirror) {
    const int modulus=n+1,extent=mirror?modulus/2:n;
    if(mirror && modulus%3==0) return {20,0,modulus/3,{}};
    std::vector<unsigned> d=masks;
    std::vector<int> queue;
    std::array<std::vector<int>,7> placed;
    auto single=[](unsigned mask) { return mask && !(mask & (mask-1)); };
    auto fold=[=](int x) { return std::min(x,modulus-x); };
    for(int x=1;x<=extent;++x) {
        if(!d[x]) return {20,0,x,{}};
        if(single(d[x])) queue.push_back(x);
    }
    int contradiction=0;
    auto exclude=[&](int x,unsigned bit) {
        if(x==0 || !(d[x]&bit)) return;
        d[x]&=~bit;
        if(!d[x]) contradiction=x;
        else if(single(d[x])) queue.push_back(x);
    };
    for(size_t i=0;i<queue.size();++i) {
        int x=queue[i];
        unsigned bit=d[x];
        int c=0;
        while((1u<<c)!=bit) ++c;
        if(c>=colors) return {20,static_cast<int>(i),x,{}};
        // A fixed representative and two copies of a free representative.
        if(x%2==0) exclude(x/2,bit);
        if(mirror && (modulus-x)%2==0) exclude((modulus-x)/2,bit);
        placed[c].push_back(x);
        // Two fixed representatives. Addition and subtraction cover the
        // choices of their signs around zero in the reflected interval.
        for(int y:placed[c]) {
            if(mirror) exclude(fold(x+y),bit);
            else if(x+y<=n) exclude(x+y,bit);
            exclude(x>y?x-y:y-x,bit);
            if(contradiction) return {20,static_cast<int>(i+1),contradiction,{}};
        }
    }
    int assigned=static_cast<int>(queue.size());
    return {assigned==extent?10:0,assigned,0,std::move(d)};
}

int main() {
    int count;
    if(!(std::cin>>count) || count<1) return 2;
    for(int i=0;i<count;++i) {
        int n,colors,restrictions,mirror;
        if(!(std::cin>>n>>colors>>restrictions>>mirror) || n<1 || colors<1 ||
           colors>7 || restrictions<0 || (mirror!=0 && mirror!=1)) return 2;
        const int m=n+1,extent=mirror?m/2:n;
        auto representative=[=](int x) { return mirror?std::min(x,m-x):x; };
        std::vector<unsigned> masks(extent+1,(1u<<colors)-1);
        for(int r=0;r<restrictions;++r) {
            int x;
            unsigned mask;
            if(!(std::cin>>x>>mask) || x<1 || x>n || mask>=(1u<<colors)) return 2;
            masks[representative(x)] &= mask;
        }
        auto o=propagate(n,colors,masks,mirror);
        std::cout<<o.status<<' '<<o.assigned<<' '<<o.position;
        if(o.status==10) {
            for(int x=1;x<=n;++x) {
                unsigned bit=o.domains[representative(x)];
                int c=0;
                while((1u<<c)!=bit) ++c;
                std::cout<<' '<<c;
            }
        }
        std::cout<<'\n';
    }
}
