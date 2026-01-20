-- Test data

-- Coordinators (IDs 1-2)
INSERT INTO users (email, name) VALUES
    ('carlos@test.com', 'Carlos Coordinador'),
    ('maria@test.com', 'María Coordinadora');

-- Teachers (IDs 3-7)
INSERT INTO users (email, name) VALUES
    ('juancito@test.com', 'Juancito Docente'),
    ('laura@test.com', 'Laura Docente'),
    ('pedro@test.com', 'Pedro Docente'),
    ('ana@test.com', 'Ana Docente'),
    ('roberto@test.com', 'Roberto Docente');

INSERT INTO areas (coordinator_id, name, description) VALUES
    (1, 'Ciencias Exactas', 'Ciencias naturales y exactas'),
    (2, 'Humanidades', 'Ciencias sociales y humanidades');

INSERT INTO subjects (area_id, name, description) VALUES
    (1, 'Matemáticas', 'Números, álgebra y cálculo'),
    (1, 'Física', 'Estudio de la materia y energía'),
    (1, 'Biología', 'Estudio de los organismos vivos'),
    (2, 'Historia', 'Estudio de eventos pasados'),
    (2, 'Literatura', 'Estudio de obras escritas');

-- Curso 3a: Miércoles primera hora tiene clase compartida Física + Matemáticas
-- Curso 3b: Miércoles primera hora tiene clase compartida Historia + Literatura (2 individuales + 1 compartida por materia)
-- Curso 5c: Martes primera hora tiene clase compartida Física + Matemáticas
INSERT INTO courses (name, schedule) VALUES
    ('3a', '{"monday": [{"time": "08:00-09:30", "subject": "Matemáticas"}, {"time": "09:45-11:15", "subject": "Física"}], "tuesday": [{"time": "08:00-09:30", "subject": "Biología"}, {"time": "09:45-11:15", "subject": "Matemáticas"}], "wednesday": [{"time": "08:00-09:30", "subject": "Física", "shared_with": "Matemáticas"}, {"time": "09:45-11:15", "subject": "Biología"}], "thursday": [{"time": "08:00-09:30", "subject": "Matemáticas"}, {"time": "09:45-11:15", "subject": "Física"}], "friday": [{"time": "08:00-09:30", "subject": "Biología"}, {"time": "09:45-11:15", "subject": "Matemáticas"}]}'),
    ('3b', '{"monday": [{"time": "08:00-09:30", "subject": "Historia"}, {"time": "09:45-11:15", "subject": "Literatura"}], "tuesday": [{"time": "08:00-09:30", "subject": "Literatura"}, {"time": "09:45-11:15", "subject": "Historia"}], "wednesday": [{"time": "08:00-09:30", "subject": "Historia", "shared_with": "Literatura"}], "thursday": [], "friday": []}'),
    ('5c', '{"monday": [{"time": "08:00-09:30", "subject": "Matemáticas"}, {"time": "09:45-11:15", "subject": "Historia"}], "tuesday": [{"time": "08:00-09:30", "subject": "Física", "shared_with": "Matemáticas"}, {"time": "09:45-11:15", "subject": "Literatura"}], "wednesday": [{"time": "08:00-09:30", "subject": "Biología"}, {"time": "09:45-11:15", "subject": "Matemáticas"}], "thursday": [{"time": "08:00-09:30", "subject": "Historia"}, {"time": "09:45-11:15", "subject": "Física"}], "friday": [{"time": "08:00-09:30", "subject": "Literatura"}, {"time": "09:45-11:15", "subject": "Biología"}]}');

INSERT INTO students (course_id, name) VALUES
    (1, 'Ana García'),
    (1, 'Carlos López'),
    (1, 'María Fernández'),
    (1, 'Juan Martínez'),
    (1, 'Laura Rodríguez'),
    (2, 'Pedro Sánchez'),
    (2, 'Sofia Torres'),
    (2, 'Diego Ramírez'),
    (2, 'Valentina Cruz'),
    (3, 'Mateo Herrera'),
    (3, 'Isabella Morales'),
    (3, 'Lucas Vargas'),
    (3, 'Camila Reyes'),
    (3, 'Sebastián Ortiz');

INSERT INTO problematic_nuclei (name, description) VALUES
    ('Communication and Language', 'Nucleus related to communication skills'),
    ('Logical-Mathematical Thinking', 'Nucleus related to reasoning and mathematics');

INSERT INTO knowledge_areas (nucleus_id, name, description) VALUES
    (1, 'Reading Comprehension', 'Reading and text comprehension skills'),
    (1, 'Written Expression', 'Writing and composition skills'),
    (2, 'Basic Arithmetic', 'Fundamental mathematical operations'),
    (2, 'Geometry', 'Spatial and geometric concepts');

INSERT INTO categories (knowledge_area_id, name, description) VALUES
    (1, 'Narrative Texts', 'Comprehension of stories and tales'),
    (1, 'Informative Texts', 'Comprehension of expository texts'),
    (2, 'Spelling', 'Spelling rules'),
    (2, 'Grammar', 'Sentence structure'),
    (3, 'Addition and Subtraction', 'Basic operations'),
    (3, 'Multiplication', 'Tables and operations'),
    (4, 'Plane Figures', 'Triangles, squares, circles'),
    (4, 'Geometric Solids', 'Cubes, spheres, cylinders');

-- Teacher assignments to courses
-- Teachers: Juancito(3)=Matemáticas, Laura(4)=Física, Pedro(5)=Biología, Ana(6)=Historia, Roberto(7)=Literatura
-- Subjects: Matemáticas(1), Física(2), Biología(3), Historia(4), Literatura(5)
-- Courses: 3a(1), 3b(2), 5c(3)

INSERT INTO course_subjects (course_id, subject_id, teacher_id, start_date, end_date, school_year) VALUES
    -- Course 3a: Matemáticas, Física, Biología
    (1, 1, 3, '2026-03-01', '2026-12-15', 2026),  -- Juancito teaches Matemáticas in 3a
    (1, 2, 4, '2026-03-01', '2026-12-15', 2026),  -- Laura teaches Física in 3a
    (1, 3, 5, '2026-03-01', '2026-12-15', 2026),  -- Pedro teaches Biología in 3a
    -- Course 3b: Historia, Literatura
    (2, 4, 6, '2026-03-01', '2026-12-15', 2026),  -- Ana teaches Historia in 3b
    (2, 5, 7, '2026-03-01', '2026-12-15', 2026),  -- Roberto teaches Literatura in 3b
    -- Course 5c: All subjects (mixed)
    (3, 1, 3, '2026-03-01', '2026-12-15', 2026),  -- Juancito teaches Matemáticas in 5c
    (3, 2, 4, '2026-03-01', '2026-12-15', 2026),  -- Laura teaches Física in 5c
    (3, 3, 5, '2026-03-01', '2026-12-15', 2026),  -- Pedro teaches Biología in 5c
    (3, 4, 6, '2026-03-01', '2026-12-15', 2026),  -- Ana teaches Historia in 5c
    (3, 5, 7, '2026-03-01', '2026-12-15', 2026);  -- Roberto teaches Literatura in 5c

-- Coordination document for Ciencias Exactas (published)
-- Area 1 = Ciencias Exactas, Subjects: Matemáticas(1), Física(2), Biología(3)
-- Nucleus 2 = Logical-Mathematical Thinking
-- Categories: 5=Addition/Subtraction, 6=Multiplication, 7=Plane Figures, 8=Geometric Solids
INSERT INTO coordination_documents (name, area_id, start_date, end_date, status, methodological_strategies, subjects_data, nucleus_ids, category_ids) VALUES
(
    'Planificación Anual - Ciencias Exactas 2026',
    1,
    '2026-03-01',
    '2026-12-15',
    'published',
    'El enfoque pedagógico para el área de Ciencias Exactas se basa en la integración de conceptos matemáticos, físicos y biológicos a través de situaciones problemáticas del mundo real. Se priorizará el desarrollo del pensamiento lógico-matemático mediante actividades que promuevan la experimentación, el análisis de datos y la formulación de hipótesis.

Las metodologías de enseñanza incluirán el aprendizaje basado en problemas, trabajo colaborativo en laboratorio, y el uso de recursos tecnológicos para la visualización de conceptos abstractos. Se fomentará la conexión entre las operaciones aritméticas básicas y su aplicación en contextos científicos.

Los conceptos de geometría se abordarán de manera integrada con física (mediciones, escalas) y biología (formas en la naturaleza, estructuras celulares), permitiendo a los estudiantes comprender la transversalidad del conocimiento matemático en las ciencias naturales.',
    '{
        "1": {
            "class_count": 5,
            "category_ids": [5, 6, 7],
            "class_plan": [
                {"class_number": 1, "title": "Introducción a las operaciones básicas", "objective": "Que los estudiantes comprendan los conceptos fundamentales de suma y resta, identificando su uso en situaciones cotidianas.", "category_ids": [5]},
                {"class_number": 2, "title": "Suma y resta con números naturales", "objective": "Desarrollar habilidades de cálculo mental y escrito para resolver operaciones de suma y resta con números de hasta 3 cifras.", "category_ids": [5]},
                {"class_number": 3, "title": "Introducción a la multiplicación", "objective": "Introducir el concepto de multiplicación como suma repetida y comprender su utilidad práctica.", "category_ids": [6]},
                {"class_number": 4, "title": "Tablas de multiplicar y patrones", "objective": "Memorizar las tablas del 1 al 5 e identificar patrones numéricos en la multiplicación.", "category_ids": [6]},
                {"class_number": 5, "title": "Figuras geométricas en el plano", "objective": "Reconocer y clasificar figuras geométricas planas según sus propiedades (lados, vértices, ángulos).", "category_ids": [7]}
            ]
        },
        "2": {
            "class_count": 4,
            "category_ids": [7, 8],
            "class_plan": [
                {"class_number": 1, "title": "Mediciones y unidades básicas", "objective": "Comprender los sistemas de medición y aplicarlos en experimentos físicos simples.", "category_ids": [7]},
                {"class_number": 2, "title": "Geometría en el mundo físico", "objective": "Relacionar conceptos geométricos con fenómenos físicos observables.", "category_ids": [7]},
                {"class_number": 3, "title": "Volumen y cuerpos geométricos", "objective": "Calcular volúmenes de cuerpos geométricos regulares y relacionarlos con la capacidad.", "category_ids": [8]},
                {"class_number": 4, "title": "Aplicaciones de sólidos geométricos", "objective": "Aplicar conocimientos de sólidos geométricos en problemas de física básica.", "category_ids": [8]}
            ]
        },
        "3": {
            "class_count": 4,
            "category_ids": [5, 7, 8],
            "class_plan": [
                {"class_number": 1, "title": "Conteo y clasificación de organismos", "objective": "Aplicar técnicas de conteo y clasificación para organizar datos biológicos.", "category_ids": [5]},
                {"class_number": 2, "title": "Formas geométricas en la naturaleza", "objective": "Identificar patrones geométricos en estructuras naturales (hojas, flores, cristales).", "category_ids": [7]},
                {"class_number": 3, "title": "Estructuras celulares y formas 3D", "objective": "Relacionar formas tridimensionales con estructuras celulares y moleculares.", "category_ids": [8]},
                {"class_number": 4, "title": "Mediciones en experimentos biológicos", "objective": "Realizar mediciones precisas y registrar datos en experimentos de laboratorio.", "category_ids": [5, 7]}
            ]
        }
    }',
    '{2}',
    '{5, 6, 7, 8}'
);

-- Moment types (tipos de momentos)
INSERT INTO moment_types (name, description) VALUES
    ('Apertura/Motivación', 'Momento inicial de la clase para captar la atención'),
    ('Desarrollo/Construcción/Práctica', 'Momento central de la clase para desarrollar el contenido'),
    ('Cierre/Metacognición', 'Momento final para reflexionar y consolidar aprendizajes');

-- Activities (actividades)
INSERT INTO activities (name, description) VALUES
    ('Expositivas', 'Presentación de contenidos por parte del docente'),
    ('Dialogadas', 'Intercambio de ideas y debate entre docente y estudiantes'),
    ('Experimentales', 'Actividades prácticas y de laboratorio'),
    ('Colaborativas', 'Trabajo en equipo y cooperativo'),
    ('Lúdicas', 'Juegos y actividades recreativas con propósito educativo'),
    ('Investigativas', 'Búsqueda y análisis de información'),
    ('Productivas', 'Creación de productos o proyectos'),
    ('Aprendizaje Basado en Problemas', 'Resolución de problemas reales o simulados'),
    ('Método de casos', 'Análisis de casos de estudio'),
    ('Trabajo por proyectos', 'Desarrollo de proyectos integradores');

-- Coordination document for Humanidades (published)
-- Area 2 = Humanidades, Subjects: Historia(4), Literatura(5)
-- Nucleus 1 = Communication and Language
-- Categories: 1=Narrative Texts, 2=Informative Texts, 3=Spelling, 4=Grammar
INSERT INTO coordination_documents (name, area_id, start_date, end_date, status, methodological_strategies, subjects_data, nucleus_ids, category_ids) VALUES
(
    'Planificación Anual - Humanidades 2026',
    2,
    '2026-03-01',
    '2026-12-15',
    'published',
    'El enfoque pedagógico para el área de Humanidades integra el desarrollo de habilidades de comunicación, comprensión lectora y expresión escrita a través del análisis de textos históricos y literarios. Se fomentará el pensamiento crítico y la capacidad de argumentación mediante el estudio de fuentes primarias y secundarias.

Las metodologías incluirán análisis de textos, debates histórico-literarios, producción escrita creativa y trabajo colaborativo en proyectos de investigación. Se buscará la conexión entre eventos históricos y su representación en la literatura de cada época.',
    '{
        "4": {
            "class_count": 5,
            "category_ids": [1, 2, 3],
            "class_plan": [
                {"class_number": 1, "title": "Introducción a las fuentes históricas", "objective": "Identificar y clasificar diferentes tipos de fuentes históricas.", "category_ids": [2]},
                {"class_number": 2, "title": "Narrativas históricas del siglo XIX", "objective": "Analizar textos narrativos que describen eventos históricos del siglo XIX.", "category_ids": [1]},
                {"class_number": 3, "title": "Documentos y testimonios", "objective": "Interpretar documentos históricos y testimonios escritos.", "category_ids": [2, 3]},
                {"class_number": 4, "title": "Crónicas y relatos de época", "objective": "Comprender la estructura y estilo de las crónicas históricas.", "category_ids": [1]},
                {"class_number": 5, "title": "Redacción de ensayos históricos", "objective": "Producir textos argumentativos sobre temas históricos.", "category_ids": [3]}
            ]
        },
        "5": {
            "class_count": 5,
            "category_ids": [1, 2, 4],
            "class_plan": [
                {"class_number": 1, "title": "Géneros literarios: narrativa", "objective": "Identificar características de los textos narrativos.", "category_ids": [1]},
                {"class_number": 2, "title": "Análisis de cuentos clásicos", "objective": "Analizar estructura y elementos de cuentos tradicionales.", "category_ids": [1]},
                {"class_number": 3, "title": "Textos informativos y reseñas", "objective": "Comprender y producir textos informativos sobre obras literarias.", "category_ids": [2]},
                {"class_number": 4, "title": "Gramática aplicada a la escritura", "objective": "Aplicar reglas gramaticales en la producción de textos literarios.", "category_ids": [4]},
                {"class_number": 5, "title": "Taller de escritura creativa", "objective": "Producir textos narrativos originales aplicando técnicas literarias.", "category_ids": [1, 4]}
            ]
        }
    }',
    '{1}',
    '{1, 2, 3, 4}'
);
