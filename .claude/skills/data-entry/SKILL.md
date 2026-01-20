---
name: data-entry
description: Expert data entry for the educational planning database. Use this skill to add, modify, or query users, areas, subjects, courses, schedules, coordination documents, and all other database entities.
---

# Data Entry Expert - Educational Planning System

You are an expert data entry operator for this educational planning system. When the user asks to add, modify, or query data, execute the appropriate SQL commands.

## Database Connection

```bash
psql "postgresql://postgres:postgres@localhost:5480/av3"
```

---

## Complete Database Schema

### 1. users
Teachers and coordinators.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Current data:**
| ID | Role | Name |
|----|------|------|
| 1 | Coordinator | Carlos Coordinador |
| 2 | Coordinator | María Coordinadora |
| 3 | Teacher | Juancito Docente |
| 4 | Teacher | Laura Docente |
| 5 | Teacher | Pedro Docente |
| 6 | Teacher | Ana Docente |
| 7 | Teacher | Roberto Docente |

### 2. areas
Subject groupings with a coordinator.

```sql
CREATE TABLE areas (
    id SERIAL PRIMARY KEY,
    coordinator_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Current data:**
| ID | Name | Coordinator |
|----|------|-------------|
| 1 | Ciencias Exactas | Carlos (ID 1) |
| 2 | Humanidades | María (ID 2) |

### 3. subjects
Individual subjects belonging to an area.

```sql
CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    area_id INTEGER NOT NULL REFERENCES areas(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Current data:**
| ID | Area | Name |
|----|------|------|
| 1 | Ciencias Exactas (1) | Matemáticas |
| 2 | Ciencias Exactas (1) | Física |
| 3 | Ciencias Exactas (1) | Biología |
| 4 | Humanidades (2) | Historia |
| 5 | Humanidades (2) | Literatura |

### 4. courses
Student groups (e.g., "3a", "5b") with weekly schedule.

```sql
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    schedule JSONB,  -- Weekly schedule with time slots
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Schedule JSONB format:**
```json
{
  "monday": [
    {"time": "08:00-09:30", "subject": "Matemáticas"},
    {"time": "09:45-11:15", "subject": "Física"}
  ],
  "tuesday": [...],
  "wednesday": [
    {"time": "08:00-09:30", "subject": "Física", "shared_with": "Matemáticas"}
  ],
  "thursday": [...],
  "friday": [...]
}
```

**Shared classes**: Add `"shared_with": "SubjectName"` when two subjects are taught simultaneously.

**Current courses:** 3a (ID 1), 3b (ID 2), 5c (ID 3)

### 5. students
Students enrolled in a course.

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6. course_subjects
Assignment of a teacher to teach a subject in a course.

```sql
CREATE TABLE course_subjects (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id),
    subject_id INTEGER NOT NULL REFERENCES subjects(id),
    teacher_id INTEGER NOT NULL REFERENCES users(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    school_year INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Current assignments:**
| Course | Subject | Teacher |
|--------|---------|---------|
| 3a | Matemáticas | Juancito (3) |
| 3a | Física | Laura (4) |
| 3a | Biología | Pedro (5) |
| 3b | Historia | Ana (6) |
| 3b | Literatura | Roberto (7) |
| 5c | All subjects | Various |

### 7. problematic_nuclei
High-level knowledge themes.

```sql
CREATE TABLE problematic_nuclei (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Current data:**
| ID | Name |
|----|------|
| 1 | Communication and Language |
| 2 | Logical-Mathematical Thinking |

### 8. knowledge_areas
Specific knowledge domains under nuclei.

```sql
CREATE TABLE knowledge_areas (
    id SERIAL PRIMARY KEY,
    nucleus_id INTEGER NOT NULL REFERENCES problematic_nuclei(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Current data:**
| ID | Nucleus | Name |
|----|---------|------|
| 1 | Communication (1) | Reading Comprehension |
| 2 | Communication (1) | Written Expression |
| 3 | Logical-Math (2) | Basic Arithmetic |
| 4 | Logical-Math (2) | Geometry |

### 9. categories
Granular skills/concepts to teach.

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    knowledge_area_id INTEGER NOT NULL REFERENCES knowledge_areas(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Current data:**
| ID | Knowledge Area | Name |
|----|----------------|------|
| 1 | Reading Comprehension (1) | Narrative Texts |
| 2 | Reading Comprehension (1) | Informative Texts |
| 3 | Written Expression (2) | Spelling |
| 4 | Written Expression (2) | Grammar |
| 5 | Basic Arithmetic (3) | Addition and Subtraction |
| 6 | Basic Arithmetic (3) | Multiplication |
| 7 | Geometry (4) | Plane Figures |
| 8 | Geometry (4) | Geometric Solids |

### 10. coordination_documents
Planning documents created by coordinators.

```sql
CREATE TABLE coordination_documents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    area_id INTEGER NOT NULL REFERENCES areas(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',  -- draft, published, archived
    methodological_strategies TEXT,
    subjects_data JSONB,  -- Per-subject planning
    nucleus_ids INTEGER[] DEFAULT '{}',
    category_ids INTEGER[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**subjects_data JSONB format:**
```json
{
  "1": {  // subject_id as key
    "class_count": 5,
    "category_ids": [5, 6, 7],
    "class_plan": [
      {"class_number": 1, "title": "Introduction", "objective": "...", "category_ids": [5]},
      {"class_number": 2, "title": "Deep dive", "objective": "...", "category_ids": [5, 6]}
    ]
  },
  "2": {...}
}
```

### 11. moment_types
Types of class moments (apertura, desarrollo, cierre).

```sql
CREATE TABLE moment_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 12. activities
Didactic activities available for lesson planning.

```sql
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 13. teacher_lesson_plans
Individual lesson plans created by teachers.

```sql
CREATE TABLE teacher_lesson_plans (
    id SERIAL PRIMARY KEY,
    course_subject_id INTEGER NOT NULL REFERENCES course_subjects(id),
    coordination_document_id INTEGER NOT NULL REFERENCES coordination_documents(id),
    class_number INTEGER NOT NULL,
    title VARCHAR(255),
    category_ids INTEGER[] DEFAULT '{}',
    objective TEXT,
    knowledge_content TEXT,
    didactic_strategies TEXT,
    class_format VARCHAR(100),
    moments JSONB,  -- {apertura: {...}, desarrollo: {...}, cierre: {...}}
    status VARCHAR(50) DEFAULT 'pending',  -- pending, planned, completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(course_subject_id, coordination_document_id, class_number)
);
```

---

## Common Operations

### Add a new user (teacher or coordinator)
```sql
INSERT INTO users (email, name) VALUES ('email@test.com', 'Full Name');
```

### Add a new area
```sql
INSERT INTO areas (coordinator_id, name, description)
VALUES (1, 'Area Name', 'Description');
```

### Add a new subject to an area
```sql
INSERT INTO subjects (area_id, name, description)
VALUES (1, 'Subject Name', 'Description');
```

### Add a new course with schedule
```sql
INSERT INTO courses (name, schedule) VALUES (
    '4a',
    '{"monday": [{"time": "08:00-09:30", "subject": "Matemáticas"}], "tuesday": [], "wednesday": [], "thursday": [], "friday": []}'
);
```

### Add a class slot to existing course schedule
```sql
UPDATE courses
SET schedule = jsonb_set(
    schedule,
    '{thursday}',
    (COALESCE(schedule->'thursday', '[]'::jsonb) || '[{"time": "10:00-11:30", "subject": "Biología"}]'::jsonb)
)
WHERE name = '3a';
```

### Add a shared class slot
```sql
UPDATE courses
SET schedule = jsonb_set(
    schedule,
    '{friday}',
    (COALESCE(schedule->'friday', '[]'::jsonb) || '[{"time": "08:00-09:30", "subject": "Historia", "shared_with": "Literatura"}]'::jsonb)
)
WHERE name = '3b';
```

### Add a student to a course
```sql
INSERT INTO students (course_id, name) VALUES (1, 'Student Name');
```

### Assign a teacher to a subject in a course
```sql
INSERT INTO course_subjects (course_id, subject_id, teacher_id, start_date, end_date, school_year)
VALUES (1, 1, 3, '2026-03-01', '2026-12-15', 2026);
```

### Create a coordination document
```sql
INSERT INTO coordination_documents (name, area_id, start_date, end_date, status, nucleus_ids, category_ids)
VALUES ('Document Name', 1, '2026-03-01', '2026-12-15', 'draft', '{2}', '{5,6,7}');
```

### Update document subjects_data
```sql
UPDATE coordination_documents
SET subjects_data = '{"1": {"class_count": 5, "category_ids": [5,6], "class_plan": []}}'::jsonb
WHERE id = 1;
```

### Publish a document
```sql
UPDATE coordination_documents SET status = 'published' WHERE id = 1;
```

### Add a problematic nucleus
```sql
INSERT INTO problematic_nuclei (name, description) VALUES ('Name', 'Description');
```

### Add a knowledge area
```sql
INSERT INTO knowledge_areas (nucleus_id, name, description) VALUES (1, 'Name', 'Description');
```

### Add a category
```sql
INSERT INTO categories (knowledge_area_id, name, description) VALUES (1, 'Name', 'Description');
```

---

## Query Reference Data

### List all users
```sql
SELECT id, name, email FROM users ORDER BY id;
```

### List all areas with coordinators
```sql
SELECT a.id, a.name, u.name as coordinator FROM areas a JOIN users u ON a.coordinator_id = u.id;
```

### List all subjects with their areas
```sql
SELECT s.id, s.name, a.name as area FROM subjects s JOIN areas a ON s.area_id = a.id;
```

### List all courses with their schedules
```sql
SELECT id, name, schedule FROM courses;
```

### List teacher assignments
```sql
SELECT cs.id, c.name as course, s.name as subject, u.name as teacher
FROM course_subjects cs
JOIN courses c ON cs.course_id = c.id
JOIN subjects s ON cs.subject_id = s.id
JOIN users u ON cs.teacher_id = u.id;
```

### List all categories with hierarchy
```sql
SELECT c.id, c.name, ka.name as knowledge_area, pn.name as nucleus
FROM categories c
JOIN knowledge_areas ka ON c.knowledge_area_id = ka.id
JOIN problematic_nuclei pn ON ka.nucleus_id = pn.id;
```

---

## Important Notes

1. **Foreign key constraints**: Always verify that referenced IDs exist before inserting
2. **Schedule format**: Days must be lowercase: monday, tuesday, wednesday, thursday, friday
3. **Shared classes**: Both subjects in a shared class must belong to the same area
4. **subjects_data keys**: Use subject_id as string keys (e.g., "1", "2")
5. **Status values**: coordination_documents use 'draft', 'published', 'archived'
6. **Array syntax**: Use PostgreSQL array syntax `'{1,2,3}'` for integer arrays
