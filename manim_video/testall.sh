#!/bin/bash
cd /home/claude/rashr/manim_video
for s in $(python3 -c "from narration import NARRATION;print(' '.join(NARRATION))"); do
  python -m manim -ql --fps 15 scenes.py $s --media_dir build/media > build/low_$s.log 2>&1 && echo "OK $s" || echo "FAIL $s"
done
