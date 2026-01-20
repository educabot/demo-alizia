import os
import json
import copy
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from openai import AzureOpenAI

app = FastAPI(title="Annual Planning API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5480/av3")

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5-mini")

ai_client = AzureOpenAI(
    api_version="2024-02-15-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)


def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


class CoordinationDocumentCreate(BaseModel):
    name: str
    area_id: int
    start_date: str
    end_date: str
    methodological_strategies: Optional[str] = None
    subjects_data: Optional[dict] = None
    nucleus_ids: List[int] = []
    category_ids: List[int] = []


class CoordinationDocumentUpdate(BaseModel):
    name: Optional[str] = None
    methodological_strategies: Optional[str] = None
    subjects_data: Optional[dict] = None
    status: Optional[str] = None


class ChatHistoryItem(BaseModel):
    role: str
    content: str

class ChatMessage(BaseModel):
    history: List[ChatHistoryItem]


class GenerateRequest(BaseModel):
    generate_strategy: bool = True
    generate_class_plans: bool = True


class TeacherLessonPlanCreate(BaseModel):
    course_subject_id: int
    coordination_document_id: int
    class_number: int
    title: Optional[str] = None
    category_ids: List[int] = []
    objective: Optional[str] = None
    knowledge_content: Optional[str] = None
    didactic_strategies: Optional[str] = None
    class_format: Optional[str] = None
    moments: Optional[dict] = None


class TeacherLessonPlanUpdate(BaseModel):
    title: Optional[str] = None
    category_ids: Optional[List[int]] = None
    objective: Optional[str] = None
    knowledge_content: Optional[str] = None
    didactic_strategies: Optional[str] = None
    class_format: Optional[str] = None
    moments: Optional[dict] = None
    status: Optional[str] = None


# Response Models
from datetime import datetime, date as date_type

class RootResponse(BaseModel):
    message: str
    docs: str

class DeleteResponse(BaseModel):
    message: str
    id: int

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

class AreaResponse(BaseModel):
    id: int
    coordinator_id: Optional[int]
    name: str
    description: Optional[str]
    created_at: datetime

class SubjectResponse(BaseModel):
    id: int
    area_id: int
    name: str
    description: Optional[str]
    created_at: datetime

class CourseResponse(BaseModel):
    id: int
    name: str
    schedule: Optional[dict]
    created_at: datetime

class StudentResponse(BaseModel):
    id: int
    course_id: int
    name: str
    created_at: datetime

class CourseSubjectResponse(BaseModel):
    id: int
    course_id: int
    subject_id: int
    teacher_id: int
    start_date: date_type
    end_date: date_type
    school_year: int
    course_name: Optional[str] = None
    subject_name: Optional[str] = None
    teacher_name: Optional[str] = None
    created_at: datetime

class ProblematicNucleusResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

class KnowledgeAreaResponse(BaseModel):
    id: int
    nucleus_id: int
    name: str
    description: Optional[str]
    created_at: datetime

class CategoryResponse(BaseModel):
    id: int
    knowledge_area_id: int
    name: str
    description: Optional[str]
    created_at: datetime

class MomentTypeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

class ActivityResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

class CoordinationDocumentResponse(BaseModel):
    id: int
    name: str
    area_id: int
    start_date: date_type
    end_date: date_type
    status: str
    methodological_strategies: Optional[str]
    subjects_data: Optional[dict]
    nucleus_ids: List[int]
    category_ids: List[int]
    created_at: datetime

class CoordinationDocumentDetailResponse(CoordinationDocumentResponse):
    area: Optional[AreaResponse] = None
    subjects: List[SubjectResponse] = []
    categories: List[CategoryResponse] = []
    nuclei: List[ProblematicNucleusResponse] = []

class TeacherLessonPlanResponse(BaseModel):
    id: int
    course_subject_id: int
    coordination_document_id: int
    class_number: int
    title: Optional[str]
    category_ids: List[int]
    objective: Optional[str]
    knowledge_content: Optional[str]
    didactic_strategies: Optional[str]
    class_format: Optional[str]
    moments: Optional[dict]
    status: str
    created_at: datetime
    updated_at: datetime
    course_name: Optional[str] = None
    subject_name: Optional[str] = None
    document_name: Optional[str] = None
    is_shared_class: Optional[bool] = None
    shared_with_subject: Optional[str] = None
    is_own_plan: Optional[bool] = None
    created_by_teacher: Optional[str] = None
    created_by_subject: Optional[str] = None

class TeacherLessonPlanDetailResponse(TeacherLessonPlanResponse):
    moment_types: List[MomentTypeResponse] = []
    activities: List[ActivityResponse] = []
    categories: List[CategoryResponse] = []

class SharedClassSlot(BaseModel):
    day: str
    time: str
    subject: str
    shared_with: str

class SharedClassesResponse(BaseModel):
    course_id: int
    area_id: int
    shared_classes: List[SharedClassSlot]

class SharedClassNumbersResponse(BaseModel):
    shared_class_numbers: List[int]
    shared_class_info: dict

class ClassPlanItem(BaseModel):
    class_number: int
    title: str
    objective: Optional[str] = None
    category_ids: List[int] = []

class CoordinationStatusResponse(BaseModel):
    has_published_document: bool
    document_id: Optional[int]
    document_name: Optional[str]
    coordinator_name: Optional[str]
    class_plan: List[ClassPlanItem]
    subject_category_ids: List[int]
    category_ids: List[int]
    nucleus_ids: List[int]

class ChatResponse(BaseModel):
    response: str
    document: Optional[CoordinationDocumentResponse] = None

class TeacherChatResponse(BaseModel):
    response: str
    plan: Optional[TeacherLessonPlanResponse] = None
    changes_made: List[str] = []

class GenerateMomentResponse(BaseModel):
    moment_type: str
    generated_content: str
    plan: TeacherLessonPlanResponse


# AI Helper Functions
def generate_methodological_strategies(area_name: str, subjects: list, categories: list, nuclei: list) -> str:
    subject_names = [s["name"] for s in subjects]
    category_names = [c["name"] for c in categories]
    nucleus_names = [n["name"] for n in nuclei]

    prompt = f"""Eres un experto en planificación educativa. Genera una estrategia metodológica para el área de {area_name}.

Materias involucradas: {', '.join(subject_names)}
Núcleos problemáticos: {', '.join(nucleus_names)}
Categorías/conceptos a enseñar: {', '.join(category_names)}

Escribe una estrategia metodológica de 2-3 párrafos que explique:
1. El enfoque pedagógico general para integrar estas materias
2. Las metodologías de enseñanza recomendadas
3. Cómo se relacionan los conceptos entre las diferentes materias

Responde solo con la estrategia, sin títulos ni encabezados."""

    try:
        response = ai_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=16000
        )
        content = response.choices[0].message.content
        print(f"[AI] Generated strategy: {content[:100] if content else 'EMPTY'}...")
        return content or ""
    except Exception as e:
        print(f"[AI] Error generating strategy: {type(e).__name__}: {e}")
        raise


def generate_class_plans(subjects_data: dict, subjects: list, categories: list) -> dict:
    category_map = {c["id"]: c["name"] for c in categories}
    subject_map = {s["id"]: s["name"] for s in subjects}

    updated_subjects_data = {}

    for subject_id, data in subjects_data.items():
        subject_name = subject_map.get(int(subject_id), f"Materia {subject_id}")
        class_count = data.get("class_count", 10)
        subject_category_ids = data.get("category_ids", [])
        subject_category_names = [category_map.get(cid, f"Cat {cid}") for cid in subject_category_ids]

        prompt = f"""Genera un plan de clases para la materia {subject_name}.
Total de clases: {class_count}
Categorías/conceptos a cubrir: {', '.join(subject_category_names)}

Para cada clase, genera:
- Un título breve y descriptivo
- Los IDs de categorías que se trabajan en esa clase (de la lista: {subject_category_ids})

Responde en formato JSON como un array de objetos con esta estructura:
[{{"class_number": 1, "title": "Título de la clase", "category_ids": [1, 2]}}]

Solo responde con el JSON, sin explicaciones adicionales."""

        try:
            response = ai_client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=16000
            )
            content = response.choices[0].message.content
            # Parse JSON from response
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            class_plan = json.loads(content)
        except Exception as e:
            # Fallback: generate basic plan without AI
            class_plan = []
            cats_per_class = max(1, len(subject_category_ids) // class_count) if subject_category_ids else 0
            for i in range(class_count):
                start_idx = (i * cats_per_class) % len(subject_category_ids) if subject_category_ids else 0
                end_idx = start_idx + cats_per_class
                class_cats = subject_category_ids[start_idx:end_idx] if subject_category_ids else []
                class_plan.append({
                    "class_number": i + 1,
                    "title": f"Clase {i + 1}",
                    "category_ids": class_cats
                })

        updated_subjects_data[subject_id] = {
            **data,
            "class_plan": class_plan
        }

    return updated_subjects_data


def generate_lesson_moment_content(
    moment_type: str,
    subject_name: str,
    class_title: str,
    objective: str,
    activity_names: list,
    custom_text: str = ""
) -> str:
    """Generate content for a lesson moment (apertura, desarrollo, cierre) using AI."""

    moment_descriptions = {
        "apertura": "Apertura/Motivación - el momento inicial de la clase para captar la atención y motivar a los estudiantes",
        "desarrollo": "Desarrollo/Construcción - el momento central de la clase donde se desarrolla el contenido principal",
        "cierre": "Cierre/Metacognición - el momento final para reflexionar, consolidar aprendizajes y evaluar comprensión"
    }

    moment_desc = moment_descriptions.get(moment_type, moment_type)
    activities_str = ", ".join(activity_names) if activity_names else "actividades variadas"

    prompt = f"""Eres un experto en planificación educativa. Genera una descripción para el momento de {moment_desc} de una clase.

Materia: {subject_name}
Tema de la clase: {class_title}
Objetivo: {objective}
Estrategias/Actividades seleccionadas: {activities_str}
{f'Notas adicionales del docente: {custom_text}' if custom_text else ''}

IMPORTANTE - Estilo de redacción:
- Escribe en tercera persona del singular, presente indicativo, como documento de planificación formal
- Usa frases como: "Se inicia la clase...", "El docente presenta...", "Se propone a los estudiantes...", "Se cierra la actividad..."
- NO uses imperativo (no digas "presente", "haga", "pida")
- NO uses primera persona (no digas "presento", "hago")

Ejemplo del estilo correcto:
"Al iniciar la clase se capta la atención de los estudiantes presentando una situación problemática real. El docente plantea preguntas orientadoras que conectan el tema con experiencias cotidianas. Se promueve la participación mediante una lluvia de ideas..."

Escribe 2-3 párrafos describiendo qué sucede en este momento de la clase, aplicando las estrategias seleccionadas. No uses encabezados ni listas numeradas."""

    try:
        response = ai_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=16000
        )
        content = response.choices[0].message.content
        print(f"[AI] Generated {moment_type} content: {content[:100] if content else 'EMPTY'}...")
        return content or ""
    except Exception as e:
        print(f"[AI] Error generating {moment_type} content: {type(e).__name__}: {e}")
        return f"Error al generar contenido. Por favor, usa el chat con Alizia para generar el contenido de {moment_type}."


# Chat function calling tools
CHAT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "update_document_title",
            "description": "Actualiza el título del documento de coordinación",
            "parameters": {
                "type": "object",
                "properties": {
                    "new_title": {
                        "type": "string",
                        "description": "El nuevo título para el documento"
                    }
                },
                "required": ["new_title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_methodological_strategy",
            "description": "REEMPLAZA COMPLETAMENTE la estrategia metodológica del documento. Solo usar si el usuario quiere cambiar TODO el texto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "new_strategy": {
                        "type": "string",
                        "description": "La nueva estrategia metodológica completa"
                    }
                },
                "required": ["new_strategy"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "append_to_methodological_strategy",
            "description": "AGREGA texto al final de la estrategia metodológica existente. Usar cuando el usuario quiere añadir algo sin borrar lo existente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text_to_append": {
                        "type": "string",
                        "description": "El texto a agregar al final de la estrategia existente"
                    }
                },
                "required": ["text_to_append"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_class_title",
            "description": "Actualiza el título de una clase específica de una materia",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject_id": {
                        "type": "integer",
                        "description": "ID de la materia"
                    },
                    "class_number": {
                        "type": "integer",
                        "description": "Número de la clase (1-indexed)"
                    },
                    "new_title": {
                        "type": "string",
                        "description": "El nuevo título para la clase"
                    }
                },
                "required": ["subject_id", "class_number", "new_title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_class_categories",
            "description": "Actualiza las categorías asignadas a una clase específica",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject_id": {
                        "type": "integer",
                        "description": "ID de la materia"
                    },
                    "class_number": {
                        "type": "integer",
                        "description": "Número de la clase (1-indexed)"
                    },
                    "category_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Lista de IDs de categorías para asignar a la clase"
                    }
                },
                "required": ["subject_id", "class_number", "category_ids"]
            }
        }
    }
]


# Proposal chat tools for agreements and decisions
PROPOSAL_CHAT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "set_agreement_value",
            "description": "Establece el valor/decisión para un acuerdo. Usar cuando el docente ha tomado una decisión clara.",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "El valor o decisión tomada por el docente"
                    }
                },
                "required": ["value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_agreement_complete",
            "description": "Marca el acuerdo como completado. Solo usar cuando el docente ha confirmado su decisión final.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Resumen breve de la decisión tomada"
                    }
                },
                "required": ["summary"]
            }
        }
    }
]


def get_proposal_chat_system_prompt(
    agreement_title: str,
    agreement_description: str,
    responsible_type: str,
    proposal_name: str,
    existing_value: str = None
) -> str:
    """Generate system prompt based on responsible type."""

    base_context = f"""Eres Alizia, una Docente Referente (DR) de tecnología educativa que ayuda a docentes de aula (DA) a implementar proyectos de pensamiento computacional.

Proyecto actual: {proposal_name}
Acuerdo en discusión: {agreement_title}
Descripción: {agreement_description}
"""

    if existing_value:
        base_context += f"\nValor actual del acuerdo: {existing_value}\n"

    if responsible_type == "da_solo":
        tone = """
TONO: Sugerente y orientador
- El DA tiene la decisión final sobre este acuerdo
- Tu rol es ofrecer sugerencias, hacer preguntas que ayuden a reflexionar, y validar las decisiones del DA
- NO impongas tu criterio, pero sí puedes ofrecer alternativas o señalar consideraciones importantes
- Cuando el DA exprese una decisión clara, usa set_agreement_value para registrarla
- Cuando el DA confirme que está satisfecho con su decisión, usa mark_agreement_complete
"""
    else:  # conjunto
        tone = """
TONO: Firme y co-decisor
- Este es un acuerdo CONJUNTO donde tú (Alizia/DR) participas activamente en la decisión
- Puedes y DEBES expresar tu opinión fundamentada
- Puedes proponer alternativas y negociar hasta llegar a un acuerdo mutuo
- No aceptes decisiones que consideres pedagógicamente inadecuadas sin discutirlas primero
- Cuando lleguen a un acuerdo conjunto, usa set_agreement_value para registrarlo
- Cuando ambos estén de acuerdo, usa mark_agreement_complete
"""

    return base_context + tone + """

IMPORTANTE:
- Responde siempre en español, de manera cálida pero profesional
- Mantén las respuestas concisas (2-3 párrafos máximo)
- Haz preguntas clarificadoras cuando sea necesario
- Celebra las buenas decisiones del docente
"""


def process_proposal_chat(
    agreement_title: str,
    agreement_description: str,
    responsible_type: str,
    proposal_name: str,
    history: list,
    existing_value: str = None
) -> dict:
    """Process chat messages for proposal agreements."""

    system_prompt = get_proposal_chat_system_prompt(
        agreement_title, agreement_description, responsible_type, proposal_name, existing_value
    )

    messages = [{"role": "system", "content": system_prompt}]
    for item in history:
        messages.append({"role": item["role"], "content": item["content"]})

    response = ai_client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=messages,
        tools=PROPOSAL_CHAT_TOOLS,
        tool_choice="auto",
        max_completion_tokens=16000
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    result = {
        "response": response_message.content or "",
        "agreement_completed": False,
        "decision_value": None
    }

    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"[ProposalChat] Function: {function_name}, Args: {args}")

            if function_name == "set_agreement_value":
                result["decision_value"] = args["value"]
                if not result["response"]:
                    result["response"] = f"He registrado tu decisión: {args['value']}"

            elif function_name == "mark_agreement_complete":
                result["agreement_completed"] = True
                if not result["response"]:
                    result["response"] = f"Excelente, hemos acordado: {args['summary']}. Este acuerdo queda completado."

    return result


# Teacher lesson plan chat tools
TEACHER_LESSON_CHAT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "update_moment_content",
            "description": "Actualiza el contenido de un momento de la clase (apertura, desarrollo o cierre)",
            "parameters": {
                "type": "object",
                "properties": {
                    "moment_type": {
                        "type": "string",
                        "enum": ["apertura", "desarrollo", "cierre"],
                        "description": "El momento a actualizar"
                    },
                    "new_content": {
                        "type": "string",
                        "description": "El nuevo contenido para el momento. Debe estar escrito en tercera persona, presente indicativo (ej: 'Se inicia la clase...', 'El docente presenta...')"
                    }
                },
                "required": ["moment_type", "new_content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_objective",
            "description": "Actualiza el objetivo de la clase",
            "parameters": {
                "type": "object",
                "properties": {
                    "new_objective": {
                        "type": "string",
                        "description": "El nuevo objetivo de la clase"
                    }
                },
                "required": ["new_objective"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_title",
            "description": "Actualiza el título de la clase",
            "parameters": {
                "type": "object",
                "properties": {
                    "new_title": {
                        "type": "string",
                        "description": "El nuevo título de la clase"
                    }
                },
                "required": ["new_title"]
            }
        }
    }
]


def process_teacher_lesson_chat(plan: dict, history: list, activities: list) -> dict:
    """Process chat messages for teacher lesson plan editing."""
    activity_map = {a["id"]: a["name"] for a in activities}
    moments = plan.get("moments") or {}

    # Build info about current moments
    moments_info = []
    for moment_type in ["apertura", "desarrollo", "cierre"]:
        moment_data = moments.get(moment_type, {})
        content = moment_data.get("generatedContent", "Sin contenido")
        activity_ids = moment_data.get("activities", [])
        activity_names = [activity_map.get(aid, f"Actividad {aid}") for aid in activity_ids]
        moments_info.append(f"- {moment_type.capitalize()}: Estrategias: {', '.join(activity_names) or 'ninguna'}. Contenido: {content[:200]}...")

    system_prompt = f"""Eres Alizia, una asistente de IA para planificación de clases. Ayudas a los docentes a mejorar sus planes de clase.

Plan de clase actual:
- Título: {plan.get('title', 'Sin título')}
- Materia: {plan.get('subject_name', 'Desconocida')}
- Objetivo: {plan.get('objective', 'Sin objetivo')}

Momentos de la clase:
{chr(10).join(moments_info)}

IMPORTANTE sobre el estilo de redacción:
- El contenido debe estar en TERCERA PERSONA, PRESENTE INDICATIVO
- Usa frases como: "Se inicia la clase...", "El docente presenta...", "Se propone a los estudiantes...", "Se cierra la actividad..."
- NO uses imperativo (no digas "presente", "haga", "pida")
- NO uses primera persona (no digas "presento", "hago")

Cuando el usuario pida cambios, usa las funciones disponibles para modificar el plan.
Responde siempre en español de manera amigable y concisa."""

    messages = [{"role": "system", "content": system_prompt}]
    for item in history:
        messages.append({"role": item["role"], "content": item["content"]})

    response = ai_client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=messages,
        tools=TEACHER_LESSON_CHAT_TOOLS,
        tool_choice="auto",
        max_completion_tokens=16000
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    updates = {}
    changes_made = []

    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"[TeacherChat] Function: {function_name}, Args: {args}")

            if function_name == "update_moment_content":
                moment_type = args["moment_type"]
                new_content = args["new_content"]
                if "moments" not in updates:
                    # Deep copy to preserve all nested data
                    updates["moments"] = copy.deepcopy(moments)
                if moment_type not in updates["moments"]:
                    updates["moments"][moment_type] = moments.get(moment_type, {}).copy()
                updates["moments"][moment_type]["generatedContent"] = new_content
                changes_made.append(f"contenido de {moment_type} actualizado")

            elif function_name == "update_objective":
                updates["objective"] = args["new_objective"]
                changes_made.append("objetivo actualizado")

            elif function_name == "update_title":
                updates["title"] = args["new_title"]
                changes_made.append("título actualizado")

    response_text = response_message.content or ""
    if changes_made and not response_text:
        response_text = f"¡Listo! He realizado los siguientes cambios: {', '.join(changes_made)}."

    return {
        "response": response_text,
        "updates": updates,
        "changes_made": changes_made
    }


def process_chat_message(doc: dict, history: list, subjects: list, categories: list) -> dict:
    category_map = {c["id"]: c["name"] for c in categories}
    subject_map = {s["id"]: s["name"] for s in subjects}
    # Also create a name-to-id map for subjects
    subject_name_to_id = {s["name"].lower(): s["id"] for s in subjects}

    subjects_data = doc.get("subjects_data") or {}
    subjects_info = []
    for sid, sdata in subjects_data.items():
        sname = subject_map.get(int(sid), f"Materia {sid}")
        class_plan = sdata.get("class_plan", [])
        classes_info = [f"Clase {c['class_number']}: {c.get('title', 'Sin título')}" for c in class_plan[:5]]
        subjects_info.append(f"- {sname} (ID: {sid}): {len(class_plan)} clases. Primeras: {', '.join(classes_info)}")

    current_strategy = doc.get('methodological_strategies', '') or 'No generada aún'

    system_prompt = f"""Eres Alizia, una asistente de IA para planificación educativa. Ayudas a modificar documentos de coordinación.

Documento actual:
- Título: {doc['name']}
- Estrategia metodológica COMPLETA (NO la modifiques a menos que te lo pidan explícitamente):
\"\"\"
{current_strategy}
\"\"\"

Materias y sus clases (USA ESTOS IDs EXACTOS):
{chr(10).join(subjects_info)}

Categorías disponibles:
{', '.join([f"{c['name']} (ID: {c['id']})" for c in categories[:20]])}

IMPORTANTE:
- Cuando modifiques una clase, usa el ID de la materia que aparece entre paréntesis arriba.
- Si el usuario pide AGREGAR algo al final de la estrategia, usa append_to_methodological_strategy (NO reemplaces todo).
- Si el usuario pide REEMPLAZAR o CAMBIAR completamente la estrategia, usa update_methodological_strategy.
- Cuando el usuario pida modificar algo, usa las funciones disponibles para hacer los cambios.
- Si no hay una función para lo que pide, explica qué puedes hacer.
Responde siempre en español de manera amigable y concisa."""

    # Build messages array from history
    messages = [{"role": "system", "content": system_prompt}]
    for item in history:
        messages.append({"role": item["role"], "content": item["content"]})

    response = ai_client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=messages,
        tools=CHAT_TOOLS,
        tool_choice="auto",
        max_completion_tokens=16000
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    updates = {}
    changes_made = []

    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"[Chat] Function: {function_name}, Args: {args}")  # Debug log

            if function_name == "update_document_title":
                updates["name"] = args["new_title"]
                changes_made.append(f"título cambiado a '{args['new_title']}'")

            elif function_name == "update_methodological_strategy":
                updates["methodological_strategies"] = args["new_strategy"]
                changes_made.append("estrategia metodológica actualizada")

            elif function_name == "append_to_methodological_strategy":
                current = doc.get('methodological_strategies', '') or ''
                new_text = args["text_to_append"]
                updates["methodological_strategies"] = current.rstrip() + " " + new_text
                changes_made.append("texto agregado al final de la estrategia metodológica")

            elif function_name == "update_class_title":
                sid = str(args["subject_id"])
                class_num = args["class_number"]
                new_title = args["new_title"]
                found = False

                # Try to find the subject in subjects_data
                for key in subjects_data.keys():
                    if str(key) == sid:
                        if "class_plan" in subjects_data[key]:
                            for c in subjects_data[key]["class_plan"]:
                                if c["class_number"] == class_num:
                                    c["title"] = new_title
                                    found = True
                                    break
                        if found:
                            updates["subjects_data"] = subjects_data
                            subject_name = subject_map.get(int(key), f"Materia {key}")
                            changes_made.append(f"título de clase {class_num} de {subject_name} cambiado a '{new_title}'")
                            break

                if not found:
                    print(f"[Chat] Could not find subject {sid} or class {class_num}. Available keys: {list(subjects_data.keys())}")

            elif function_name == "update_class_categories":
                sid = str(args["subject_id"])
                class_num = args["class_number"]
                new_cats = args["category_ids"]
                found = False

                for key in subjects_data.keys():
                    if str(key) == sid:
                        if "class_plan" in subjects_data[key]:
                            for c in subjects_data[key]["class_plan"]:
                                if c["class_number"] == class_num:
                                    c["category_ids"] = new_cats
                                    found = True
                                    break
                        if found:
                            updates["subjects_data"] = subjects_data
                            subject_name = subject_map.get(int(key), f"Materia {key}")
                            changes_made.append(f"categorías de clase {class_num} de {subject_name} actualizadas")
                            break

    # Build response based on what actually happened
    if changes_made:
        assistant_response = f"Listo! He realizado los siguientes cambios: {', '.join(changes_made)}."
    elif response_message.content:
        assistant_response = response_message.content
    else:
        assistant_response = "No pude realizar los cambios solicitados. Por favor, verifica el nombre de la materia y el número de clase."

    return {
        "response": assistant_response,
        "updates": updates
    }


# Shared classes helper function
def get_shared_classes_for_area(course_schedule: dict, area_subject_names: list) -> list:
    """
    Detects slots with shared_with where both subjects belong to the area.
    Returns: [{ day, time, subject, shared_with }]
    """
    shared_classes = []
    if not course_schedule:
        return shared_classes

    for day, slots in course_schedule.items():
        if not isinstance(slots, list):
            continue
        for slot in slots:
            if not isinstance(slot, dict):
                continue
            subject = slot.get("subject")
            shared_with = slot.get("shared_with")
            time = slot.get("time")

            # Check if this is a shared class and both subjects are in the area
            if shared_with and subject in area_subject_names and shared_with in area_subject_names:
                shared_classes.append({
                    "day": day,
                    "time": time,
                    "subject": subject,
                    "shared_with": shared_with
                })

    return shared_classes


def calculate_shared_class_numbers(course_schedule: dict, subject_name: str,
                                    area_subject_names: list, total_classes: int) -> dict:
    """
    Calcula qué números de clase caen en horarios compartidos y con qué materia.

    Args:
        course_schedule: Schedule del curso
        subject_name: Nombre de la materia
        area_subject_names: Lista de materias del área
        total_classes: Total de clases planificadas para la materia

    Returns:
        Dict mapping class numbers to shared subject name: {3: "Física", 8: "Física", ...}
    """
    if not course_schedule or total_classes <= 0:
        return {}

    days_order = ["monday", "tuesday", "wednesday", "thursday", "friday"]

    # First pass: find weekly pattern
    weekly_class_count = 0
    shared_positions = []  # (position, shared_with_subject_name)

    for day in days_order:
        slots = course_schedule.get(day, [])
        if not isinstance(slots, list):
            continue

        for slot in slots:
            if not isinstance(slot, dict):
                continue

            slot_subject = slot.get("subject")
            slot_shared_with = slot.get("shared_with")

            # Check if this subject appears in this slot
            is_subject_direct = slot_subject == subject_name
            is_subject_shared = slot_shared_with == subject_name

            if is_subject_direct or is_subject_shared:
                # Check if this is a shared class with another area subject
                shared_with_name = None
                if is_subject_direct and slot_shared_with and slot_shared_with in area_subject_names:
                    shared_with_name = slot_shared_with
                elif is_subject_shared and slot_subject in area_subject_names:
                    shared_with_name = slot_subject

                if shared_with_name:
                    shared_positions.append((weekly_class_count, shared_with_name))

                weekly_class_count += 1

    if weekly_class_count == 0:
        return {}

    # Generate all shared class numbers up to total_classes
    shared_class_info = {}
    for pos, shared_with_name in shared_positions:
        class_num = pos + 1  # 1-indexed
        while class_num <= total_classes:
            shared_class_info[class_num] = shared_with_name
            class_num += weekly_class_count

    return shared_class_info


def find_partner_course_subject_id(cur, course_subject_id: int, shared_class_info: dict, class_number: int) -> int | None:
    """
    Encuentra el course_subject_id del profesor compañero para una clase compartida.

    Args:
        cur: Database cursor
        course_subject_id: Current teacher's course_subject_id
        shared_class_info: Dict from calculate_shared_class_numbers {class_num: partner_subject_name}
        class_number: The class number to check

    Returns:
        Partner's course_subject_id or None if not a shared class
    """
    if class_number not in shared_class_info:
        return None

    partner_subject_name = shared_class_info[class_number]

    # Get current course_subject details
    cur.execute("""
        SELECT cs.course_id, s.area_id
        FROM course_subjects cs
        JOIN subjects s ON cs.subject_id = s.id
        WHERE cs.id = %s
    """, (course_subject_id,))
    current = cur.fetchone()

    if not current:
        return None

    # Find partner course_subject (same course, partner subject name, same area)
    cur.execute("""
        SELECT cs.id
        FROM course_subjects cs
        JOIN subjects s ON cs.subject_id = s.id
        WHERE cs.course_id = %s
          AND s.name = %s
          AND s.area_id = %s
          AND cs.id != %s
    """, (current['course_id'], partner_subject_name, current['area_id'], course_subject_id))

    partner = cur.fetchone()
    return partner['id'] if partner else None


def get_shared_class_info_for_course_subject(cur, course_subject_id: int) -> dict:
    """
    Get shared class info for a course_subject.
    Returns dict mapping class_number to partner_subject_name.
    """
    # Get course_subject details
    cur.execute("""
        SELECT cs.*, s.name as subject_name, s.area_id, c.schedule
        FROM course_subjects cs
        JOIN subjects s ON cs.subject_id = s.id
        JOIN courses c ON cs.course_id = c.id
        WHERE cs.id = %s
    """, (course_subject_id,))
    cs = cur.fetchone()

    if not cs:
        return {}

    # Get all subjects in the same area
    cur.execute("SELECT name FROM subjects WHERE area_id = %s", (cs['area_id'],))
    area_subjects = [s['name'] for s in cur.fetchall()]

    # Get total classes from coordination document
    cur.execute("""
        SELECT subjects_data FROM coordination_documents
        WHERE area_id = %s AND status = 'published'
        ORDER BY created_at DESC LIMIT 1
    """, (cs['area_id'],))
    doc = cur.fetchone()

    total_classes = 0
    if doc and doc.get('subjects_data'):
        subject_data = doc['subjects_data'].get(str(cs['subject_id']), {})
        total_classes = len(subject_data.get('class_plan', []))

    if total_classes == 0:
        return {}

    return calculate_shared_class_numbers(
        cs.get('schedule') or {},
        cs['subject_name'],
        area_subjects,
        total_classes
    )


@app.get("/", response_model=RootResponse)
async def root():
    return {"message": "Annual Planning API", "docs": "/docs"}


@app.get("/users", response_model=List[UserResponse])
async def get_users():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users")
            return cur.fetchall()


@app.get("/areas", response_model=List[AreaResponse])
async def get_areas():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM areas")
            return cur.fetchall()


@app.get("/subjects", response_model=List[SubjectResponse])
async def get_subjects():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM subjects")
            return cur.fetchall()


@app.get("/courses", response_model=List[CourseResponse])
async def get_courses():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM courses")
            return cur.fetchall()


@app.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
            return cur.fetchone()


@app.get("/courses/{course_id}/students", response_model=List[StudentResponse])
async def get_course_students(course_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM students WHERE course_id = %s ORDER BY name",
                (course_id,),
            )
            return cur.fetchall()


@app.get("/courses/{course_id}/shared-classes", response_model=SharedClassesResponse)
async def get_course_shared_classes(course_id: int, area_id: int):
    """Get shared classes for a course filtered by area."""
    with get_db() as conn:
        with conn.cursor() as cur:
            # Get the course schedule
            cur.execute("SELECT schedule FROM courses WHERE id = %s", (course_id,))
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Course not found")

            schedule = result.get("schedule") or {}

            # Get subject names for the area
            cur.execute("SELECT name FROM subjects WHERE area_id = %s", (area_id,))
            area_subjects = cur.fetchall()
            area_subject_names = [s["name"] for s in area_subjects]

            # Get shared classes
            shared_classes = get_shared_classes_for_area(schedule, area_subject_names)

            return {
                "course_id": course_id,
                "area_id": area_id,
                "shared_classes": shared_classes
            }


@app.get("/course-subjects", response_model=List[CourseSubjectResponse])
async def get_course_subjects():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT cs.*,
                       c.name as course_name,
                       s.name as subject_name,
                       u.name as teacher_name
                FROM course_subjects cs
                JOIN courses c ON cs.course_id = c.id
                JOIN subjects s ON cs.subject_id = s.id
                JOIN users u ON cs.teacher_id = u.id
                ORDER BY cs.course_id, cs.subject_id
            """)
            return cur.fetchall()


@app.get("/teachers/{teacher_id}/courses", response_model=List[CourseSubjectResponse])
async def get_teacher_courses(teacher_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT cs.*,
                       c.name as course_name,
                       s.name as subject_name,
                       s.area_id
                FROM course_subjects cs
                JOIN courses c ON cs.course_id = c.id
                JOIN subjects s ON cs.subject_id = s.id
                WHERE cs.teacher_id = %s
                ORDER BY c.name, s.name
            """, (teacher_id,))
            return cur.fetchall()


@app.get("/problematic-nuclei", response_model=List[ProblematicNucleusResponse])
async def get_problematic_nuclei():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM problematic_nuclei")
            return cur.fetchall()


@app.get("/knowledge-areas", response_model=List[KnowledgeAreaResponse])
async def get_knowledge_areas():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM knowledge_areas")
            return cur.fetchall()


@app.get("/categories", response_model=List[CategoryResponse])
async def get_categories():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM categories")
            return cur.fetchall()


@app.get("/coordination-documents", response_model=List[CoordinationDocumentResponse])
async def get_coordination_documents():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM coordination_documents")
            return cur.fetchall()


@app.get("/coordination-documents/{doc_id}", response_model=CoordinationDocumentDetailResponse)
async def get_coordination_document(doc_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM coordination_documents WHERE id = %s", (doc_id,))
            doc = cur.fetchone()
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found")

            # Fetch related data
            cur.execute("SELECT * FROM areas WHERE id = %s", (doc["area_id"],))
            area = cur.fetchone()

            cur.execute("SELECT * FROM subjects WHERE area_id = %s", (doc["area_id"],))
            subjects = cur.fetchall()

            # Fetch categories for this document
            category_ids = doc.get("category_ids") or []
            categories = []
            if category_ids:
                cur.execute("SELECT * FROM categories WHERE id = ANY(%s)", (category_ids,))
                categories = cur.fetchall()

            # Fetch nuclei for this document
            nucleus_ids = doc.get("nucleus_ids") or []
            nuclei = []
            if nucleus_ids:
                cur.execute("SELECT * FROM problematic_nuclei WHERE id = ANY(%s)", (nucleus_ids,))
                nuclei = cur.fetchall()

            return {
                **doc,
                "area": area,
                "subjects": subjects,
                "categories": categories,
                "nuclei": nuclei
            }


@app.patch("/coordination-documents/{doc_id}", response_model=CoordinationDocumentResponse)
async def update_coordination_document(doc_id: int, updates: CoordinationDocumentUpdate):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM coordination_documents WHERE id = %s", (doc_id,))
            doc = cur.fetchone()
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found")

            update_fields = []
            values = []

            if updates.name is not None:
                update_fields.append("name = %s")
                values.append(updates.name)

            if updates.methodological_strategies is not None:
                update_fields.append("methodological_strategies = %s")
                values.append(updates.methodological_strategies)

            if updates.subjects_data is not None:
                update_fields.append("subjects_data = %s")
                values.append(json.dumps(updates.subjects_data))

            if updates.status is not None:
                update_fields.append("status = %s")
                values.append(updates.status)

            if not update_fields:
                return doc

            values.append(doc_id)
            query = f"UPDATE coordination_documents SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
            cur.execute(query, values)
            conn.commit()
            return cur.fetchone()


@app.delete("/coordination-documents/{doc_id}", response_model=DeleteResponse)
async def delete_coordination_document(doc_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM coordination_documents WHERE id = %s", (doc_id,))
            doc = cur.fetchone()
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found")

            cur.execute("DELETE FROM coordination_documents WHERE id = %s", (doc_id,))
            conn.commit()
            return {"message": "Document deleted", "id": doc_id}


@app.post("/coordination-documents/{doc_id}/generate", response_model=CoordinationDocumentResponse)
async def generate_document_content(doc_id: int, request: GenerateRequest):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM coordination_documents WHERE id = %s", (doc_id,))
            doc = cur.fetchone()
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found")

            cur.execute("SELECT * FROM areas WHERE id = %s", (doc["area_id"],))
            area = cur.fetchone()

            cur.execute("SELECT * FROM subjects WHERE area_id = %s", (doc["area_id"],))
            subjects = cur.fetchall()

            category_ids = doc.get("category_ids") or []
            categories = []
            if category_ids:
                cur.execute("SELECT * FROM categories WHERE id = ANY(%s)", (category_ids,))
                categories = cur.fetchall()

            nucleus_ids = doc.get("nucleus_ids") or []
            nuclei = []
            if nucleus_ids:
                cur.execute("SELECT * FROM problematic_nuclei WHERE id = ANY(%s)", (nucleus_ids,))
                nuclei = cur.fetchall()

            updates = {}

            if request.generate_strategy:
                try:
                    strategy = generate_methodological_strategies(
                        area["name"] if area else "General",
                        subjects,
                        categories,
                        nuclei
                    )
                    updates["methodological_strategies"] = strategy
                except Exception as e:
                    raise HTTPException(
                        status_code=503,
                        detail=f"Error al conectar con el servicio de IA: {type(e).__name__}"
                    )

            if request.generate_class_plans and doc.get("subjects_data"):
                subjects_data = generate_class_plans(
                    doc["subjects_data"],
                    subjects,
                    categories
                )
                updates["subjects_data"] = subjects_data

            # Update document
            if updates:
                update_fields = []
                values = []

                if "methodological_strategies" in updates:
                    update_fields.append("methodological_strategies = %s")
                    values.append(updates["methodological_strategies"])

                if "subjects_data" in updates:
                    update_fields.append("subjects_data = %s")
                    values.append(json.dumps(updates["subjects_data"]))

                values.append(doc_id)
                query = f"UPDATE coordination_documents SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
                cur.execute(query, values)
                conn.commit()
                return cur.fetchone()

            return doc


@app.post("/coordination-documents/{doc_id}/chat", response_model=ChatResponse)
async def chat_with_document(doc_id: int, chat: ChatMessage):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM coordination_documents WHERE id = %s", (doc_id,))
            doc = cur.fetchone()
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found")

            cur.execute("SELECT * FROM subjects WHERE area_id = %s", (doc["area_id"],))
            subjects = cur.fetchall()

            category_ids = doc.get("category_ids") or []
            categories = []
            if category_ids:
                cur.execute("SELECT * FROM categories WHERE id = ANY(%s)", (category_ids,))
                categories = cur.fetchall()

            # Convert history to list of dicts
            history = [{"role": item.role, "content": item.content} for item in chat.history]
            result = process_chat_message(doc, history, subjects, categories)

            # Apply updates if any
            if result["updates"]:
                update_fields = []
                values = []

                if "name" in result["updates"]:
                    update_fields.append("name = %s")
                    values.append(result["updates"]["name"])

                if "methodological_strategies" in result["updates"]:
                    update_fields.append("methodological_strategies = %s")
                    values.append(result["updates"]["methodological_strategies"])

                if "subjects_data" in result["updates"]:
                    update_fields.append("subjects_data = %s")
                    values.append(json.dumps(result["updates"]["subjects_data"]))

                if update_fields:
                    values.append(doc_id)
                    query = f"UPDATE coordination_documents SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
                    cur.execute(query, values)
                    conn.commit()
                    updated_doc = cur.fetchone()
                    return {
                        "response": result["response"],
                        "document": updated_doc
                    }

            return {
                "response": result["response"],
                "document": doc
            }


@app.post("/coordination-documents", response_model=CoordinationDocumentResponse)
async def create_coordination_document(doc: CoordinationDocumentCreate):
    with get_db() as conn:
        with conn.cursor() as cur:
            # Validate that categories belong to selected nuclei
            if doc.category_ids and doc.nucleus_ids:
                cur.execute(
                    """
                    SELECT c.id FROM categories c
                    JOIN knowledge_areas ka ON c.knowledge_area_id = ka.id
                    WHERE c.id = ANY(%s) AND ka.nucleus_id = ANY(%s)
                    """,
                    (doc.category_ids, doc.nucleus_ids),
                )
                valid_category_ids = {row["id"] for row in cur.fetchall()}
                invalid_ids = set(doc.category_ids) - valid_category_ids
                if invalid_ids:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Categories {list(invalid_ids)} do not belong to the selected nuclei",
                    )

            cur.execute(
                """
                INSERT INTO coordination_documents
                (name, area_id, start_date, end_date, methodological_strategies, subjects_data, nucleus_ids, category_ids)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    doc.name,
                    doc.area_id,
                    doc.start_date,
                    doc.end_date,
                    doc.methodological_strategies,
                    json.dumps(doc.subjects_data) if doc.subjects_data else None,
                    doc.nucleus_ids,
                    doc.category_ids,
                ),
            )
            conn.commit()
            return cur.fetchone()


# ============= Catalog Endpoints =============

@app.get("/moment-types", response_model=List[MomentTypeResponse])
async def get_moment_types():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM moment_types ORDER BY id")
            return cur.fetchall()


@app.get("/activities", response_model=List[ActivityResponse])
async def get_activities():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM activities ORDER BY id")
            return cur.fetchall()


# ============= Teacher Lesson Plan Endpoints =============

@app.get("/teachers/{teacher_id}/lesson-plans", response_model=List[TeacherLessonPlanResponse])
async def get_teacher_lesson_plans(teacher_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT tlp.*,
                       c.name as course_name,
                       s.name as subject_name,
                       cd.name as document_name
                FROM teacher_lesson_plans tlp
                JOIN course_subjects cs ON tlp.course_subject_id = cs.id
                JOIN courses c ON cs.course_id = c.id
                JOIN subjects s ON cs.subject_id = s.id
                JOIN coordination_documents cd ON tlp.coordination_document_id = cd.id
                WHERE cs.teacher_id = %s
                ORDER BY tlp.course_subject_id, tlp.class_number
            """, (teacher_id,))
            return cur.fetchall()


@app.get("/course-subjects/{course_subject_id}/lesson-plans", response_model=List[TeacherLessonPlanResponse])
async def get_course_subject_lesson_plans(course_subject_id: int):
    """
    Get lesson plans for a course_subject, including plans from partner teachers
    for shared classes.
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            # Get shared class info for this course_subject
            shared_class_info = get_shared_class_info_for_course_subject(cur, course_subject_id)

            # Find all partner course_subject_ids for shared classes
            partner_cs_ids = set()
            for class_num in shared_class_info.keys():
                partner_id = find_partner_course_subject_id(cur, course_subject_id, shared_class_info, class_num)
                if partner_id:
                    partner_cs_ids.add(partner_id)

            # Query plans from both own and partner course_subjects
            all_cs_ids = [course_subject_id] + list(partner_cs_ids)

            cur.execute("""
                SELECT tlp.*,
                       tlp.course_subject_id as owner_course_subject_id,
                       u.name as created_by_teacher,
                       s.name as created_by_subject
                FROM teacher_lesson_plans tlp
                JOIN course_subjects cs ON tlp.course_subject_id = cs.id
                JOIN users u ON cs.teacher_id = u.id
                JOIN subjects s ON cs.subject_id = s.id
                WHERE tlp.course_subject_id = ANY(%s)
                ORDER BY tlp.class_number
            """, (all_cs_ids,))
            all_plans = cur.fetchall()

            # Filter: for shared classes, only return one plan (prioritize partner's if exists)
            result_plans = []
            seen_class_numbers = set()

            for plan in all_plans:
                class_num = plan['class_number']
                is_shared = class_num in shared_class_info
                is_own_plan = plan['owner_course_subject_id'] == course_subject_id

                # Include plan if:
                # 1. It's our own plan and we haven't seen this class number, OR
                # 2. It's a shared class from partner and we haven't seen this class number
                if class_num not in seen_class_numbers:
                    plan_dict = dict(plan)
                    plan_dict['is_shared_class'] = is_shared
                    plan_dict['shared_with_subject'] = shared_class_info.get(class_num)
                    plan_dict['is_own_plan'] = is_own_plan
                    result_plans.append(plan_dict)
                    seen_class_numbers.add(class_num)

            return result_plans


@app.get("/course-subjects/{course_subject_id}/coordination-status", response_model=CoordinationStatusResponse)
async def get_course_subject_coordination_status(course_subject_id: int):
    """Check if there's a published coordination document for this course-subject"""
    with get_db() as conn:
        with conn.cursor() as cur:
            # Get the course_subject details
            cur.execute("""
                SELECT cs.*, s.area_id, s.name as subject_name, c.name as course_name
                FROM course_subjects cs
                JOIN subjects s ON cs.subject_id = s.id
                JOIN courses c ON cs.course_id = c.id
                WHERE cs.id = %s
            """, (course_subject_id,))
            cs = cur.fetchone()

            if not cs:
                raise HTTPException(status_code=404, detail="Course subject not found")

            # Find published coordination document for this area
            cur.execute("""
                SELECT cd.*, u.name as coordinator_name
                FROM coordination_documents cd
                JOIN areas a ON cd.area_id = a.id
                LEFT JOIN users u ON a.coordinator_id = u.id
                WHERE cd.area_id = %s
                  AND cd.status = 'published'
                ORDER BY cd.created_at DESC
                LIMIT 1
            """, (cs["area_id"],))
            doc = cur.fetchone()

            if doc:
                # Get class plan for this subject from the document
                subjects_data = doc.get("subjects_data") or {}
                subject_id = str(cs["subject_id"])
                class_plan = []
                if subject_id in subjects_data:
                    class_plan = subjects_data[subject_id].get("class_plan", [])

                # Get document-level category_ids (all categories available in the document)
                document_category_ids = doc.get("category_ids") or []
                document_nucleus_ids = doc.get("nucleus_ids") or []

                return {
                    "has_published_document": True,
                    "document_id": doc["id"],
                    "document_name": doc["name"],
                    "coordinator_name": doc.get("coordinator_name"),
                    "class_plan": class_plan,
                    "subject_category_ids": subjects_data.get(subject_id, {}).get("category_ids", []),
                    "category_ids": document_category_ids,  # All categories from the document
                    "nucleus_ids": document_nucleus_ids  # Nuclei from the document
                }

            return {
                "has_published_document": False,
                "document_id": None,
                "document_name": None,
                "coordinator_name": None,
                "class_plan": [],
                "subject_category_ids": [],
                "category_ids": [],
                "nucleus_ids": []
            }


@app.get("/course-subjects/{course_subject_id}/shared-class-numbers", response_model=SharedClassNumbersResponse)
async def get_shared_class_numbers(course_subject_id: int):
    """Get list of class numbers that fall on shared time slots"""
    with get_db() as conn:
        with conn.cursor() as cur:
            # Get course_subject details
            cur.execute("""
                SELECT cs.*, s.name as subject_name, s.area_id, c.schedule
                FROM course_subjects cs
                JOIN subjects s ON cs.subject_id = s.id
                JOIN courses c ON cs.course_id = c.id
                WHERE cs.id = %s
            """, (course_subject_id,))
            cs = cur.fetchone()

            if not cs:
                raise HTTPException(status_code=404, detail="Course subject not found")

            # Get all subjects in the same area (for shared class detection)
            cur.execute("SELECT name FROM subjects WHERE area_id = %s", (cs["area_id"],))
            area_subjects = cur.fetchall()
            area_subject_names = [s["name"] for s in area_subjects]

            # Get the coordination document to find total classes for this subject
            cur.execute("""
                SELECT cd.subjects_data
                FROM coordination_documents cd
                WHERE cd.area_id = %s AND cd.status = 'published'
                ORDER BY cd.created_at DESC
                LIMIT 1
            """, (cs["area_id"],))
            doc = cur.fetchone()

            total_classes = 0
            if doc and doc.get("subjects_data"):
                subject_id = str(cs["subject_id"])
                if subject_id in doc["subjects_data"]:
                    class_plan = doc["subjects_data"][subject_id].get("class_plan", [])
                    total_classes = len(class_plan)

            if total_classes == 0:
                return {"shared_class_numbers": []}

            # Calculate which class numbers are shared and with which subject
            schedule = cs.get("schedule") or {}
            shared_info = calculate_shared_class_numbers(
                schedule,
                cs["subject_name"],
                area_subject_names,
                total_classes
            )

            return {
                "shared_class_numbers": list(shared_info.keys()),
                "shared_class_info": shared_info  # {class_number: shared_with_subject_name}
            }


@app.get("/teacher-lesson-plans/{plan_id}", response_model=TeacherLessonPlanDetailResponse)
async def get_teacher_lesson_plan(plan_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT tlp.*,
                       cs.course_id, cs.subject_id, cs.teacher_id,
                       c.name as course_name,
                       s.name as subject_name,
                       cd.name as document_name,
                       cd.subjects_data
                FROM teacher_lesson_plans tlp
                JOIN course_subjects cs ON tlp.course_subject_id = cs.id
                JOIN courses c ON cs.course_id = c.id
                JOIN subjects s ON cs.subject_id = s.id
                JOIN coordination_documents cd ON tlp.coordination_document_id = cd.id
                WHERE tlp.id = %s
            """, (plan_id,))
            plan = cur.fetchone()

            if not plan:
                raise HTTPException(status_code=404, detail="Lesson plan not found")

            # Get moment types and activities for the form
            cur.execute("SELECT * FROM moment_types ORDER BY id")
            moment_types = cur.fetchall()

            cur.execute("SELECT * FROM activities ORDER BY id")
            activities = cur.fetchall()

            # Get categories for the plan
            category_ids = plan.get("category_ids") or []
            categories = []
            if category_ids:
                cur.execute("SELECT * FROM categories WHERE id = ANY(%s)", (category_ids,))
                categories = cur.fetchall()

            return {
                **plan,
                "moment_types": moment_types,
                "activities": activities,
                "categories": categories
            }


@app.post("/teacher-lesson-plans", response_model=TeacherLessonPlanResponse)
async def create_teacher_lesson_plan(plan: TeacherLessonPlanCreate):
    with get_db() as conn:
        with conn.cursor() as cur:
            # Verify course_subject exists
            cur.execute("SELECT * FROM course_subjects WHERE id = %s", (plan.course_subject_id,))
            cs = cur.fetchone()
            if not cs:
                raise HTTPException(status_code=404, detail="Course subject not found")

            # Verify coordination document exists
            cur.execute("SELECT * FROM coordination_documents WHERE id = %s", (plan.coordination_document_id,))
            doc = cur.fetchone()
            if not doc:
                raise HTTPException(status_code=404, detail="Coordination document not found")

            # Check if this is a shared class and if partner already has a plan
            shared_class_info = get_shared_class_info_for_course_subject(cur, plan.course_subject_id)
            if plan.class_number in shared_class_info:
                partner_cs_id = find_partner_course_subject_id(
                    cur, plan.course_subject_id, shared_class_info, plan.class_number
                )
                if partner_cs_id:
                    # Check if partner already created a plan for this class
                    cur.execute("""
                        SELECT tlp.*, u.name as created_by_teacher, s.name as created_by_subject
                        FROM teacher_lesson_plans tlp
                        JOIN course_subjects cs ON tlp.course_subject_id = cs.id
                        JOIN users u ON cs.teacher_id = u.id
                        JOIN subjects s ON cs.subject_id = s.id
                        WHERE tlp.course_subject_id = %s
                          AND tlp.coordination_document_id = %s
                          AND tlp.class_number = %s
                    """, (partner_cs_id, plan.coordination_document_id, plan.class_number))
                    existing_partner_plan = cur.fetchone()

                    if existing_partner_plan:
                        # Return existing partner plan instead of creating duplicate
                        plan_dict = dict(existing_partner_plan)
                        plan_dict['is_shared_class'] = True
                        plan_dict['shared_with_subject'] = shared_class_info.get(plan.class_number)
                        plan_dict['is_own_plan'] = False
                        plan_dict['existing_shared_plan'] = True
                        return plan_dict

            cur.execute("""
                INSERT INTO teacher_lesson_plans
                (course_subject_id, coordination_document_id, class_number, title, category_ids,
                 objective, knowledge_content, didactic_strategies, class_format, moments, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
                ON CONFLICT (course_subject_id, coordination_document_id, class_number)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    category_ids = EXCLUDED.category_ids,
                    objective = EXCLUDED.objective,
                    knowledge_content = EXCLUDED.knowledge_content,
                    didactic_strategies = EXCLUDED.didactic_strategies,
                    class_format = EXCLUDED.class_format,
                    moments = EXCLUDED.moments,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING *
            """, (
                plan.course_subject_id,
                plan.coordination_document_id,
                plan.class_number,
                plan.title,
                plan.category_ids,
                plan.objective,
                plan.knowledge_content,
                plan.didactic_strategies,
                plan.class_format,
                json.dumps(plan.moments) if plan.moments else None
            ))
            conn.commit()
            return cur.fetchone()


class GenerateMomentRequest(BaseModel):
    moment_type: str  # apertura, desarrollo, cierre


# ============= Proposal Models =============

class ProposalResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    duration_weeks: int
    tools: list
    curriculum_card: dict
    alizia_info: dict
    initial_agreements: list
    stages: list
    is_active: bool
    created_at: datetime

class ProposalProgressCreate(BaseModel):
    user_id: int
    proposal_id: int
    course_subject_id: int

class ProposalProgressResponse(BaseModel):
    id: int
    user_id: int
    proposal_id: int
    course_subject_id: int
    status: str
    agreements_data: dict
    stages_data: dict
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

class AgreementUpdate(BaseModel):
    status: Optional[str] = None
    decision_value: Optional[str] = None
    conversation_history: Optional[list] = None

class DecisionUpdate(BaseModel):
    status: Optional[str] = None
    decision_value: Optional[str] = None
    conversation_history: Optional[list] = None

class ProposalChatMessage(BaseModel):
    history: List[ChatHistoryItem]

class ProposalChatResponse(BaseModel):
    response: str
    agreement_completed: bool = False
    decision_value: Optional[str] = None


@app.post("/teacher-lesson-plans/{plan_id}/generate-moment", response_model=GenerateMomentResponse)
async def generate_lesson_plan_moment(plan_id: int, request: GenerateMomentRequest):
    """Generate AI content for a specific moment of a lesson plan."""
    with get_db() as conn:
        with conn.cursor() as cur:
            # Get the lesson plan with subject info
            cur.execute("""
                SELECT tlp.*, s.name as subject_name
                FROM teacher_lesson_plans tlp
                JOIN course_subjects cs ON tlp.course_subject_id = cs.id
                JOIN subjects s ON cs.subject_id = s.id
                WHERE tlp.id = %s
            """, (plan_id,))
            plan = cur.fetchone()

            if not plan:
                raise HTTPException(status_code=404, detail="Lesson plan not found")

            # Get all activities to map IDs to names
            cur.execute("SELECT * FROM activities")
            all_activities = {a["id"]: a["name"] for a in cur.fetchall()}

            # Get moment data
            moments = plan.get("moments") or {}
            moment_data = moments.get(request.moment_type, {})
            activity_ids = moment_data.get("activities", [])
            custom_text = moment_data.get("customText", "")

            # Get activity names
            activity_names = [all_activities.get(aid, f"Actividad {aid}") for aid in activity_ids]

            # Generate content using AI
            generated_content = generate_lesson_moment_content(
                moment_type=request.moment_type,
                subject_name=plan["subject_name"],
                class_title=plan.get("title") or "",
                objective=plan.get("objective") or "",
                activity_names=activity_names,
                custom_text=custom_text
            )

            # Update the moments with generated content
            moments[request.moment_type] = {
                **moment_data,
                "generatedContent": generated_content
            }

            # Save back to database
            cur.execute("""
                UPDATE teacher_lesson_plans
                SET moments = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING *
            """, (json.dumps(moments), plan_id))
            conn.commit()

            return {
                "moment_type": request.moment_type,
                "generated_content": generated_content,
                "plan": cur.fetchone()
            }


@app.patch("/teacher-lesson-plans/{plan_id}", response_model=TeacherLessonPlanResponse)
async def update_teacher_lesson_plan(plan_id: int, updates: TeacherLessonPlanUpdate):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM teacher_lesson_plans WHERE id = %s", (plan_id,))
            plan = cur.fetchone()
            if not plan:
                raise HTTPException(status_code=404, detail="Lesson plan not found")

            update_fields = ["updated_at = CURRENT_TIMESTAMP"]
            values = []

            if updates.title is not None:
                update_fields.append("title = %s")
                values.append(updates.title)

            if updates.category_ids is not None:
                update_fields.append("category_ids = %s")
                values.append(updates.category_ids)

            if updates.objective is not None:
                update_fields.append("objective = %s")
                values.append(updates.objective)

            if updates.knowledge_content is not None:
                update_fields.append("knowledge_content = %s")
                values.append(updates.knowledge_content)

            if updates.didactic_strategies is not None:
                update_fields.append("didactic_strategies = %s")
                values.append(updates.didactic_strategies)

            if updates.class_format is not None:
                update_fields.append("class_format = %s")
                values.append(updates.class_format)

            if updates.moments is not None:
                update_fields.append("moments = %s")
                values.append(json.dumps(updates.moments))

            if updates.status is not None:
                update_fields.append("status = %s")
                values.append(updates.status)

            values.append(plan_id)
            query = f"UPDATE teacher_lesson_plans SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
            cur.execute(query, values)
            conn.commit()
            return cur.fetchone()


@app.delete("/teacher-lesson-plans/{plan_id}", response_model=DeleteResponse)
async def delete_teacher_lesson_plan(plan_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM teacher_lesson_plans WHERE id = %s", (plan_id,))
            plan = cur.fetchone()
            if not plan:
                raise HTTPException(status_code=404, detail="Lesson plan not found")

            cur.execute("DELETE FROM teacher_lesson_plans WHERE id = %s", (plan_id,))
            conn.commit()
            return {"message": "Lesson plan deleted", "id": plan_id}


@app.post("/teacher-lesson-plans/{plan_id}/chat", response_model=TeacherChatResponse)
async def chat_with_teacher_lesson_plan(plan_id: int, chat: ChatMessage):
    with get_db() as conn:
        with conn.cursor() as cur:
            # Get plan with subject name
            cur.execute("""
                SELECT tlp.*, s.name as subject_name
                FROM teacher_lesson_plans tlp
                JOIN course_subjects cs ON tlp.course_subject_id = cs.id
                JOIN subjects s ON cs.subject_id = s.id
                WHERE tlp.id = %s
            """, (plan_id,))
            plan = cur.fetchone()
            if not plan:
                raise HTTPException(status_code=404, detail="Lesson plan not found")

            # Get all activities
            cur.execute("SELECT * FROM activities")
            activities = cur.fetchall()

            # Convert history to list of dicts
            history = [{"role": item.role, "content": item.content} for item in chat.history]
            result = process_teacher_lesson_chat(dict(plan), history, activities)

            # Apply updates if any
            if result["updates"]:
                update_fields = ["updated_at = CURRENT_TIMESTAMP"]
                values = []

                if "title" in result["updates"]:
                    update_fields.append("title = %s")
                    values.append(result["updates"]["title"])

                if "objective" in result["updates"]:
                    update_fields.append("objective = %s")
                    values.append(result["updates"]["objective"])

                if "moments" in result["updates"]:
                    update_fields.append("moments = %s")
                    values.append(json.dumps(result["updates"]["moments"]))

                if len(values) > 0:
                    values.append(plan_id)
                    query = f"UPDATE teacher_lesson_plans SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
                    cur.execute(query, values)
                    conn.commit()
                    updated_plan = cur.fetchone()
                    return {
                        "response": result["response"],
                        "plan": updated_plan,
                        "changes_made": result["changes_made"]
                    }

            return {
                "response": result["response"],
                "plan": plan,
                "changes_made": []
            }


# ============= Proposal Endpoints =============

@app.get("/proposals", response_model=List[ProposalResponse])
async def get_proposals():
    """Get all active proposals."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM proposals WHERE is_active = true ORDER BY id")
            return cur.fetchall()


@app.get("/proposals/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(proposal_id: int):
    """Get a proposal by ID with full details."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM proposals WHERE id = %s", (proposal_id,))
            proposal = cur.fetchone()
            if not proposal:
                raise HTTPException(status_code=404, detail="Proposal not found")
            return proposal


@app.get("/teachers/{teacher_id}/proposals", response_model=List[ProposalResponse])
async def get_teacher_proposals(teacher_id: int):
    """Get all proposals available for a teacher."""
    with get_db() as conn:
        with conn.cursor() as cur:
            # For now, return all active proposals
            # In the future, this could filter based on teacher's subjects/areas
            cur.execute("SELECT * FROM proposals WHERE is_active = true ORDER BY id")
            return cur.fetchall()


@app.post("/proposal-progress", response_model=ProposalProgressResponse)
async def create_proposal_progress(progress: ProposalProgressCreate):
    """Start a proposal for a teacher in a specific course-subject."""
    with get_db() as conn:
        with conn.cursor() as cur:
            # Check if progress already exists
            cur.execute("""
                SELECT * FROM proposal_progress
                WHERE user_id = %s AND proposal_id = %s AND course_subject_id = %s
            """, (progress.user_id, progress.proposal_id, progress.course_subject_id))
            existing = cur.fetchone()
            if existing:
                return existing

            # Create new progress
            cur.execute("""
                INSERT INTO proposal_progress (user_id, proposal_id, course_subject_id, status, started_at)
                VALUES (%s, %s, %s, 'in_progress', CURRENT_TIMESTAMP)
                RETURNING *
            """, (progress.user_id, progress.proposal_id, progress.course_subject_id))
            conn.commit()
            return cur.fetchone()


@app.get("/proposal-progress/{user_id}/{proposal_id}/{course_subject_id}", response_model=ProposalProgressResponse)
async def get_proposal_progress(user_id: int, proposal_id: int, course_subject_id: int):
    """Get current progress for a proposal."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM proposal_progress
                WHERE user_id = %s AND proposal_id = %s AND course_subject_id = %s
            """, (user_id, proposal_id, course_subject_id))
            progress = cur.fetchone()
            if not progress:
                raise HTTPException(status_code=404, detail="Progress not found")
            return progress


@app.get("/proposal-progress/{progress_id}", response_model=ProposalProgressResponse)
async def get_proposal_progress_by_id(progress_id: int):
    """Get proposal progress by ID."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM proposal_progress WHERE id = %s", (progress_id,))
            progress = cur.fetchone()
            if not progress:
                raise HTTPException(status_code=404, detail="Progress not found")
            return progress


@app.patch("/proposal-progress/{progress_id}/agreements/{agreement_id}")
async def update_agreement(progress_id: int, agreement_id: str, update: AgreementUpdate):
    """Update an agreement's status and value."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM proposal_progress WHERE id = %s", (progress_id,))
            progress = cur.fetchone()
            if not progress:
                raise HTTPException(status_code=404, detail="Progress not found")

            agreements_data = progress.get("agreements_data") or {}
            if agreement_id not in agreements_data:
                agreements_data[agreement_id] = {}

            if update.status is not None:
                agreements_data[agreement_id]["status"] = update.status
            if update.decision_value is not None:
                agreements_data[agreement_id]["decision_value"] = update.decision_value
            if update.conversation_history is not None:
                agreements_data[agreement_id]["conversation_history"] = update.conversation_history

            # Check if all agreements are completed to potentially update overall status
            cur.execute("SELECT initial_agreements FROM proposals WHERE id = %s", (progress["proposal_id"],))
            proposal = cur.fetchone()
            total_agreements = len(proposal.get("initial_agreements", []))
            completed_agreements = sum(1 for a in agreements_data.values() if a.get("status") == "completed")

            new_status = progress["status"]
            if completed_agreements == total_agreements and total_agreements > 0:
                new_status = "agreements_completed"

            cur.execute("""
                UPDATE proposal_progress
                SET agreements_data = %s, status = %s
                WHERE id = %s
                RETURNING *
            """, (json.dumps(agreements_data), new_status, progress_id))
            conn.commit()
            return cur.fetchone()


@app.patch("/proposal-progress/{progress_id}/stages/{stage_number}/decisions/{decision_id}")
async def update_stage_decision(progress_id: int, stage_number: int, decision_id: str, update: DecisionUpdate):
    """Update a stage decision's status and value."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM proposal_progress WHERE id = %s", (progress_id,))
            progress = cur.fetchone()
            if not progress:
                raise HTTPException(status_code=404, detail="Progress not found")

            stages_data = progress.get("stages_data") or {}
            stage_key = str(stage_number)
            if stage_key not in stages_data:
                stages_data[stage_key] = {}
            if decision_id not in stages_data[stage_key]:
                stages_data[stage_key][decision_id] = {}

            if update.status is not None:
                stages_data[stage_key][decision_id]["status"] = update.status
            if update.decision_value is not None:
                stages_data[stage_key][decision_id]["decision_value"] = update.decision_value
            if update.conversation_history is not None:
                stages_data[stage_key][decision_id]["conversation_history"] = update.conversation_history

            cur.execute("""
                UPDATE proposal_progress
                SET stages_data = %s
                WHERE id = %s
                RETURNING *
            """, (json.dumps(stages_data), progress_id))
            conn.commit()
            return cur.fetchone()


@app.post("/proposal-progress/{progress_id}/agreements/{agreement_id}/chat", response_model=ProposalChatResponse)
async def chat_with_agreement(progress_id: int, agreement_id: str, chat: ProposalChatMessage):
    """Chat with Alizia about a specific agreement."""
    with get_db() as conn:
        with conn.cursor() as cur:
            # Get progress
            cur.execute("SELECT * FROM proposal_progress WHERE id = %s", (progress_id,))
            progress = cur.fetchone()
            if not progress:
                raise HTTPException(status_code=404, detail="Progress not found")

            # Get proposal
            cur.execute("SELECT * FROM proposals WHERE id = %s", (progress["proposal_id"],))
            proposal = cur.fetchone()
            if not proposal:
                raise HTTPException(status_code=404, detail="Proposal not found")

            # Find the agreement
            initial_agreements = proposal.get("initial_agreements", [])
            agreement = next((a for a in initial_agreements if a["id"] == agreement_id), None)
            if not agreement:
                raise HTTPException(status_code=404, detail="Agreement not found")

            # Get existing value if any
            agreements_data = progress.get("agreements_data") or {}
            existing_value = agreements_data.get(agreement_id, {}).get("decision_value")

            # Process chat
            history = [{"role": item.role, "content": item.content} for item in chat.history]
            result = process_proposal_chat(
                agreement_title=agreement["title"],
                agreement_description=agreement["description"],
                responsible_type=agreement["responsible_type"],
                proposal_name=proposal["name"],
                history=history,
                existing_value=existing_value
            )

            # Update progress if value or completion changed
            if result["decision_value"] or result["agreement_completed"]:
                if agreement_id not in agreements_data:
                    agreements_data[agreement_id] = {}

                if result["decision_value"]:
                    agreements_data[agreement_id]["decision_value"] = result["decision_value"]

                if result["agreement_completed"]:
                    agreements_data[agreement_id]["status"] = "completed"

                # Save conversation history
                agreements_data[agreement_id]["conversation_history"] = history + [
                    {"role": "assistant", "content": result["response"]}
                ]

                # Check if all agreements completed
                total_agreements = len(initial_agreements)
                completed_agreements = sum(1 for a in agreements_data.values() if a.get("status") == "completed")
                new_status = "agreements_completed" if completed_agreements == total_agreements else progress["status"]

                cur.execute("""
                    UPDATE proposal_progress
                    SET agreements_data = %s, status = %s
                    WHERE id = %s
                """, (json.dumps(agreements_data), new_status, progress_id))
                conn.commit()

            return result


@app.post("/proposal-progress/{progress_id}/stages/{stage_number}/decisions/{decision_id}/chat", response_model=ProposalChatResponse)
async def chat_with_stage_decision(progress_id: int, stage_number: int, decision_id: str, chat: ProposalChatMessage):
    """Chat with Alizia about a specific stage decision."""
    with get_db() as conn:
        with conn.cursor() as cur:
            # Get progress
            cur.execute("SELECT * FROM proposal_progress WHERE id = %s", (progress_id,))
            progress = cur.fetchone()
            if not progress:
                raise HTTPException(status_code=404, detail="Progress not found")

            # Get proposal
            cur.execute("SELECT * FROM proposals WHERE id = %s", (progress["proposal_id"],))
            proposal = cur.fetchone()
            if not proposal:
                raise HTTPException(status_code=404, detail="Proposal not found")

            # Find the stage and decision
            stages = proposal.get("stages", [])
            stage = next((s for s in stages if s["number"] == stage_number), None)
            if not stage:
                raise HTTPException(status_code=404, detail="Stage not found")

            decision = next((d for d in stage.get("decisions", []) if d["id"] == decision_id), None)
            if not decision:
                raise HTTPException(status_code=404, detail="Decision not found")

            # Get existing value if any
            stages_data = progress.get("stages_data") or {}
            stage_key = str(stage_number)
            existing_value = stages_data.get(stage_key, {}).get(decision_id, {}).get("decision_value")

            # Process chat
            history = [{"role": item.role, "content": item.content} for item in chat.history]
            result = process_proposal_chat(
                agreement_title=decision["title"],
                agreement_description=decision["description"],
                responsible_type=decision["responsible_type"],
                proposal_name=proposal["name"],
                history=history,
                existing_value=existing_value
            )

            # Update progress if value or completion changed
            if result["decision_value"] or result["agreement_completed"]:
                if stage_key not in stages_data:
                    stages_data[stage_key] = {}
                if decision_id not in stages_data[stage_key]:
                    stages_data[stage_key][decision_id] = {}

                if result["decision_value"]:
                    stages_data[stage_key][decision_id]["decision_value"] = result["decision_value"]

                if result["agreement_completed"]:
                    stages_data[stage_key][decision_id]["status"] = "completed"

                # Save conversation history
                stages_data[stage_key][decision_id]["conversation_history"] = history + [
                    {"role": "assistant", "content": result["response"]}
                ]

                cur.execute("""
                    UPDATE proposal_progress
                    SET stages_data = %s
                    WHERE id = %s
                """, (json.dumps(stages_data), progress_id))
                conn.commit()

            return result
