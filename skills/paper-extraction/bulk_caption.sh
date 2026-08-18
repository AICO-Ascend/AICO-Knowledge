#!/usr/bin/env bash
# bulk_caption.sh — 全量精 caption 所有未解读的页级 PNG
# 可恢复：每轮重算 uncaptioned 列表，断了再跑自动续上
# 并行安全：m3_caption.py --save 带 fcntl 文件锁
# 用法: bash skills/paper-extraction/bulk_caption.sh [PARALLELISM]
set -u
cd /mnt/project/g00952465/AICO-knowledge
PAR="${1:-5}"
LOG="extraction/bulk_caption.log"
echo "=== bulk_caption start $(date -u +%FT%TZ) parallelism=$PAR ===" >> "$LOG"

# 重算未 caption 列表到临时文件
compute_uncaptioned() {
  python3 -c "
import json,os
cap=json.load(open('extraction/minimax_captions.json'))
cap_keys=set(k.split('/')[-1] for k in cap)
pngs=sorted(f for f in os.listdir('extraction/assets') if f.endswith('.png'))
for p in pngs:
    if p not in cap_keys: print('extraction/assets/'+p)
" > /tmp/uncaptioned.txt
}

# 单张处理：跑 m3_caption --save；失败重试 1 次
do_one() {
  local img="$1"
  for attempt in 1 2; do
    if python3 skills/paper-extraction/m3_caption.py --save "$img" >/dev/null 2>&1; then
      echo "OK    $img"
      return 0
    fi
    sleep 3
  done
  echo "FAIL  $img" | tee -a extraction/bulk_caption_failures.txt
  return 1
}
export -f do_one

compute_uncaptioned
TOTAL=$(wc -l < /tmp/uncaptioned.txt)
echo "uncaptioned to process: $TOTAL" >> "$LOG"

# 并行跑，-P 限并发
cat /tmp/uncaptioned.txt | xargs -P "$PAR" -I {} bash -c 'do_one "$@"' _ {} \
  | while read line; do
      echo "$(date -u +%H:%M:%S) $line" >> "$LOG"
    done

# 收尾统计
compute_uncaptioned
REMAINING=$(wc -l < /tmp/uncaptioned.txt)
DONE_NOW=$(python3 -c "import json;print(len(json.load(open('extraction/minimax_captions.json'))))")
echo "=== bulk_caption done $(date -u +%FT%TZ) total_captioned=$DONE_NOW remaining=$REMAINING ===" >> "$LOG"
