-- Proposals schema for the DA (Docente de Aula) flow

CREATE TABLE IF NOT EXISTS proposals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    duration_weeks INTEGER DEFAULT 8,
    tools JSONB DEFAULT '[]',
    curriculum_card JSONB DEFAULT '{}',
    alizia_info JSONB DEFAULT '{}',
    initial_agreements JSONB DEFAULT '[]',
    stages JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS proposal_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    proposal_id INTEGER REFERENCES proposals(id) ON DELETE CASCADE,
    course_subject_id INTEGER REFERENCES course_subjects(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'not_started',
    agreements_data JSONB DEFAULT '{}',
    stages_data JSONB DEFAULT '{}',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, proposal_id, course_subject_id)
);

CREATE INDEX IF NOT EXISTS idx_proposal_progress_user ON proposal_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_proposal_progress_proposal ON proposal_progress(proposal_id);
CREATE INDEX IF NOT EXISTS idx_proposal_progress_course_subject ON proposal_progress(course_subject_id);
