#!/bin/bash
cd /home/claude/rashr/manim_video
python3 -c "from narration import NARRATION;print('\n'.join(NARRATION))" | xargs -P 2 -I{} sh -c 'python -m manim -qh --fps 60 scenes.py {} --media_dir build/media > build/hi_{}.log 2>&1 && echo "OK {}" || echo "FAIL {}"'
echo DONE
