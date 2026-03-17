import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, X, Share, CloudCheck, Clock, ArrowRight } from 'lucide-react';
import { useStore } from '@/store/useStore';
import { Button } from '@/components/ui/button';
import { ChatBot } from '@/components/ui/ChatBot';
import { api, postData } from '@/services/api';
import type { ChatMessage, Activity } from '@/types';

export function TeacherLessonPlan() {
  const { id } = useParams();
  const navigate = useNavigate();
  const planId = parseInt(id || '0');

  const [editingContent, setEditingContent] = useState<{ [key: string]: string }>({});
  const [selectedActivity, setSelectedActivity] = useState<{
    momentKey: string;
    activityId: number;
  } | null>(null);

  const {
    currentLessonPlan,
    setCurrentLessonPlan,
    teacherChatHistory,
    addTeacherChatMessage,
    clearTeacherChatHistory,
    isGenerating,
    setIsGenerating,
    activitiesByMoment,
    setActivitiesByMoment,
    categories,
    setCategories,
  } = useStore();

  useEffect(() => {
    loadPlan();
    loadActivities();
    loadCategories();
    return () => {
      clearTeacherChatHistory();
    };
  }, [planId]);

  // Auto-generate content for all activities when plan loads for the first time
  useEffect(() => {
    if (currentLessonPlan && !isGenerating) {
      const moments = (currentLessonPlan as any).moments || {};
      const needsGeneration = ['apertura', 'desarrollo', 'cierre'].some((moment) => {
        const activityIds: number[] = moments[moment]?.activities || [];
        const activityContent = moments[moment]?.activityContent || {};
        return activityIds.some((id) => !activityContent[String(id)]?.trim());
      });

      if (needsGeneration) {
        handleGenerateAllActivities();
      }
    }
  }, [currentLessonPlan?.id]);

  const loadPlan = async () => {
    try {
      const plan = await api.lessonPlans.getById(planId);
      setCurrentLessonPlan(plan as any);
    } catch (error) {
      console.error('Error loading plan:', error);
    }
  };

  const loadActivities = async () => {
    if (activitiesByMoment.apertura.length > 0) return;
    try {
      const data = await api.activities.getAll();
      setActivitiesByMoment(data as any);
    } catch (error) {
      console.error('Error loading activities:', error);
    }
  };

  const loadCategories = async () => {
    if (categories.length > 0) return;
    try {
      const data = await api.categories.getAll();
      setCategories(data);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const handleGenerateAllActivities = async () => {
    if (!currentLessonPlan || isGenerating) return;

    setIsGenerating(true);
    try {
      const moments = (currentLessonPlan as any).moments || {};

      // Collect all activities that need generation
      const pending: { moment_type: string; activity_id: number }[] = [];
      for (const momentType of ['apertura', 'desarrollo', 'cierre']) {
        const activityIds: number[] = moments[momentType]?.activities || [];
        const existingContent = moments[momentType]?.activityContent || {};
        for (const activityId of activityIds) {
          if (!existingContent[String(activityId)]?.trim()) {
            pending.push({ moment_type: momentType, activity_id: activityId });
          }
        }
      }

      // Launch all in parallel with staggered delay to avoid saturation
      await Promise.all(
        pending.map((req, i) =>
          new Promise((resolve) => setTimeout(resolve, i * 1000)).then(() =>
            postData(`/teacher-lesson-plans/${planId}/generate-activity`, req)
          )
        )
      );

      const updatedPlan = await api.lessonPlans.getById(planId);
      setCurrentLessonPlan(updatedPlan as any);
    } catch (error) {
      console.error('Error generating activity content:', error);
      alert('Error al generar contenido con IA');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleChatMessage = async (message: string) => {
    const userMessage: ChatMessage = {
      role: 'user',
      content: message.trim(),
    };

    addTeacherChatMessage(userMessage);
    setIsGenerating(true);

    try {
      const result = await api.chat.sendMessage(`/teacher-lesson-plans/${planId}/chat`, {
        history: teacherChatHistory.concat(userMessage),
      });

      addTeacherChatMessage({ role: 'assistant', content: (result as any).response });

      if ((result as any).plan && (result as any).changes_made && (result as any).changes_made.length > 0) {
        setCurrentLessonPlan({ ...currentLessonPlan, ...(result as any).plan });
      }
    } catch (e) {
      console.error('Error sending teacher chat message:', e);
      addTeacherChatMessage({ role: 'assistant', content: 'Lo siento, hubo un error. Intenta de nuevo.' });
    } finally {
      setIsGenerating(false);
    }
  };

  const editKey = (momentKey: string, activityId: number) => `${momentKey}:${activityId}`;

  const handleContentEdit = (momentKey: string, activityId: number, content: string) => {
    const key = editKey(momentKey, activityId);
    setEditingContent((prev) => ({ ...prev, [key]: content }));
  };

  const handleSaveContent = async (momentKey: string, activityId: number) => {
    try {
      const key = editKey(momentKey, activityId);
      const updatedContent = editingContent[key];
      if (!updatedContent || !currentLessonPlan) return;

      const moments = { ...(currentLessonPlan as any).moments };
      const momentData = { ...moments[momentKey] };
      const activityContent = { ...(momentData.activityContent || {}) };
      activityContent[String(activityId)] = updatedContent;
      momentData.activityContent = activityContent;
      moments[momentKey] = momentData;

      await api.lessonPlans.update(planId, { moments });

      setCurrentLessonPlan({
        ...currentLessonPlan,
        moments,
      } as any);

      setEditingContent((prev) => {
        const newState = { ...prev };
        delete newState[key];
        return newState;
      });
    } catch (error) {
      console.error('Error saving content:', error);
      alert('Error al guardar el contenido');
    }
  };

  if (!currentLessonPlan) {
    return <div className="flex items-center justify-center h-screen">Cargando...</div>;
  }

  const allActivities = [
    ...activitiesByMoment.apertura,
    ...activitiesByMoment.desarrollo,
    ...activitiesByMoment.cierre,
  ];

  const getActivitiesForMoment = (momentKey: string): Activity[] => {
    const moments = currentLessonPlan.moments as any;
    const activityIds = moments?.[momentKey]?.activities || [];
    return activityIds
      .map((actId: number) => allActivities.find((a) => a.id === actId))
      .filter(Boolean) as Activity[];
  };

  const getCategoryNames = (): string[] => {
    const categoryIds = currentLessonPlan.category_ids || [];
    return categoryIds
      .map((catId) => categories.find((c) => c.id === catId)?.name)
      .filter(Boolean) as string[];
  };

  const getSelectedActivityName = (): string => {
    if (!selectedActivity) return 'Actividad';
    const act = allActivities.find((a) => a.id === selectedActivity.activityId);
    return act?.name || 'Actividad';
  };

  const momentSections = [
    { key: 'apertura', name: 'Actividad de Apertura' },
    { key: 'desarrollo', name: 'Actividad de Desarrollo' },
    { key: 'cierre', name: 'Actividad de Cierre' },
  ];

  const selectedActivityContent = selectedActivity
    ? ((currentLessonPlan.moments as any)?.[selectedActivity.momentKey]
        ?.activityContent?.[String(selectedActivity.activityId)] || '')
    : '';

  const currentEditKey = selectedActivity
    ? editKey(selectedActivity.momentKey, selectedActivity.activityId)
    : '';

  return (
    <div className="h-screen flex flex-col gradient-background">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-[#DAD5F6] bg-[#FFFFFF26] backdrop-blur-sm">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(`/teacher/cs/${currentLessonPlan.course_subject_id}`)}
            className="cursor-pointer hover:opacity-70"
          >
            <ChevronLeft className="w-6 h-6 text-[#324155]" />
          </button>
        </div>
        <div className="flex items-center gap-2">
          <h1 className="header-title text-[#10182B]">Planificación de clase</h1>
          <CloudCheck className="w-5 h-5 text-[#324155]" />
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={() => {}}
            className="flex items-center gap-2 text-primary bg-muted border-none cursor-pointer rounded-xl hover:bg-muted hover:text-primary"
          >
            <Share className="w-4 h-4 text-primary" />
            Compartir
          </Button>
          <button
            onClick={() => navigate(`/teacher/cs/${currentLessonPlan.course_subject_id}`)}
            className="cursor-pointer hover:opacity-70"
          >
            <X className="w-6 h-6 text-[#324155]" />
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden p-6 gap-6">
        {/* Left Sidebar - Chat */}
        <div className="w-80 flex flex-col">
          <ChatBot
            messages={teacherChatHistory}
            onSendMessage={handleChatMessage}
            isGenerating={isGenerating}
            placeholder="Escribí tu mensaje para Alizia..."
            welcomeMessage={{
              title: 'Documento creado',
              content: 'Si necesitás realizar algún cambio, podés escribirme y lo ajustamos.',
            }}
          />
        </div>

        {/* Center - Class Content */}
        <div className="flex-1 flex flex-col activity-card-bg rounded-2xl overflow-hidden">
          {/* Header */}
          <div className="p-4 px-6 border-b border-[#DAD5F6] flex flex-row items-center justify-between h-14">
            <h3 className="headline-1-bold text-[#10182B]">{currentLessonPlan.title || 'Título clase'}</h3>
          </div>
          {/* Scrollable content */}
          <div className="flex-1 overflow-y-auto p-6">
            <div className="space-y-6">
              {/* Objetivo de la clase */}
              <div>
                <h4 className="section-title text-[#10182B] mb-2">Objetivo de la clase</h4>
                <p className="section-description text-[#324155] leading-relaxed">
                  {currentLessonPlan.objective || 'Sin objetivo definido'}
                </p>
              </div>

              {/* Categorías a trabajar */}
              {getCategoryNames().length > 0 && (
                <div>
                  <h4 className="section-title text-[#10182B] mb-2">Categorías a trabajar</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {getCategoryNames().map((name, idx) => (
                      <li key={idx} className="body-2-regular text-[#324155]">{name}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Activity sections */}
              {momentSections.map((section) => {
                const activities = getActivitiesForMoment(section.key);

                return (
                  <div key={section.key}>
                    <h4 className="section-title text-[#10182B] mb-3">{section.name}</h4>
                    {activities.length > 0 ? (
                      <div className="flex flex-wrap gap-4">
                        {activities.map((activity) => (
                          <div
                            key={activity.id}
                            onClick={() => setSelectedActivity({ momentKey: section.key, activityId: activity.id })}
                            className={`cursor-pointer bg-white border rounded-2xl p-4 flex flex-col justify-between min-w-[200px] max-w-[280px] flex-1 transition-all hover:shadow-md group ${
                              selectedActivity?.activityId === activity.id
                                ? 'border-primary shadow-md'
                                : 'border-[#E4E8EF]'
                            }`}
                          >
                            <h5 className="body-2-medium text-[#10182B] mb-3">{activity.name}</h5>
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-1 text-[#47566C]">
                                <Clock className="w-4 h-4" />
                                <span className="callout-regular">{activity.duration_minutes || 10} min</span>
                              </div>
                              <ArrowRight className="w-5 h-5 text-[#47566C] group-hover:translate-x-1 transition-transform" />
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="body-2-regular text-[#47566C]/60 italic">Sin actividades seleccionadas</p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Side Panel - Activity Content */}
        {selectedActivity && (
          <div className="w-96 flex flex-col activity-card-bg rounded-2xl overflow-hidden transition-all">
            {/* Panel Header */}
            <div className="p-4 px-6 border-b border-[#DAD5F6] flex flex-row items-center justify-between h-14">
              <h3 className="headline-1-bold text-[#10182B] truncate">{getSelectedActivityName()}</h3>
              <button
                onClick={() => {
                  setSelectedActivity(null);
                  if (currentEditKey) {
                    setEditingContent((prev) => {
                      const newState = { ...prev };
                      delete newState[currentEditKey];
                      return newState;
                    });
                  }
                }}
                className="cursor-pointer hover:opacity-70 flex-shrink-0"
              >
                <X className="w-5 h-5 text-[#324155]" />
              </button>
            </div>
            {/* Panel Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {selectedActivityContent ? (
                <div>
                  {editingContent[currentEditKey] !== undefined ? (
                    <div className="space-y-3">
                      <textarea
                        value={editingContent[currentEditKey]}
                        onChange={(e) => handleContentEdit(selectedActivity.momentKey, selectedActivity.activityId, e.target.value)}
                        className="w-full p-3 border border-[#DAD5F6] rounded-lg section-description text-[#324155] leading-relaxed resize-none focus:outline-none focus:ring-2 focus:ring-primary/20"
                        rows={12}
                        placeholder="Editá el contenido generado..."
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleSaveContent(selectedActivity.momentKey, selectedActivity.activityId)}
                          className="px-3 py-1.5 bg-primary text-white text-sm rounded-lg hover:bg-primary/90 cursor-pointer"
                        >
                          Guardar
                        </button>
                        <button
                          onClick={() => {
                            setEditingContent((prev) => {
                              const newState = { ...prev };
                              delete newState[currentEditKey];
                              return newState;
                            });
                          }}
                          className="px-3 py-1.5 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300 cursor-pointer"
                        >
                          Cancelar
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div
                      className="section-description text-[#324155] leading-relaxed whitespace-pre-wrap cursor-pointer hover:bg-[#F5F3FF] p-2 rounded-lg transition-colors"
                      onClick={() => handleContentEdit(selectedActivity.momentKey, selectedActivity.activityId, selectedActivityContent)}
                      title="Clic para editar"
                    >
                      {selectedActivityContent}
                    </div>
                  )}
                </div>
              ) : (
                <p className="body-2-regular text-[#47566C]/60 italic">Generando contenido con IA...</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
