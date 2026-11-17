/* Exact maximum clique in the COMPATIBILITY graph of a set of norm-36 vectors in Z[sqrt2]^11 (edge iff distinct and
 * inner product <= 18, decided exactly in 64-bit integers) = maximum independent set of the conflict graph.
 * Branch and bound with greedy-colouring bounds (Tomita MCQ style) on bitsets.
 * Input (stdin): n lb mode seed time_limit_s, then n lines of 22 ints, then (mode 1) k and k indices of an excluded set.
 *   mode 0: find a clique of size > lb, else prove none exists (status OPTIMAL means the search completed).
 *   mode 1: find a clique of size >= lb that is NOT exactly the excluded set (equal-size move); vertex order is
 *           shuffled by seed. status OPTIMAL with size < lb means no such clique exists.
 * Output: "STATUS <OPTIMAL|TIMEOUT> SIZE <s> NODES <k>" then the indices of the clique found (if any).          */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#define D 11
typedef uint64_t W;
static int n, NW; static W *adj; static long long nodes = 0; static int timed_out = 0; static double tlimit; static clock_t t0;
static int best = 0, *bestset, *cur; static int mode; static W *excl; static int nexcl;
#define ROW(i) (adj + (size_t)(i) * NW)
static int exact_le18(long long a, long long b) {
  long long x = 18 - a, y = -b;
  if (y == 0) return x >= 0;
  if (x >= 0 && y >= 0) return 1;
  if (x <= 0 && y <= 0) return 0;
  if (x > 0) return x * x >= 2 * y * y;
  return 2 * y * y >= x * x;
}
static int popc(const W *s) { int c = 0; for (int i = 0; i < NW; i++) c += __builtin_popcountll(s[i]); return c; }
static int found_done = 0;
static void expand(W *P, int depth) {
  if (found_done || timed_out) return;
  nodes++;
  if ((nodes & 1023) == 0 && (double)(clock() - t0) / CLOCKS_PER_SEC > tlimit) { timed_out = 1; return; }
  int cnt = popc(P);
  if (cnt == 0) {
    if (mode == 0) { if (depth > best) { best = depth; memcpy(bestset, cur, sizeof(int) * depth); found_done = 1; } }
    return;
  }
  /* greedy colouring of P */
  int *order = malloc(sizeof(int) * cnt), *col = malloc(sizeof(int) * cnt);
  W *U = malloc(sizeof(W) * NW), *Q = malloc(sizeof(W) * NW);
  memcpy(U, P, sizeof(W) * NW);
  int k = 0, color = 0;
  while (k < cnt) {
    color++;
    memcpy(Q, U, sizeof(W) * NW);
    for (int w = 0; w < NW; w++) while (Q[w]) {
      int b = __builtin_ctzll(Q[w]); int v = w * 64 + b;
      Q[w] &= Q[w] - 1;
      /* remove neighbours of v from Q (same colour class must be independent) */
      W *r = ROW(v); for (int x = w; x < NW; x++) Q[x] &= ~r[x];
      U[w] &= ~(1ULL << b);
      order[k] = v; col[k] = color; k++;
    }
  }
  W *NP = malloc(sizeof(W) * NW);
  int target = mode == 0 ? best + 1 : best;  /* mode 1: best holds lb */
  for (int i = cnt - 1; i >= 0 && !found_done && !timed_out; i--) {
    if (depth + col[i] < target) break;
    int v = order[i];
    cur[depth] = v;
    W *r = ROW(v);
    for (int x = 0; x < NW; x++) NP[x] = P[x] & r[x];
    if (mode == 1 && depth + 1 >= target) {
      /* any clique of size >= target that differs from the excluded set is accepted */
      int same = (depth + 1 == nexcl);
      if (same) { for (int t = 0; t <= depth; t++) if (!((excl[cur[t] >> 6] >> (cur[t] & 63)) & 1)) { same = 0; break; } }
      if (!same) { best = depth + 1; memcpy(bestset, cur, sizeof(int) * (depth + 1)); found_done = 1; break; }
    }
    if (mode == 0 && depth + 1 > best && popc(NP) == 0) { best = depth + 1; memcpy(bestset, cur, sizeof(int) * (depth + 1)); found_done = 1; break; }
    expand(NP, depth + 1);
    P[v >> 6] &= ~(1ULL << (v & 63));
  }
  free(order); free(col); free(U); free(Q); free(NP);
}
int main(void) {
  int lb, seed;
  if (scanf("%d %d %d %d %lf", &n, &lb, &mode, &seed, &tlimit) != 5) return 2;
  long long (*V)[2 * D] = malloc(sizeof(*V) * n);
  for (int i = 0; i < n; i++) for (int j = 0; j < 2 * D; j++) if (scanf("%lld", &V[i][j]) != 1) return 2;
  NW = (n + 63) / 64;
  /* vertex permutation: mode 1 shuffles for diversity */
  int *perm = malloc(sizeof(int) * n); for (int i = 0; i < n; i++) perm[i] = i;
  srand(seed);
  if (mode == 1) for (int i = n - 1; i > 0; i--) { int j = rand() % (i + 1); int t = perm[i]; perm[i] = perm[j]; perm[j] = t; }
  adj = calloc((size_t)n * NW, sizeof(W));
  long long ne = 0;
  for (int a = 0; a < n; a++) for (int b = a + 1; b < n; b++) {
    long long *u = V[perm[a]], *v = V[perm[b]], x = 0, y = 0;
    for (int k = 0; k < D; k++) { x += u[2*k] * v[2*k] + 2 * u[2*k+1] * v[2*k+1]; y += u[2*k] * v[2*k+1] + u[2*k+1] * v[2*k]; }
    if (exact_le18(x, y)) { ROW(a)[b >> 6] |= 1ULL << (b & 63); ROW(b)[a >> 6] |= 1ULL << (a & 63); ne++; }
  }
  excl = calloc(NW, sizeof(W)); nexcl = 0;
  if (mode == 1) {
    int *inv = malloc(sizeof(int) * n); for (int i = 0; i < n; i++) inv[perm[i]] = i;
    if (scanf("%d", &nexcl) != 1) return 2;
    for (int i = 0; i < nexcl; i++) { int t; if (scanf("%d", &t) != 1) return 2; t = inv[t]; excl[t >> 6] |= 1ULL << (t & 63); }
  }
  bestset = malloc(sizeof(int) * (n + 1)); cur = malloc(sizeof(int) * (n + 1));
  best = lb;
  W *P = malloc(sizeof(W) * NW); memset(P, 0, sizeof(W) * NW); for (int i = 0; i < n; i++) P[i >> 6] |= 1ULL << (i & 63);
  t0 = clock();
  /* mode 0 restarts after each improvement so that the reported size is the proven maximum */
  int found_any = 0, fsz = 0; int *fset = malloc(sizeof(int) * (n + 1));
  for (;;) {
    found_done = 0;
    W *P2 = malloc(sizeof(W) * NW); memcpy(P2, P, sizeof(W) * NW);
    expand(P2, 0); free(P2);
    if (found_done) { found_any = 1; fsz = best; memcpy(fset, bestset, sizeof(int) * best); if (mode == 1) break; continue; }
    break;
  }
  fprintf(stderr, "n %d compat_edges %lld\n", n, ne);
  printf("STATUS %s SIZE %d NODES %lld EDGES %lld\n", timed_out ? "TIMEOUT" : "OPTIMAL", found_any ? fsz : lb, nodes, ne);
  if (found_any) { for (int i = 0; i < fsz; i++) printf("%d ", perm[fset[i]]); }
  printf("\n");
  return 0;
}
