"""SQLite database connection and schema initialization for Faceless Media Studio."""
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
import config.settings as app_settings

# Thread-local storage for SQLite connections
_local = threading.local()

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    handle TEXT NOT NULL,
    target_niche TEXT NOT NULL,
    editorial_promise TEXT NOT NULL,
    currency TEXT DEFAULT 'INR',
    monthly_budget_ceiling REAL DEFAULT 3000.0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    angle TEXT,
    category_pillar TEXT NOT NULL,
    primary_viewer_question TEXT,
    target_audience TEXT,
    evidence_summary TEXT,
    demand_score REAL DEFAULT 0,
    originality_score REAL DEFAULT 0,
    evergreen_score REAL DEFAULT 0,
    commercial_score REAL DEFAULT 0,
    competition_score REAL DEFAULT 0,
    source_quality_score REAL DEFAULT 0,
    feasibility_score REAL DEFAULT 0,
    total_score REAL DEFAULT 0,
    status TEXT DEFAULT 'backlog',
    why_this_topic TEXT,
    suggested_length_min INTEGER DEFAULT 12,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    publisher TEXT,
    source_type TEXT,
    excerpt TEXT,
    credibility_rating INTEGER DEFAULT 5,
    created_at TEXT NOT NULL,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    version TEXT DEFAULT '1.0',
    title TEXT NOT NULL,
    hook_text TEXT,
    promise_text TEXT,
    body_text TEXT,
    conclusion_text TEXT,
    call_to_action TEXT,
    word_count INTEGER DEFAULT 0,
    target_duration_sec INTEGER DEFAULT 600,
    content_hash TEXT,
    status TEXT DEFAULT 'draft',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS claim_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    script_id INTEGER NOT NULL,
    claim_text TEXT NOT NULL,
    source_url TEXT,
    source_title TEXT,
    verified INTEGER DEFAULT 1,
    notes TEXT,
    timestamp_marker TEXT DEFAULT '00:00',
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS storyboards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    script_id INTEGER NOT NULL,
    scene_order INTEGER NOT NULL,
    scene_title TEXT NOT NULL,
    scene_type TEXT DEFAULT 'context',
    duration_sec REAL DEFAULT 10.0,
    narration_text TEXT NOT NULL,
    visual_prompt TEXT,
    visual_type TEXT DEFAULT 'title_card',
    asset_id INTEGER,
    on_screen_text TEXT,
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    source_url TEXT,
    license_type TEXT NOT NULL,
    commercial_allowed INTEGER DEFAULT 1,
    attribution_required INTEGER DEFAULT 0,
    attribution_text TEXT,
    resolution TEXT DEFAULT '1920x1080',
    file_size_bytes INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS voiceovers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    script_id INTEGER NOT NULL,
    engine TEXT NOT NULL,
    voice_id TEXT NOT NULL,
    audio_path TEXT NOT NULL,
    duration_sec REAL DEFAULT 0,
    sample_rate INTEGER DEFAULT 24000,
    status TEXT DEFAULT 'ready',
    created_at TEXT NOT NULL,
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS render_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    script_id INTEGER NOT NULL,
    output_path TEXT NOT NULL,
    resolution TEXT DEFAULT '1920x1080',
    fps INTEGER DEFAULT 30,
    status TEXT DEFAULT 'queued',
    progress_pct INTEGER DEFAULT 0,
    render_time_sec REAL DEFAULT 0,
    error_message TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS video_exports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    render_job_id INTEGER NOT NULL,
    script_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    thumbnail_path TEXT,
    duration_sec REAL DEFAULT 0,
    resolution TEXT DEFAULT '1920x1080',
    file_size_bytes INTEGER DEFAULT 0,
    content_hash TEXT NOT NULL,
    verified INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (render_job_id) REFERENCES render_jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    script_id INTEGER NOT NULL,
    video_export_id INTEGER NOT NULL,
    content_hash TEXT NOT NULL,
    approved_by TEXT DEFAULT 'Creator',
    approved_at TEXT NOT NULL,
    approval_notes TEXT,
    is_valid INTEGER DEFAULT 1,
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE CASCADE,
    FOREIGN KEY (video_export_id) REFERENCES video_exports(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS youtube_uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_export_id INTEGER NOT NULL,
    youtube_video_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    tags TEXT,
    privacy_status TEXT DEFAULT 'private',
    scheduled_publish_at TEXT,
    uploaded_at TEXT NOT NULL,
    quota_used INTEGER DEFAULT 1600,
    response_json TEXT,
    FOREIGN KEY (video_export_id) REFERENCES video_exports(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS analytics_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    channel_views INTEGER DEFAULT 0,
    watch_time_hours REAL DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    ctr_pct REAL DEFAULT 0,
    avg_view_duration_sec REAL DEFAULT 0,
    avg_pct_viewed REAL DEFAULT 0,
    subscribers_gained INTEGER DEFAULT 0,
    estimated_revenue_usd REAL DEFAULT 0,
    estimated_revenue_inr REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS cost_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    cost_inr REAL DEFAULT 0.0,
    within_budget INTEGER DEFAULT 1,
    notes TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workflow_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_name TEXT NOT NULL,
    status TEXT NOT NULL,
    summary TEXT,
    duration_sec REAL DEFAULT 0.0,
    created_at TEXT NOT NULL
);
"""


def reset_db_connection():
    """Reset the thread-local SQLite connection."""
    if hasattr(_local, "connection") and _local.connection is not None:
        try:
            _local.connection.close()
        except Exception:
            pass
        _local.connection = None


def get_db_connection(db_path: Path = None) -> sqlite3.Connection:
    """Return a thread-local SQLite connection with row factory enabled."""
    target_path = db_path or app_settings.DATABASE_PATH
    if not hasattr(_local, "connection") or _local.connection is None or getattr(_local, "db_path", None) != target_path:
        reset_db_connection()
        conn = sqlite3.connect(str(target_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        _local.connection = conn
        _local.db_path = target_path
    return _local.connection


@contextmanager
def get_db_cursor(db_path: Path = None):
    """Context manager for database transactions with automatic commit/rollback."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def init_db(db_path: Path = None):
    """Initialize database tables and default channel profile."""
    target_path = db_path or app_settings.DATABASE_PATH
    conn = sqlite3.connect(str(target_path))
    conn.executescript(SCHEMA_SQL)
    conn.commit()

    # Seed default channel if not exists
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM channels")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            """
            INSERT INTO channels (name, handle, target_niche, editorial_promise, currency, monthly_budget_ceiling, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """,
            (
                "Apex Enterprise",
                "@ApexEnterprise",
                "Business Case Studies & Corporate Autopsies",
                "We dissect the balance sheets, boardroom blunders, and financial mechanics behind the world's most fascinating businesses.",
                "INR",
                3000.0,
            ),
        )
        conn.commit()
    conn.close()
