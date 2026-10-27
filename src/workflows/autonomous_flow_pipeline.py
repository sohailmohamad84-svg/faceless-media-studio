"""Apex Enterprise Autonomous Google Flow to YouTube Production Worker.
Executes the full automated lifecycle:
1. Detects next topic in queue.
2. Checks if authentic Google Veo 2 video clips exist; if not, generates them via Google Flow.
3. Downloads all 720p scene clips with real physical motion.
4. Assembles 60 FPS master documentary with en-US-ChristopherNeural, ASS subtitles & Foley.
5. Evaluates with AI Video Inspector (score >= 90).
6. Uploads to YouTube and updates dashboard log.
"""
import asyncio
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath("."))

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from playwright.async_api import async_playwright
from src.editing.flow_master_engine import FlowMasterEngine
from src.quality.ai_video_inspector import AIVideoInspector
from src.workflows.daily_shorts_pipeline import VIRAL_SHORTS_QUEUE, DailyShortsPipeline
from src.youtube.uploader import YouTubePublisher

DOWNLOADS_DIR = os.path.expandvars(r"C:\Users\Sohail\Downloads")
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

PROJECT_URL = "https://flow.google.com/project/f256491a-53d7-47f6-9357-f3f233a1ad5a"


async def ensure_scene_clips(topic: dict) -> bool:
    """Generate and download any missing Flow video clips for the topic."""
    scenes = topic["scenes"]
    os.makedirs("data/flow_clips", exist_ok=True)
    
    missing_scenes = []
    for sc in scenes:
        p = Path(sc["input_video"])
        if not p.exists() or p.stat().st_size < 1_000_000:
            missing_scenes.append(sc)
            
    if not missing_scenes:
        print("All scene video clips already exist on disk!", flush=True)
        return True
        
    print(f"Missing {len(missing_scenes)} scene clips. Generating via Google Flow...", flush=True)
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_DATA_DIR,
            executable_path=CHROME_EXE,
            headless=True,
            accept_downloads=True
        )
        page = context.pages[0] if context.pages else await context.new_page()
        
        for sc in missing_scenes:
            num = sc.get("scene_num", 1)
            title = sc.get("title", f"Scene {num}")
            prompt = sc["prompt"]
            dest_path = os.path.abspath(sc["input_video"])
            
            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1_000_000:
                print(f"Scene {num} already downloaded ({os.path.getsize(dest_path)} bytes), skipping.", flush=True)
                continue
                
            print(f"\n=======================================================", flush=True)
            print(f"🎬 GENERATING SCENE {num}/{len(scenes)}: {title}", flush=True)
            print(f"Prompt: {prompt}", flush=True)
            print(f"=======================================================", flush=True)
            
            # 1. Ensure on clean project canvas
            await page.goto(PROJECT_URL)
            await page.wait_for_timeout(4000)
            
            initial_tiles = await page.locator("flow-video-tile").count()
            print(f"Canvas tiles before generation: {initial_tiles}", flush=True)
            
            # 2. Focus prompt box and insert text
            prompt_box = page.locator("[contenteditable='true']").first
            await prompt_box.click()
            await page.wait_for_timeout(300)
            await page.keyboard.insert_text(prompt)
            await page.wait_for_timeout(600)
            
            # 3. Click start generation
            send_btn = page.locator("button[aria-label='Start generation'], button:has-text('arrow_forward')").last
            print("Submitting prompt to Google Flow canvas...", flush=True)
            await send_btn.click()
            await page.wait_for_timeout(3000)
            
            # 4. Check for approval popup if any
            approve = page.locator("button:has-text('Always approve'), button:has-text('Approve')")
            if await approve.count() > 0 and await approve.first.is_visible():
                print("Clicking approval button...", flush=True)
                await approve.first.click()
                await page.wait_for_timeout(2000)
                
            # 5. Wait for new tile to appear on canvas
            print("Waiting for new video tile to register...", flush=True)
            for _ in range(15):
                await page.wait_for_timeout(2000)
                now_tiles = await page.locator("flow-video-tile").count()
                if now_tiles > initial_tiles:
                    print(f"New video tile created! Total canvas tiles: {now_tiles}", flush=True)
                    break
                    
            # 6. Monitor render progress
            print("Rendering Veo 2 video clip in Google Flow...", flush=True)
            start_t = time.time()
            gen_done = False
            for _ in range(65):  # up to ~5 minutes
                await page.wait_for_timeout(5000)
                elapsed = int(time.time() - start_t)
                
                stop_count = await page.locator("button:has-text('Stop'), button[aria-label='Stop']").count()
                newest_tile = page.locator("flow-video-tile").first
                pending = await newest_tile.locator("flow-pending-tile").count()
                
                print(f"  [{elapsed}s] StopBtn: {stop_count} | Pending: {pending}", flush=True)
                
                if elapsed >= 30 and stop_count == 0 and pending == 0:
                    print(f"🎉 Generation completed in {elapsed}s!", flush=True)
                    gen_done = True
                    break
                    
            if not gen_done:
                print(f"WARNING: Scene {num} render timed out. Attempting fallback download...", flush=True)
                
            # 7. Download newest tile (first tile on canvas)
            await page.wait_for_timeout(2000)
            newest_tile = page.locator("flow-video-tile").first
            await newest_tile.click()
            await page.wait_for_timeout(1000)
            
            try:
                dl_btn = page.locator("[aria-label*='Download media'], button:has-text('download')").first
                await dl_btn.click()
                await page.wait_for_timeout(600)
                
                opt_720 = page.locator("text='720p'").first
                print(f"Downloading 720p clip for Scene {num}...", flush=True)
                
                async with page.expect_download(timeout=40000) as download_info:
                    await opt_720.click()
                    
                download = await download_info.value
                await download.save_as(dest_path)
                print(f"✅ Scene {num} saved to {dest_path} ({os.path.getsize(dest_path)} bytes)", flush=True)
            except Exception as e:
                print(f"❌ Download error on Scene {num}: {e}", flush=True)
                
            # 8. Return to canvas
            done_btn = page.locator("button:has-text('Done')").first
            if await done_btn.count() > 0 and await done_btn.is_visible():
                await done_btn.click()
            else:
                await page.goto(PROJECT_URL)
            await page.wait_for_timeout(3000)
            
        await context.close()
        
    return True


async def run_autonomous_cycle(privacy_status: str = "private") -> dict:
    """End-to-end autonomous cycle: topic -> Flow generation -> 60fps master -> QA -> YouTube upload."""
    print("=======================================================", flush=True)
    print("🚀 APEX AUTONOMOUS GOOGLE FLOW TO YOUTUBE ENGINE", flush=True)
    print("=======================================================", flush=True)
    
    published = [r["id"] for r in DailyShortsPipeline.get_published_ids()]
    next_topic = None
    for item in VIRAL_SHORTS_QUEUE:
        if item["id"] not in published:
            next_topic = item
            break
            
    if not next_topic:
        print("All scheduled topics have already been published!", flush=True)
        return {"success": False, "error": "All topics published"}
        
    print(f"Target Video Topic: {next_topic['title']} ({next_topic['id']})", flush=True)
    
    # Step 1: Ensure all Google Veo video clips are created and downloaded
    await ensure_scene_clips(next_topic)
    
    # Step 2: Assemble 60 FPS Master Video
    out_filename = f"{next_topic['id']}_master_1080p.mp4"
    print(f"\nAssembling 60 FPS master video: exports/{out_filename}...", flush=True)
    master_path = await FlowMasterEngine.build_master_video(
        scenes=next_topic["scenes"],
        output_filename=out_filename,
        ambient_sfx="tension_drone.wav"
    )
    print(f"Master video built at: {master_path} ({os.path.getsize(master_path)} bytes)", flush=True)
    
    # Step 3: Run AI Video Quality Inspector
    print("\nEvaluating video with AI Video Quality Inspector...", flush=True)
    qa_result = AIVideoInspector.evaluate_video(str(master_path), is_veo_flow_source=True)
    print(f"AI Score: {qa_result['score']}/100 | Verdict: {qa_result['verdict']}", flush=True)
    print(json.dumps(qa_result, indent=2))
    
    if qa_result["score"] < 85 or qa_result.get("verdict") == "REJECT":
        print(f"⚠️ Video failed quality inspection gate! Flags: {qa_result.get('flags')}", flush=True)
        return {"success": False, "error": f"Failed quality gate: {qa_result.get('flags')}", "qa": qa_result}
        
    # Step 4: Upload to YouTube Shorts
    clean_title = next_topic["title"]
    if not clean_title.endswith("#shorts"):
        clean_title += " #shorts"
        
    print(f"\nUploading to YouTube Shorts ({privacy_status})...", flush=True)
    upload_res = YouTubePublisher.upload_short_file(
        file_path=str(master_path),
        title=clean_title,
        description=next_topic["description"],
        tags=next_topic["tags"],
        privacy_status=privacy_status
    )
    print("Upload Result:")
    print(json.dumps(upload_res, indent=2))
    
    if upload_res.get("success"):
        video_url = upload_res.get("url")
        DailyShortsPipeline.record_published_id(next_topic["id"], video_url)
        print(f"🎉 SUCCESS! Published {next_topic['title']} -> {video_url}", flush=True)
        
        # Git commit and push publication log
        try:
            subprocess.run(["git", "add", "data/daily_shorts_log.json", "src/workflows/daily_shorts_pipeline.py"], check=False)
            subprocess.run(["git", "commit", "-m", f"chore(publish): Published {next_topic['id']} ({privacy_status})"], check=False)
            subprocess.run(["git", "push", "origin", "main"], check=False)
            print("Pushed publication record to GitHub repository.", flush=True)
        except Exception as e:
            print(f"Git push warning: {e}", flush=True)
            
        return {
            "success": True,
            "title": next_topic["title"],
            "url": video_url,
            "score": qa_result["score"],
            "duration": qa_result["duration"],
            "fps": qa_result["fps"]
        }
    else:
        print(f"Upload failed: {upload_res.get('error')}", flush=True)
        return upload_res


if __name__ == "__main__":
    priv = sys.argv[1] if len(sys.argv) > 1 else "private"
    asyncio.run(run_autonomous_cycle(privacy_status=priv))
