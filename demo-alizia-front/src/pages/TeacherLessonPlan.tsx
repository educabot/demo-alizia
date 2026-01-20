import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Send, Loader2 } from 'lucide-react';
import { useStore } from '@/store/useStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { api } from '@/services/api';
import type { ChatMessage } from '@/types';

export function TeacherLessonPlan() {
  const { id } = useParams();
  const navigate = useNavigate();
  const planId = parseInt(id || '0');

  const {
    currentLessonPlan,
    setCurrentLessonPlan,
    teacherChatHistory,
    addTeacherChatMessage,
    clearTeacherChatHistory,
    isGenerating,
    setIsGenerating,
    categories,
    activities,
  } = useStore();

  const [chatInput, setChatInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadPlan();
    return () => {
      clearTeacherChatHistory();
    };
  }, [planId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [teacherChatHistory]);

  const loadPlan = async () => {
    try {
      const plan = await api.lessonPlans.getById(planId);
      setCurrentLessonPlan(plan as any);
    } catch (error) {
      console.error('Error loading plan:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim() || !currentLessonPlan) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: chatInput,
    };

    addTeacherChatMessage(userMessage);
    setChatInput('');
    setIsGenerating(true);

    try {
      const response = await api.chat.sendMessage(`/teacher-lesson-plans/${planId}/chat`, {
        message: chatInput,
        history: teacherChatHistory,
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: (response as any).response || 'Sin respuesta',
      };

      addTeacherChatMessage(assistantMessage);

      if ((response as any).updated_plan) {
        setCurrentLessonPlan((response as any).updated_plan);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Error al procesar el mensaje',
      };
      addTeacherChatMessage(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  if (!currentLessonPlan) {
    return <div className="flex items-center justify-center h-screen">Cargando...</div>;
  }

  const categoryNames = (currentLessonPlan.category_ids || []).map((catId: number) => {
    const cat = categories.find((c) => c.id === catId);
    return cat ? cat.name : `Cat ${catId}`;
  });

  const getActivityNames = (momentKey: string) => {
    const activityIds = currentLessonPlan.moments?.[momentKey]?.activities || [];
    return activityIds.map((actId: number) => {
      const act = activities.find((a) => a.id === actId);
      return act ? act.name : `Act ${actId}`;
    });
  };

  const momentTypes = [
    { key: 'apertura', name: 'Apertura/Motivación' },
    { key: 'desarrollo', name: 'Desarrollo/Construcción' },
    { key: 'cierre', name: 'Cierre/Metacognición' },
  ];

  return (
    <div className="h-screen flex flex-col">
      <div className="border-b p-4 flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate(`/teacher/cs/${currentLessonPlan.course_subject_id}`)}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          {currentLessonPlan.course_name} - {currentLessonPlan.subject_name}
        </Button>
        <Badge variant={currentLessonPlan.status === 'planned' ? 'default' : 'secondary'}>
          {currentLessonPlan.status === 'planned' ? 'Planificada' : 'En progreso'}
        </Badge>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            <div>
              <h2 className="text-3xl font-bold">
                Clase {currentLessonPlan.class_number}: {currentLessonPlan.title || 'Sin título'}
              </h2>
            </div>

            <Card>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-2">Objetivo</h3>
                <p>{currentLessonPlan.objective || <em>No definido</em>}</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-3">Categorías</h3>
                <div className="flex flex-wrap gap-2">
                  {categoryNames.map((name, idx) => (
                    <Badge key={idx} variant="secondary">
                      {name}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-4">Momentos de la clase</h3>
                <div className="space-y-4">
                  {momentTypes.map((mt) => {
                    const activityNames = getActivityNames(mt.key);
                    const customText = currentLessonPlan.moments?.[mt.key]?.customText || '';

                    return (
                      <div key={mt.key} className="border rounded-lg p-4">
                        <h4 className="font-semibold mb-2">{mt.name}</h4>
                        {activityNames.length > 0 && (
                          <div className="mb-2">
                            <p className="text-sm font-medium mb-1">Actividades:</p>
                            <div className="flex flex-wrap gap-1">
                              {activityNames.map((name, idx) => (
                                <Badge key={idx} variant="outline" className="text-xs">
                                  {name}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        {customText && (
                          <div>
                            <p className="text-sm font-medium mb-1">Otros:</p>
                            <p className="text-sm text-muted-foreground">{customText}</p>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="w-96 border-l flex flex-col">
          <div className="p-4 border-b flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">
              A
            </div>
            <div>
              <h3 className="font-semibold">Chat con Alizia</h3>
              <p className="text-xs text-muted-foreground">Tu asistente de planificación</p>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {teacherChatHistory.length === 0 ? (
              <div className="text-sm text-muted-foreground">
                Hola! Soy Alizia, tu asistente de planificación. Puedo ayudarte a mejorar tu plan de clase. Pídeme que
                reescriba la apertura, cambie el desarrollo, o modifique cualquier momento.
              </div>
            ) : (
              teacherChatHistory.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                    }`}
                  >
                    <p className="text-sm">{msg.content}</p>
                  </div>
                </div>
              ))
            )}
            {isGenerating && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg p-3">
                  <Loader2 className="h-4 w-4 animate-spin" />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="p-4 border-t">
            <div className="flex gap-2">
              <Input
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Escribe un mensaje..."
                disabled={isGenerating}
              />
              <Button size="icon" onClick={handleSendMessage} disabled={isGenerating}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
