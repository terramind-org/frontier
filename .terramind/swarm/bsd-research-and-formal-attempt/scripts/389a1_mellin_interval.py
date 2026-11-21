from decimal import Decimal as D, localcontext, ROUND_HALF_EVEN
from math import isqrt

PREC=36

def down(x): return x.next_minus()
def up(x): return x.next_plus()
def mul(a,b,lo=True):
    with localcontext() as c:
        c.prec=PREC; c.rounding=ROUND_HALF_EVEN
        z=a*b
        return down(z) if lo else up(z)
def add(a,b,lo=True):
    with localcontext() as c:
        c.prec=PREC; c.rounding=ROUND_HALF_EVEN
        z=a+b
        return down(z) if lo else up(z)
def div(a,b,lo=True):
    with localcontext() as c:
        c.prec=PREC; c.rounding=ROUND_HALF_EVEN
        z=a/b
        return down(z) if lo else up(z)
def expi(x,lo=True):
    with localcontext() as c:
        c.prec=PREC; c.rounding=ROUND_HALF_EVEN
        z=x.exp()
        return down(z) if lo else up(z)
def lni(x,lo=True):
    with localcontext() as c:
        c.prec=PREC; c.rounding=ROUND_HALF_EVEN
        z=x.ln()
        return down(z) if lo else up(z)
def sqrti(x,lo=True):
    with localcontext() as c:
        c.prec=PREC; c.rounding=ROUND_HALF_EVEN
        z=x.sqrt()
        return down(z) if lo else up(z)

def interval_mul(a,b):
    return (min(mul(x,y,True) for x in a for y in b), max(mul(x,y,False) for x in a for y in b))

def primes(n):
    return [p for p in range(2,n+1) if all(p%d for d in range(2,isqrt(p)+1))]

def coeffs(N):
    # a_p = p+1-#E(F_p); recurrence a_{p^r}=a_p*a_{p^(r-1)}-p*a_{p^(r-2)}.
    aps={}
    for p in primes(N):
        count=1
        for x in range(p):
            rhs=(x*x*x+x*x-2*x)%p
            # y^2+y=rhs; count roots by direct enumeration.
            count += sum(1 for y in range(p) if (y*y+y-rhs)%p==0)
        aps[p]=p+1-count
    a=[0]*(N+1); a[1]=1
    for n in range(2,N+1):
        p=next(p for p in aps if n%p==0)
        m=n; k=0
        while m%p==0: m//=p; k+=1
        power=[1,aps[p]]
        for r in range(2,k+1): power.append(aps[p]*power[-1]-p*power[-2])
        a[n]=power[k]*a[m]
    return a,aps

def tail_integral_exp2(k):
    # integral_1^infty t^2 exp(-k*t) dt
    ek=expi(-k,True); den=k
    term1=div(1,den,False)
    term2=div(2,mul(den,den,True),False)
    term3=div(2,mul(mul(den,den,True),den,True),False)
    return mul(ek,add(add(term1,term2,False),term3,False),False)

def tail_integral_exp2_from(k, start):
    # integral_start^infty t^2 exp(-k*t) dt; k>0, start>=0.
    e=expi(-mul(k,start,True),False)
    term1=div(mul(start,start,False),k,False)
    term2=div(mul(D(2),start,False),mul(k,k,True),False)
    term3=div(D(2),mul(mul(k,k,True),k,True),False)
    return mul(e,add(add(term1,term2,False),term3,False),False)

# c interval from 3.14159265358979 < pi < 3.14159265358980 and sqrt(389)
pi=(D('3.14159265358979'),D('3.14159265358980'))
sqrt389=(sqrti(D(389),True),sqrti(D(389),False))
c=(div(mul(D(2),pi[0],True),sqrt389[1],True),div(mul(D(2),pi[1],False),sqrt389[0],False))
N=T=80; h=D(1)/D(16)
a,aps=coeffs(N)
print('precision',PREC,'grid',h,'N=T',N)
print('a_p',aps)
print('a_1..80',a[1:])
print('c_interval',c)
# Each grid cell t=[left,right], and each n: exp(-cnt) decreasing, log^2 increasing.
Slo=D(0); Shi=D(0)
steps=int((D(T)-D(1))/h)
for i in range(steps):
    left=D(1)+h*i; right=left+h
    loglo=lni(left,True); loghi=lni(right,False)
    log2lo=mul(loglo,loglo,True); log2hi=mul(loghi,loghi,False)
    celllo=D(0); cellhi=D(0)
    for n in range(1,N+1):
        xlo=mul(mul(c[0],D(n),True),left,True)
        xhi=mul(mul(c[1],D(n),False),right,False)
        elo=expi(-xhi,True); ehi=expi(-xlo,False)
        plo=mul(elo,log2lo,True); phi=mul(ehi,log2hi,False)
        if a[n]>=0:
            celllo=add(celllo,mul(D(a[n]),plo,True),True); cellhi=add(cellhi,mul(D(a[n]),phi,False),False)
        else:
            celllo=add(celllo,mul(D(a[n]),phi,True),True); cellhi=add(cellhi,mul(D(a[n]),plo,False),False)
    Slo=add(Slo,mul(h,celllo,True),True); Shi=add(Shi,mul(h,cellhi,False),False)
print('finite_sum_interval',Slo,Shi)
# n>N tail: for t>=1, sum_{n>N} 2n exp(-cnt) <= 2 exp(-c(N+1)t)*[(N+1)/(1-q)+q/(1-q)^2], q=exp(-c),
# bound q(t) by q(1), and integrate t^2 exp(-c(N+1)t).
q=expi(-c[0],False); one=D(1)
geom=add(div(D(N+1),add(one,-q,True),False),div(q,mul(add(one,-q,True),add(one,-q,True),True),False),False)
ntail=mul(mul(D(2),geom,False),tail_integral_exp2(mul(c[0],D(N+1),True)),False)
# t>T tail: for all 1<=n<=N, e^-cnt <=e^-ct. Integrate from T,
# not from 1, using the slowest permissible rate c (the n=1 term).
ttail=mul(D(N*(N+1)),tail_integral_exp2_from(c[0],D(T)),False)
print('n_tail_bound',ntail)
print('t_tail_bound',ttail)
err=add(ntail,ttail,False)
whole=(add(Slo,-err,True),add(Shi,err,False))
print('integral_interval',whole)
print('completed_L_second_interval', (mul(D(2),whole[0],True),mul(D(2),whole[1],False)))
