#!/usr/bin/env bash
# m3_review_batch.sh — M3 全量幻灯片内容审核 (5 并发)
# 用法: bash m3_review_batch.sh <png_dir> <out_dir> [labels_file]
set -u
PNG_DIR="$1"; OUT_DIR="$2"; mkdir -p "$OUT_DIR"
M3=/mnt/project/g00952465/AICO-knowledge/skills/paper-extraction/m3_caption.py
PROMPT='这是一张中文技术汇报幻灯片的渲染截图（GLM 5.3-flash 昇腾 NPU 适配技术分享，受众含技术小白）。请严格审核并只报告你确定的问题：
1) 文字截断/溢出/重叠/乱码方框
2) 图文不符：图注/解读文字与图片实际内容矛盾（重点）
3) 表格或代码块比例失调、内容不可读
4) 布局问题：元素错位、严重大片空白（超过页面 1/3）
5) 内容事实性疑点（数字前后矛盾、术语错误）
输出格式：每条一行「[高/中/低] 位置 — 问题描述」。若无确定问题，只回答「无问题」。不要报告猜测性问题。'

review() {
  local png="$1"
  local base=$(basename "$png" .png)
  [ -s "$OUT_DIR/$base.txt" ] && return 0
  python3 "$M3" "$png" "$PROMPT" > "$OUT_DIR/$base.txt" 2>"$OUT_DIR/$base.err" || echo "CALL_FAILED" > "$OUT_DIR/$base.txt"
}
export -f review; export OUT_DIR M3 PROMPT
ls "$PNG_DIR"/slide-*.png | xargs -P 5 -I{} bash -c 'review "$@"' _ {}
echo "done: $(ls "$OUT_DIR"/*.txt 2>/dev/null | wc -l) reviewed"
grep -l "CALL_FAILED" "$OUT_DIR"/*.txt 2>/dev/null || echo "no failures"
