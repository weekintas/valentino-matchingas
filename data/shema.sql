CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT,
    description TEXT,

    csv_path TEXT NOT NULL,
    csv_sha256 TEXT NOT NULL,
    csv_size INTEGER NOT NULL,
    csv_delimiter TEXT NOT NULL,
    csv_multi_delimiter TEXT NOT NULL,

    created_at TEXT NOT NULL
);

CREATE TABLE respondents (
    id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    email TEXT,
    gender TEXT,
    csv_data TEXT,

    PRIMARY KEY (id, project_id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE match_results (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,

    resp1_id INTEGER NOT NULL,
    resp2_id INTEGER NOT NULL,
    score REAL NOT NULL,

    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (resp1_id) REFERENCES respondents(id),
    FOREIGN KEY (resp2_id) REFERENCES respondents(id),

    CHECK (resp1_id < resp2_id)
);

CREATE TABLE generated_files (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    respondent_id INTEGER NOT NULL,

    file_type TEXT CHECK (file_type IN ('RESULTS_PDF', 'RESULTS_EMAIL', 'RESULTS_PNG')) NOT NULL,
    path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,

    created_at TEXT NOT NULL,

    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (respondent_id) REFERENCES respondents(id),
    UNIQUE (sha256)
);

CREATE TABLE emails (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    respondent_id INTEGER NOT NULL,

    email_type TEXT NOT NULL,     -- e.g. 'match_result', 'reminder', 'info'
    status TEXT CHECK (status IN ('SUCCESS', 'FAIL')) NOT NULL,
    status_code TEXT NOT NULL,
    response_json TEXT NOT NULL,

    body_html_path TEXT,
    attachment_paths TEXT,

    sent_at TEXT,

    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (respondent_id) REFERENCES respondents(id)
);
