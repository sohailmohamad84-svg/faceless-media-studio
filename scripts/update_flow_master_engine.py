import sys
import re

with open("src/editing/flow_master_engine.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace _compute_chunk_timings with _compute_phrase_timings
old_chunk_func = '''    @classmethod
    def _compute_chunk_timings(
        cls,
        words: List[str],
        v_start_sec: float,
        vo_dur: float,
        chunk_sz: int = 3
    ) -> List[Tuple[str, float, float]]:
        """Compute character-weighted subtitle chunk timings for natural reading cadence."""
        if not words or vo_dur <= 0:
            return []
            
        chunks = []
        for ci in range(0, len(words), chunk_sz):
            chunks.append(words[ci:ci + chunk_sz])
            
        chunk_lens = [sum(len(w) for w in c) + len(c) - 1 for c in chunks]
        total_len = max(1, sum(chunk_lens))
        
        timed_chunks = []
        accum_time = v_start_sec
        for idx, c in enumerate(chunks):
            dur_fraction = (chunk_lens[idx] / total_len) * vo_dur
            c_start = accum_time
            c_end = accum_time + dur_fraction
            accum_time = c_end
            timed_chunks.append((" ".join(c).upper(), c_start, c_end))
            
        return timed_chunks'''

new_chunk_func = '''    @classmethod
    def _compute_phrase_timings(
        cls,
        phrases: List[str],
        v_start_sec: float,
        vo_dur: float
    ) -> List[Tuple[str, float, float]]:
        """Compute character-weighted subtitle timings for natural semantic phrases."""
        if not phrases or vo_dur <= 0:
            return []

        clean_lens = []
        for p in phrases:
            clean_text = re.sub(r"\{\\\\[^}]*\}", "", p).strip()
            clean_lens.append(max(1, len(clean_text)))

        total_len = max(1, sum(clean_lens))
        timed_phrases = []
        accum_time = v_start_sec

        for idx, p in enumerate(phrases):
            dur_fraction = (clean_lens[idx] / total_len) * vo_dur
            c_start = accum_time
            c_end = accum_time + dur_fraction
            accum_time = c_end
            timed_phrases.append((p.strip(), c_start, c_end))

        return timed_phrases'''

content = content.replace(old_chunk_func, new_chunk_func)

# 2. Replace the subtitle call in the loop
old_loop_call = '''                # Subtitles with character-weighted timing
                words = text.split()
                timed_chunks = cls._compute_chunk_timings(words, v_start_sec, vo_dur, chunk_sz=3)
                for c_text, w_start, w_end in timed_chunks:
                    c_end_clamped = min(current_time_sec + sc_dur - 0.04, w_end)
                    if c_end_clamped > w_start:
                        ass_events.append(f"Dialogue: 0,{fmt_ass(w_start)},{fmt_ass(c_end_clamped)},FlowSub,,0,0,0,,{c_text}")'''

new_loop_call = '''                # Subtitles with natural grammatical phrase boundaries & selective gold emphasis
                phrases = sc.get("subtitle_phrases")
                if not phrases:
                    words = text.split()
                    chunks = []
                    for ci in range(0, len(words), 4):
                        chunks.append(" ".join(words[ci:ci + 4]))
                    phrases = chunks

                timed_chunks = cls._compute_phrase_timings(phrases, v_start_sec, vo_dur)
                for c_text, w_start, w_end in timed_chunks:
                    c_end_clamped = min(current_time_sec + sc_dur - 0.04, w_end)
                    if c_end_clamped > w_start:
                        ass_events.append(f"Dialogue: 0,{fmt_ass(w_start)},{fmt_ass(c_end_clamped)},FlowSub,,0,0,0,,{c_text}")'''

content = content.replace(old_loop_call, new_loop_call)

# 3. Update style: Arial Black 54pt, White base, 5.0 outline, 2.5 shadow, MarginV 820
old_style = '"Style: FlowSub,Arial Black,58,&H0020FFFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,1.5,0,1,5.0,2.5,2,80,80,820,1",'
new_style = '"Style: FlowSub,Arial Black,54,&H00FFFFFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,1.2,0,1,5.0,2.5,2,80,80,820,1",'
content = content.replace(old_style, new_style)

with open("src/editing/flow_master_engine.py", "w", encoding="utf-8") as f:
    f.write(content)

print("flow_master_engine.py successfully updated!")
