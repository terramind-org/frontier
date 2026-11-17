//	==============================================================================================
//	kernelwalk: randomised depth-first search for Houston kernels of a target score.
//	Everything above this point is Greg Egan's KernelFinder.c (superpermutators/superperm,
//	commit 1922a34), unchanged; the original exhaustive search() and main() are replaced below.
//
//	Usage: kernelwalk n minScore maxLen nodeBudget restarts seed mode [prefix]
//	  mode 0: any kernel; 1: palindromic1; 2: palindromic2 (as in KernelFinder)
//	  prefix: optional kernel prefix (digits and '-') applied before the random search (mode 0 only)
//	Prints each kernel with score >= minScore, score % (n-2) == 0, ending in a digit, one per line.
//	Move order is a weighted random shuffle favouring long runs (high digits), restarted after
//	nodeBudget search nodes.
//	==============================================================================================

static unsigned long long rngState=88172645463325252ULL;
static unsigned long long rng(void) { rngState^=rngState<<13; rngState^=rngState>>7; rngState^=rngState<<17; return rngState; }
static double rnd01(void) { return (rng()>>11)*(1.0/9007199254740992.0); }

static long long nodes=0, nodeBudget=0;
static int prefixLen=0;

static void emitKernel(void)
{
printKernel(stdout,currentKernel,currentKernelLength);
fflush(stdout);
}

static void rsearch(void)
{
if (nodes++ >= nodeBudget) return;
int pal = palindromic1 || (palindromic2 && currentKernelLength!=0);
int ekl;
if (palindromic1) ekl = 2*currentKernelLength;
else if (palindromic2) ekl = 2*currentKernelLength-1;
else ekl = currentKernelLength;

if (currentKernelLength>prefixLen && currentKernelScore >= minimumScore && currentKernelScore % (kernelN-2) == 0
	&& currentKernel[currentKernelLength-1]>0) emitKernel();
if (ekl>=maxKernelLength) return;
if (currentKernelScore + (maxKernelLength - ekl) < minimumScore) return;

//	Candidate moves: digits 2..n and -1 (weight-4 edge in kernelN terms). Weighted random order.
int moves[16], nm=0;
double keys[16];
for (int d=2;d<=n;d++) moves[nm++]=d;
if (currentKernelLength!=0 && currentKernel[currentKernelLength-1]>0) moves[nm++]=-1;
for (int i=0;i<nm;i++)
	{
	double w = moves[i]==n ? 8.0 : moves[i]==n-1 ? 3.0 : moves[i]==-1 ? 1.0 : 0.5;
	keys[i] = -log(rnd01()+1e-300)/w;	//	exponential race: smaller key = tried earlier
	};
for (int i=1;i<nm;i++) for (int j=i;j>0 && keys[j]<keys[j-1];j--)
	{
	double tk=keys[j]; keys[j]=keys[j-1]; keys[j-1]=tk;
	int tm=moves[j]; moves[j]=moves[j-1]; moves[j-1]=tm;
	};
for (int i=0;i<nm;i++)
	{
	if (nodes >= nodeBudget) return;
	if (addStep(moves[i], pal))
		{
		rsearch();
		removeStep(pal);
		};
	};
}

int main(int argc, const char * argv[])
{
if (argc<8)
	{
	printf("Usage: kernelwalk n minScore maxLen nodeBudget restarts seed mode [prefix]\n");
	exit(EXIT_FAILURE);
	};
kernelN = atoi(argv[1]); n = kernelN-1;
minimumScore = atoi(argv[2]);
maxKernelLength = atoi(argv[3]);
nodeBudget = atoll(argv[4]);
long long restarts = atoll(argv[5]);
rngState ^= (unsigned long long)atoll(argv[6])*0x9E3779B97F4A7C15ULL; if (!rngState) rngState=1;
int mode = atoi(argv[7]);
palindromic1 = mode==1; palindromic2 = mode==2;
const char *prefix = argc>8 ? argv[8] : "";


/*@@ KernelFinder.c setup block (from "//\tSet up permutations, etc." up to "sprintf(outputFile") goes here @@*/

CHECK_MEM( pVisited = (char *)malloc(fn*sizeof(char)) )
CHECK_MEM( currentKernel = (int *)malloc(2*fn*sizeof(int)) )

for (long long r=0;r<restarts;r++)
	{
	for (int i=0;i<fn;i++) pVisited[i]=FALSE;
	currentKernelLength=0;
	currentKernelScore=0;
	currentPerm=0;
	nodes=0;
	prefixLen=0;
	if (palindromic1 || palindromic2) currentPerm2 = w2p[currentPerm];
	if (palindromic2 && (rng()&1))
		{
		currentKernel[0]=-1;
		currentKernelLength=1;
		currentKernelScore=-(kernelN-2);
		currentPerm=0;
		currentPerm2=w3p[currentPerm];
		};
	int ok=TRUE;
	if (mode==0)
		{
		for (const char *c=prefix;*c;c++)
			{
			int d = (*c=='-') ? -1 : (*c-'0');
			if (!addStep(d,FALSE)) { ok=FALSE; break; };
			};
		prefixLen=currentKernelLength;
		};
	if (!ok) { printf("prefix is not a valid kernel\n"); exit(EXIT_FAILURE); };
	rsearch();
	};
return 0;
}
