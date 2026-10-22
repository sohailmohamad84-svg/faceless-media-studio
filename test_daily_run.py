"""Test runner for 1-Click Daily Batch Production."""
from src.workflows.daily_autopilot import DailyAutopilot

print("Starting 1-Click Daily Batch Production (2 Viral Videos)...")
res = DailyAutopilot.produce_daily_two_part_batch()

if res.get("success"):
    print("SUCCESS: 2-Part Viral Series Produced!")
    p1 = res["part1"]
    p2 = res["part2"]
    print(f"Part 1: {p1['title']} | Duration: {p1['duration_sec']}s | File: {p1['mp4_path']}")
    print(f"Part 2: {p2['title']} | Duration: {p2['duration_sec']}s | File: {p2['mp4_path']}")
    print(f"Total production time: {res['total_render_time_sec']}s")
else:
    print("FAILED:", res)
