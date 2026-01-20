import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Send, Loader2 } from 'lucide-react';
import { useStore } from '@/store/useStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { api } from '@/services/api';
import type { CoordinationDocument, ChatMessage } from '@/types';

export function Document() {
  const { id } = useParams();
  const navigate = useNavigate();
  const docId = parseInt(id || '0');

  const {
    currentDocument,
    setCurrentDocument,
    chatHistory,
    addChatMessage,
    clearChatHistory,
    isGenerating,
    setIsGenerating,
    expandedSubjects,
    toggleSubjectExpanded,
  } = useStore();

  const [chatInput, setChatInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadDocument();
    return () => {
      clearChatHistory();
    };
  }, [docId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const loadDocument = async () => {
    try {
      const doc = await api.documents.getById(docId);
      setCurrentDocument(doc as CoordinationDocument);
    } catch (error) {
      console.error('Error loading document:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim() || !currentDocument) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: chatInput,
    };

    addChatMessage(userMessage);
    setChatInput('');
    setIsGenerating(true);

    try {
      const response = await api.chat.sendMessage(`/coordination-documents/${docId}/chat`, {
        message: chatInput,
        history: chatHistory,
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: (response as any).response || 'Sin respuesta',
      };

      addChatMessage(assistantMessage);

      if ((response as any).updated_document) {
        setCurrentDocument((response as any).updated_document);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Error al procesar el mensaje',
      };
      addChatMessage(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerateContent = async () => {
    if (!currentDocument) return;

    setIsGenerating(true);
    try {
      const response = await api.chat.sendMessage(`/coordination-documents/${docId}/generate`, {});

      if ((response as any).updated_document) {
        setCurrentDocument((response as any).updated_document);
      }
    } catch (error) {
      console.error('Error generating content:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSaveTitle = async (newTitle: string) => {
    if (!currentDocument || newTitle === currentDocument.name) return;

    try {
      await api.documents.update(docId, { name: newTitle });
      setCurrentDocument({ ...currentDocument, name: newTitle });
    } catch (error) {
      console.error('Error saving title:', error);
    }
  };

  if (!currentDocument) {
    return <div className="flex items-center justify-center h-screen">Cargando...</div>;
  }

  const categoryMap: Record<number, string> = {};
  (currentDocument.content?.categories || []).forEach((c: any) => {
    categoryMap[c.id] = c.name;
  });

  const subjectsData = currentDocument.content?.subjects_data || {};
  const subjects = currentDocument.content?.subjects || [];

  const documentCategoryIds = currentDocument.content?.category_ids || [];
  const assignedCategoryIds = new Set<number>();
  Object.values(subjectsData).forEach((sData: any) => {
    (sData.class_plan || []).forEach((c: any) => {
      (c.category_ids || []).forEach((catId: number) => assignedCategoryIds.add(catId));
    });
  });

  const unassignedCategories = documentCategoryIds
    .filter((catId: number) => !assignedCategoryIds.has(catId))
    .map((catId: number) => ({ id: catId, name: categoryMap[catId] || `Categoría ${catId}` }));

  const hasContent = currentDocument.content?.methodological_strategies?.trim().length > 0;

  return (
    <div className="h-screen flex flex-col">
      <div className="border-b p-4 flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate('/')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Doc. de coordinación
        </Button>
        <Button variant="outline">Compartir</Button>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            <div>
              <h2
                className="text-3xl font-bold outline-none"
                contentEditable
                suppressContentEditableWarning
                onBlur={(e) => handleSaveTitle(e.currentTarget.textContent || '')}
              >
                {currentDocument.name}
              </h2>
            </div>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold">Estrategia metodológica</h3>
                  {!hasContent && !isGenerating && (
                    <Button size="sm" onClick={handleGenerateContent}>
                      Generar con IA
                    </Button>
                  )}
                </div>
                {isGenerating ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin mr-2" />
                    <p>Generando contenido con IA...</p>
                  </div>
                ) : (
                  <div className="prose max-w-none">
                    {hasContent ? (
                      <p>{currentDocument.content?.methodological_strategies}</p>
                    ) : (
                      <p className="text-muted-foreground">
                        Haz clic en "Generar con IA" o haz doble clic para escribir manualmente
                      </p>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-2">Tiempos</h3>
                <p className="text-muted-foreground">
                  {currentDocument.start_date} - {currentDocument.end_date}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-4">Clases por disciplinas</h3>
                <div className="space-y-4">
                  {subjects.length === 0 ? (
                    <p className="text-muted-foreground">No hay materias configuradas</p>
                  ) : (
                    subjects.map((s: any) => {
                      const sData = subjectsData[s.id] || {};
                      const classPlan = sData.class_plan || [];
                      const isExpanded = expandedSubjects[s.id];

                      return (
                        <div key={s.id} className="border rounded-lg">
                          <div
                            className="flex items-center justify-between p-4 cursor-pointer hover:bg-muted/50"
                            onClick={() => toggleSubjectExpanded(s.id.toString())}
                          >
                            <div className="flex items-center gap-2">
                              <span>{isExpanded ? '▼' : '▶'}</span>
                              <h4 className="font-semibold">{s.name}</h4>
                            </div>
                            <Badge variant="secondary">{classPlan.length} clases</Badge>
                          </div>
                          {isExpanded && (
                            <div className="p-4 pt-0 space-y-2">
                              {classPlan.length === 0 ? (
                                <p className="text-sm text-muted-foreground">No hay plan de clases generado</p>
                              ) : (
                                classPlan.map((c: any) => (
                                  <div key={c.class_number} className="border rounded p-3 space-y-2">
                                    <div className="flex items-start gap-2">
                                      <Badge variant="outline">Clase {c.class_number}</Badge>
                                      <p className="flex-1 font-medium">{c.title || 'Sin título'}</p>
                                    </div>
                                    <div className="flex flex-wrap gap-1">
                                      {(c.category_ids || []).map((catId: number) => (
                                        <Badge key={catId} variant="secondary" className="text-xs">
                                          {categoryMap[catId] || `Cat ${catId}`}
                                        </Badge>
                                      ))}
                                    </div>
                                  </div>
                                ))
                              )}
                            </div>
                          )}
                        </div>
                      );
                    })
                  )}
                </div>

                {unassignedCategories.length > 0 && (
                  <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
                    <div className="flex gap-2">
                      <span className="text-xl">⚠️</span>
                      <div className="flex-1">
                        <p className="font-semibold mb-2">Conceptos sin asignar a clases:</p>
                        <div className="flex flex-wrap gap-1 mb-2">
                          {unassignedCategories.map((cat) => (
                            <Badge key={cat.id} variant="outline">
                              {cat.name}
                            </Badge>
                          ))}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          Usa el chat para asignar estos conceptos a las clases.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
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
            {chatHistory.length === 0 ? (
              <div className="text-sm text-muted-foreground">
                Hola! Soy Alizia, tu asistente de planificación. Puedo ayudarte a modificar el documento. Prueba pedirme
                que cambie el título o actualice una clase.
              </div>
            ) : (
              chatHistory.map((msg, idx) => (
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
