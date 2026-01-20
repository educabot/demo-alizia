import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';
import { useStore } from '@/store/useStore';
import { TabsCustom, TabsCustomContent, TabsCustomList, TabsCustomTrigger } from '@/components/ui/tabs-custom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { StudentsList } from '@/components/ui/StudentsList';
import { CourseInfo } from '@/components/ui/CourseInfo';
import { api } from '@/services/api';
import type { CoordinationDocument } from '@/types';

interface Student {
  id: number;
  name: string;
}

export function Course() {
  const { id } = useParams();
  const navigate = useNavigate();
  const courseId = parseInt(id || '0');

  const { courses } = useStore();
  const getUserArea = useStore((state) => state.getUserArea());

  const [students, setStudents] = useState<Student[]>([]);
  const [areaDocs, setAreaDocs] = useState<CoordinationDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const course = courses.find((c) => c.id === courseId);

  useEffect(() => {
    loadCourseData();
  }, [courseId]);

  const loadCourseData = async () => {
    try {
      setIsLoading(true);
      const [studentsData, allDocs] = await Promise.all([api.courses.getStudents(courseId), api.documents.getAll()]);

      setStudents(studentsData as Student[]);

      if (getUserArea) {
        const filtered = (allDocs as CoordinationDocument[]).filter((d) => d.area_id === getUserArea.id);
        setAreaDocs(filtered);
      }
    } catch (error) {
      console.error('Error loading course data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePublishDocument = async (docId: number) => {
    try {
      await api.documents.publish(docId);
      loadCourseData();
    } catch (error) {
      console.error('Error publishing document:', error);
    }
  };

  const handleDeleteDocument = async (docId: number) => {
    if (!confirm('¿Estás seguro de que quieres borrar este documento?')) return;

    try {
      await api.documents.delete(docId);
      loadCourseData();
    } catch (error) {
      console.error('Error deleting document:', error);
    }
  };

  const handleStartWizard = () => {
    navigate(`/curso/${courseId}/crear`);
  };

  if (!course) {
    return <div>Curso no encontrado</div>;
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      {/* Header */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-4 mb-6 cursor-pointer transition-colors hover:text-gray-600"
      >
        <ChevronLeft className="text-[#10182B]" />
        <h1 className="title-2-emphasized text-[#10182B]">Curso {course.name}</h1>
      </button>

      <TabsCustom defaultValue="about" className="w-full">
        <TabsCustomList className="mb-8">
          <TabsCustomTrigger value="about">Detalle del curso</TabsCustomTrigger>
          <TabsCustomTrigger value="classes">Doc. de coordenadas</TabsCustomTrigger>
        </TabsCustomList>

        <TabsCustomContent value="about" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <StudentsList students={students} isLoading={isLoading} showActions={true} />

            <CourseInfo
              fields={[
                { label: 'INSTITUCIÓN', value: 'IFD. N°13' },
                { label: 'ÁREA', value: getUserArea?.name || 'N/A' },
                { label: 'NIVEL', value: 'Secundaria' },
                { label: 'TURNO', value: 'Mañana' },
                { label: 'CICLO LECTIVO', value: '2026' },
              ]}
              showSchedule={true}
            />
          </div>
        </TabsCustomContent>

        <TabsCustomContent value="classes" className="space-y-6">
          {isLoading ? (
            // Skeleton loading state for documents
            <>
              <div>
                <h3 className="headline-1-bold text-foreground mb-4">Documentos existentes</h3>
                <div className="space-y-3">
                  {Array.from({ length: 3 }).map((_, index) => (
                    <Card key={index} className="bg-white/50 backdrop-blur-sm border-slate-200 rounded-2xl">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between">
                          <div className="space-y-2">
                            <Skeleton className="h-6 w-20 rounded-full" />
                            <Skeleton className="h-5 w-48" />
                            <Skeleton className="h-4 w-32" />
                          </div>
                          <div className="flex gap-2">
                            <Skeleton className="h-8 w-16 rounded" />
                            <Skeleton className="h-8 w-16 rounded" />
                            <Skeleton className="h-8 w-16 rounded" />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
              <div className="h-px bg-slate-200" />
            </>
          ) : areaDocs.length > 0 ? (
            <>
              <div>
                <h3 className="headline-1-bold text-foreground mb-4">Documentos existentes</h3>
                <div className="space-y-3">
                  {areaDocs.map((doc) => (
                    <Card
                      key={doc.id}
                      className="bg-white/50 backdrop-blur-sm border-slate-200 rounded-2xl cursor-pointer hover:shadow-lg transition-all"
                      onClick={() => navigate(`/doc/${doc.id}`)}
                    >
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between">
                          <div className="space-y-2">
                            <Badge
                              className={
                                doc.status === 'published'
                                  ? 'bg-green-100 text-green-800 hover:bg-green-100'
                                  : doc.status === 'archived'
                                    ? 'bg-gray-100 text-gray-800 hover:bg-gray-100'
                                    : 'bg-amber-100 text-amber-800 hover:bg-amber-100'
                              }
                            >
                              {doc.status === 'published'
                                ? 'Publicado'
                                : doc.status === 'archived'
                                  ? 'Archivado'
                                  : 'Borrador'}
                            </Badge>
                            <h4 className="headline-1-bold text-foreground">{doc.name}</h4>
                            <p className="body-2-regular text-muted-foreground">
                              {doc.start_date} - {doc.end_date}
                            </p>
                          </div>
                          <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                            {doc.status !== 'published' && (
                              <Button size="sm" variant="default" onClick={() => handlePublishDocument(doc.id)}>
                                Publicar
                              </Button>
                            )}
                            <Button size="sm" variant="outline" onClick={() => navigate(`/doc/${doc.id}`)}>
                              Editar
                            </Button>
                            <Button size="sm" variant="destructive" onClick={() => handleDeleteDocument(doc.id)}>
                              Borrar
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
              <div className="h-px bg-slate-200" />
            </>
          ) : (
            <div>
              <h3 className="headline-1-bold text-foreground mb-4">Documentos existentes</h3>
              <p className="body-2-regular text-muted-foreground">No hay documentos disponibles</p>
            </div>
          )}

          <div>
            <h3 className="headline-1-bold text-foreground mb-4">Crear nuevo documento</h3>
            <Card className="bg-white/50 backdrop-blur-sm border-slate-200 rounded-3xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Badge className="bg-primary/10 text-primary hover:bg-primary/10">Nuevo</Badge>
                    <h4 className="headline-1-bold text-foreground">Documento de coordinación</h4>
                    <p className="body-2-regular text-muted-foreground">
                      Crear documento para el área {getUserArea?.name || ''}
                    </p>
                  </div>
                  <Button onClick={handleStartWizard}>Crear</Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsCustomContent>
      </TabsCustom>
    </div>
  );
}
