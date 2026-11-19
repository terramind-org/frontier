/* Free-set server. Loads G-orbit representatives with exact conflict lists against the 604 (from orbits.c), the
 * group (group.txt) and its action on the 604 (act604.txt). For each query it lists every pool vector x = g r with
 * C604(x) subset of Rp (the 604 indices counted as removed) and x compatible (exact, dot <= 18) with every extra
 * fixed vector E (vectors of the current configuration that are not in the 604).
 * Query on stdin:  "Q m i1 .. im e" then e lines of 22 ints.  Reply: "N count" then count lines of 22 ints
 * (duplicates removed within each orbit by sorting in the caller), then "END". "X" quits.
 * Usage: freeset <reps file> <group.txt> <act604.txt> [maxconf]                                            */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define D 11
#define NG 24576
static int GP[NG][D], GS[NG][D];
static unsigned short ACT[NG][604]; static unsigned short ACTT[604][NG]; /* transposed for cache-friendly scans */
static int ocls[604]; static unsigned char (*rcls)[8]; /* 604-orbit class of each index; per rep: conflicts per class */
static int *byimg[604][604]; static int nby[604][604];
static long nrep; static signed char (*RP)[2 * D]; static int *ncf; static long *off; static unsigned short *CF;
static int orbsz604[604];
static int exact_le18(long long a, long long b) {
  long long x = 18 - a, y = -b;
  if (y == 0) return x >= 0;
  if (x >= 0 && y >= 0) return 1;
  if (x <= 0 && y <= 0) return 0;
  if (x > 0) return x * x >= 2 * y * y;
  return 2 * y * y >= x * x;
}
int main(int argc, char **argv) {
  int maxconf = argc > 4 ? atoi(argv[4]) : 700;
  FILE *f = fopen(argv[2], "r"); int ng; if (fscanf(f, "%d", &ng) != 1 || ng != NG) return 3;
  for (int g = 0; g < NG; g++) { for (int k = 0; k < D; k++) if (fscanf(f, "%d", &GP[g][k]) != 1) return 3; for (int k = 0; k < D; k++) if (fscanf(f, "%d", &GS[g][k]) != 1) return 3; }
  fclose(f);
  f = fopen(argv[3], "r");
  for (int g = 0; g < NG; g++) for (int i = 0; i < 604; i++) { int t; if (fscanf(f, "%d", &t) != 1) return 3; ACT[g][i] = t; }
  fclose(f);
  for (int g = 0; g < NG; g++) for (int i = 0; i < 604; i++) { nby[i][ACT[g][i]]++; ACTT[i][g] = ACT[g][i]; }
  { int nc2 = 0; for (int i = 0; i < 604; i++) ocls[i] = -1;
    for (int i = 0; i < 604; i++) if (ocls[i] < 0) { for (int g = 0; g < NG; g++) ocls[ACT[g][i]] = nc2; nc2++; }
    fprintf(stderr, "604 splits into %d orbits\n", nc2); }
  for (int i = 0; i < 604; i++) { int c = 0; for (int j = 0; j < 604; j++) { if (nby[i][j]) { byimg[i][j] = malloc(sizeof(int) * nby[i][j]); c++; } } orbsz604[i] = c; }
  static int fill[604][604];
  for (int g = 0; g < NG; g++) for (int i = 0; i < 604; i++) { int j = ACT[g][i]; byimg[i][j][fill[i][j]++] = g; }
  /* load reps */
  f = fopen(argv[1], "r");
  long cap = 1 << 21, ccap = 1 << 26; RP = malloc(cap * sizeof(*RP)); rcls = malloc(cap * 8); ncf = malloc(cap * sizeof(int)); off = malloc(cap * sizeof(long)); CF = malloc(ccap * 2);
  long ctot = 0; nrep = 0;
  for (;;) {
    int t[2 * D], st, nc;
    int ok = 1; for (int j = 0; j < 2 * D; j++) if (fscanf(f, "%d", &t[j]) != 1) { ok = 0; break; }
    if (!ok) break;
    if (fscanf(f, "%d %d", &st, &nc) != 2) return 4;
    if (nrep == cap) { cap *= 2; RP = realloc(RP, cap * sizeof(*RP)); ncf = realloc(ncf, cap * sizeof(int)); off = realloc(off, cap * sizeof(long)); rcls = realloc(rcls, cap * 8); }
    if (ctot + nc > ccap) { ccap *= 2; CF = realloc(CF, ccap * 2); }
    for (int j = 0; j < 2 * D; j++) RP[nrep][j] = t[j];
    off[nrep] = ctot; ncf[nrep] = nc;
    /* store the conflict whose orbit under G is largest first (fewest group elements map it to a given index) */
    int best = -1, bo = -1, tmp[700];
    for (int i = 0; i < nc; i++) { if (fscanf(f, "%d", &tmp[i]) != 1) return 4; if (orbsz604[tmp[i]] > bo) { bo = orbsz604[tmp[i]]; best = i; } }
    int sw = tmp[0]; tmp[0] = tmp[best]; tmp[best] = sw;
    memset(rcls[nrep], 0, 8);
    for (int i = 0; i < nc; i++) { CF[ctot + i] = tmp[i]; if (rcls[nrep][ocls[tmp[i]]] < 255) rcls[nrep][ocls[tmp[i]]]++; }
    ctot += nc; nrep++;
  }
  fclose(f);
  fprintf(stderr, "freeset: %ld reps, %ld conflict entries\n", nrep, ctot);
  printf("READY %ld\n", nrep); fflush(stdout);
  char cmd[8];
  static unsigned char inR[604]; static int Rl[604]; static long long EP[4000][D], EQ[4000][D];
  while (scanf("%7s", cmd) == 1) {
    if (cmd[0] == 'X') break;
    int m, e; if (scanf("%d", &m) != 1) return 5;
    memset(inR, 0, sizeof inR);
    for (int i = 0; i < m; i++) { if (scanf("%d", &Rl[i]) != 1) return 5; inR[Rl[i]] = 1; }
    if (scanf("%d", &e) != 1) return 5;
    for (int i = 0; i < e; i++) for (int k = 0; k < D; k++) if (scanf("%lld %lld", &EP[i][k], &EQ[i][k]) != 2) return 5;
    int Rcls[8] = {0}; for (int i = 0; i < m; i++) Rcls[ocls[Rl[i]]]++;
    /* collect */
    long cnt = 0, capo = 1 << 16; signed char (*out)[2 * D] = malloc(capo * sizeof(*out));
    for (long r = 0; r < nrep; r++) {
      int nc = ncf[r]; if (nc > m || nc > maxconf) continue;
      { int bad = 0; for (int t = 0; t < 8; t++) if (rcls[r][t] > Rcls[t]) { bad = 1; break; } if (bad) continue; } /* g preserves 604-orbits */
      unsigned short *c = CF + off[r];
      int c0 = c[0];
      for (int jj = 0; jj < m; jj++) {
        int j = Rl[jj]; int ng2 = nby[c0][j]; int *gl = byimg[c0][j];
        for (int t = 0; t < ng2; t++) {
          int g = gl[t]; int ok = 1;
          for (int i = 1; i < nc; i++) if (!inR[ACTT[c[i]][g]]) { ok = 0; break; }
          if (!ok) continue;
          signed char x[2 * D];
          for (int k = 0; k < D; k++) { int pk = GP[g][k]; x[2 * pk] = GS[g][k] * RP[r][2 * k]; x[2 * pk + 1] = GS[g][k] * RP[r][2 * k + 1]; }
          for (int w = 0; w < e && ok; w++) {
            long long a = 0, b = 0;
            for (int k = 0; k < D; k++) { a += x[2*k] * EP[w][k] + 2 * x[2*k+1] * EQ[w][k]; b += x[2*k] * EQ[w][k] + x[2*k+1] * EP[w][k]; }
            if (!exact_le18(a, b)) ok = 0;
          }
          if (!ok) continue;
          if (cnt == capo) { capo *= 2; out = realloc(out, capo * sizeof(*out)); }
          memcpy(out[cnt++], x, sizeof x);
        }
      }
    }
    printf("N %ld\n", cnt);
    for (long i = 0; i < cnt; i++) { for (int j = 0; j < 2 * D; j++) printf("%d%c", out[i][j], j == 2 * D - 1 ? '\n' : ' '); }
    printf("END\n"); fflush(stdout);
    free(out);
  }
  return 0;
}
