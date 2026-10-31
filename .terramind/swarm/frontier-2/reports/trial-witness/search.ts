const marksCount = 29;
const length = 623;

function score(marks: number[]): number {
  const seen = new Uint8Array(length + 1);
  let duplicates = 0;
  for (let i = 0; i < marks.length; i++) {
    for (let j = 0; j < i; j++) {
      const difference = marks[i] - marks[j];
      duplicates += seen[difference];
      seen[difference] = 1;
    }
  }
  return duplicates;
}

function randomMarks(): number[] {
  const choices = new Set<number>();
  while (choices.size < marksCount - 2) {
    choices.add(1 + Math.floor(Math.random() * (length - 1)));
  }
  return [0, ...choices, length].sort((a, b) => a - b);
}

let best = randomMarks();
let bestScore = score(best);
const started = Date.now();
const deadline = started + 40 * 60 * 1_000;
let restarts = 0;

while (Date.now() < deadline) {
  let current = randomMarks();
  let currentScore = score(current);
  let temperature = 2;
  for (let step = 0; step < 500_000 && Date.now() < deadline; step++) {
    const index = 1 + Math.floor(Math.random() * (marksCount - 2));
    const candidate = current.slice();
    candidate[index] = 1 + Math.floor(Math.random() * (length - 1));
    candidate.sort((a, b) => a - b);
    if (new Set(candidate).size !== marksCount) continue;
    const candidateScore = score(candidate);
    const progress = step / 500_000;
    temperature = 2 * (1 - progress) + 0.02;
    if (
      candidateScore <= currentScore ||
      Math.random() < Math.exp((currentScore - candidateScore) / temperature)
    ) {
      current = candidate;
      currentScore = candidateScore;
    }
    if (currentScore < bestScore) {
      best = current;
      bestScore = currentScore;
      console.error(`best duplicates=${bestScore} restart=${restarts} step=${step}`);
      if (bestScore === 0) {
        console.log(JSON.stringify({ marks: best }));
        process.exit(0);
      }
    }
  }
  restarts++;
}

console.error(`no valid ruler after ${restarts} restarts; best duplicates=${bestScore}`);
console.log(JSON.stringify({ marks: best }));
