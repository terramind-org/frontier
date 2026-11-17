/* Enumerate G-orbit representatives of a pool class of norm-36 vectors and their exact conflict lists with the 604.
 * G (order 24576) is read from group.txt: lines "perm[0..10] sign[0..10]", image y[perm[k]] = sign[k] * x[k].
 * Pool classes (coordinate k = p + q sqrt2; A = coords 0..7, B = coords 8..10):
 *   0 PURE   : every coordinate an integer (|p|<=6) or q*sqrt2 (|q|<=4)
 *   1 PURE+MIXED-B : A coordinates pure; B coordinates any p + q sqrt2 with p^2+2q^2 <= 36
 * Norm 36 exactly: sum p^2 + 2 q^2 = 36 and sum p q = 0.
 * A vector is emitted iff it is the lexicographic minimum of its G-orbit (codes compared coordinate by coordinate).
 * Output line: 22 ints, |Stab|, nconf, conflict indices into baseline.json order (exact test dot > 18).
 * Usage: orbits <class> <F604.txt> <group.txt> > reps.txt                                                 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define D 11
static int NG; static int GP[30000][D], GS[30000][D]; static int NPERM; static int PERM[64][D]; static int PSB[64][D]; /* B signs of one group element with that perm */
static long long FP[604][D], FQ[604][D];
static int nvA, nvB; static int AP[64], AQ[64], BP[200], BQ[200]; static int Arat[64], Brat[200];
static int cp[D], cq[D];
static long long leaves = 0, reps = 0, conf_hist[700];
static int cls;
static int code(int p, int q) { return (p + 6) * 9 + (q + 4); }
static int exact_gt18(long long a, long long b) {
  long long x = 18 - a, y = -b;
  if (y == 0) return x < 0;
  if (x >= 0 && y >= 0) return 0;
  if (x <= 0 && y <= 0) return 1;
  if (x > 0) return !(x * x >= 2 * y * y);
  return !(2 * y * y >= x * x);
}
static void leafv(void) {
  /* G = (48 permutations) x (all 2^8 sign flips of single A coordinates) x (simultaneous flip of B): an image of x,
   * with its A coordinates made nonnegative again, is perm(|a|, eps*sB*b). x (with a >= 0) is the representative iff it
   * is <= every such image. Each permutation comes with a fixed coset of B signs (PSB), taken from a group element. |Stab| = 2^(#zero A coords) * #{(perm, eps): image == x}. */
  leaves++;
  int xc[D]; for (int k = 0; k < D; k++) xc[k] = code(cp[k], cq[k]);
  int fix = 0;
  for (int g = 0; g < NPERM; g++) for (int e = -1; e <= 1; e += 2) {
    int y[D];
    for (int k = 0; k < D; k++) { int t = PERM[g][k]; int sg = k < 8 ? 1 : e * PSB[g][k]; y[t] = code(sg * cp[k], sg * cq[k]); }
    int c = 0;
    for (int k = 0; k < D; k++) if (y[k] != xc[k]) { c = y[k] < xc[k] ? -1 : 1; break; }
    if (c < 0) return;
    if (c == 0) fix++;
  }
  int zA = 0; for (int k = 0; k < 8; k++) if (!cp[k] && !cq[k]) zA++;
  int stab = fix << zA;
  reps++;
  int conf[604], nc = 0;
  for (int w = 0; w < 604; w++) {
    long long a = 0, b = 0;
    for (int k = 0; k < D; k++) { a += cp[k] * FP[w][k] + 2 * cq[k] * FQ[w][k]; b += cp[k] * FQ[w][k] + cq[k] * FP[w][k]; }
    if (exact_gt18(a, b)) conf[nc++] = w;
  }
  conf_hist[nc]++;
  for (int k = 0; k < D; k++) printf("%d %d ", cp[k], cq[k]);
  printf("%d %d", stab, nc);
  for (int i = 0; i < nc; i++) printf(" %d", conf[i]);
  printf("\n");
}
static void rec(int k, int rat, int pq) {
  if (k == D) { if (rat == 36 && pq == 0) leafv(); return; }
  if (k < 8) {
    for (int i = 0; i < nvA; i++) { if (rat + Arat[i] > 36) continue; cp[k] = AP[i]; cq[k] = AQ[i]; rec(k + 1, rat + Arat[i], pq); }
  } else {
    for (int i = 0; i < nvB; i++) { if (rat + Brat[i] > 36) continue; cp[k] = BP[i]; cq[k] = BQ[i]; rec(k + 1, rat + Brat[i], pq + BP[i] * BQ[i]); }
  }
  cp[k] = cq[k] = 0;
}
int main(int argc, char **argv) {
  cls = atoi(argv[1]);
  FILE *f = fopen(argv[2], "r");
  for (int w = 0; w < 604; w++) for (int k = 0; k < D; k++) if (fscanf(f, "%lld %lld", &FP[w][k], &FQ[w][k]) != 2) return 3;
  fclose(f);
  f = fopen(argv[3], "r"); if (fscanf(f, "%d", &NG) != 1) return 3;
  for (int g = 0; g < NG; g++) { for (int k = 0; k < D; k++) if (fscanf(f, "%d", &GP[g][k]) != 1) return 3; for (int k = 0; k < D; k++) if (fscanf(f, "%d", &GS[g][k]) != 1) return 3; }
  fclose(f);
  NPERM = 0;
  for (int g = 0; g < NG; g++) { int seen = 0; for (int h = 0; h < NPERM && !seen; h++) seen = !memcmp(PERM[h], GP[g], sizeof(PERM[h])); if (!seen) { memcpy(PSB[NPERM], GS[g], sizeof(PSB[0])); memcpy(PERM[NPERM++], GP[g], sizeof(PERM[0])); } }
  fprintf(stderr, "perms %d\n", NPERM);
  /* A coordinates: nonnegative only (G contains every sign flip of a single A coordinate), pure */
  nvA = 0;
  for (int p = 0; p <= 6; p++) { AP[nvA] = p; AQ[nvA] = 0; Arat[nvA] = p * p; nvA++; }
  for (int q = 1; q <= 4; q++) { AP[nvA] = 0; AQ[nvA] = q; Arat[nvA] = 2 * q * q; nvA++; }
  nvB = 0;
  for (int p = -6; p <= 6; p++) for (int q = -4; q <= 4; q++) {
    if (p * p + 2 * q * q > 36) continue;
    if (cls == 0 && p && q) continue;
    BP[nvB] = p; BQ[nvB] = q; Brat[nvB] = p * p + 2 * q * q; nvB++;
  }
  rec(0, 0, 0);
  fprintf(stderr, "class %d leaves(A>=0) %lld reps %lld\nconflict-count histogram:", cls, leaves, reps);
  for (int i = 0; i < 700; i++) if (conf_hist[i]) fprintf(stderr, " %d:%lld", i, conf_hist[i]);
  fprintf(stderr, "\n");
  return 0;
}
