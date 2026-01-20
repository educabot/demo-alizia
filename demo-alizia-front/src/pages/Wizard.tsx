import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useStore } from '@/store/useStore';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { api } from '@/services/api';

export function Wizard() {
  const { id } = useParams();
  const navigate = useNavigate();
  const courseId = parseInt(id || '0');

  const { wizardData, updateWizardData, resetWizardData, subjects, nuclei, knowledgeAreas, categories } = useStore();
  const getUserArea = useStore((state) => state.getUserArea());

  const [draggedCategoryId, setDraggedCategoryId] = useState<number | null>(null);

  useEffect(() => {
    if (getUserArea && !wizardData.areaId) {
      updateWizardData({
        areaId: getUserArea.id,
        name: getUserArea.name,
      });
    }
  }, [getUserArea]);

  const getFilteredCategories = () => {
    if (wizardData.nucleusIds.length === 0) return [];

    const knowledgeAreaIds = knowledgeAreas
      .filter((ka) => wizardData.nucleusIds.includes(ka.nucleus_id))
      .map((ka) => ka.id);

    return categories.filter((c) => knowledgeAreaIds.includes(c.knowledge_area_id));
  };

  const toggleNucleus = (nucleusId: number) => {
    const idx = wizardData.nucleusIds.indexOf(nucleusId);
    let newNucleusIds: number[];

    if (idx === -1) {
      newNucleusIds = [...wizardData.nucleusIds, nucleusId];
    } else {
      newNucleusIds = wizardData.nucleusIds.filter((id) => id !== nucleusId);
      const validCategoryIds = getFilteredCategories().map((c) => c.id);
      const newCategoryIds = wizardData.categoryIds.filter((id) => validCategoryIds.includes(id));
      updateWizardData({ categoryIds: newCategoryIds });
    }

    updateWizardData({ nucleusIds: newNucleusIds });
  };

  const toggleCategory = (categoryId: number) => {
    const idx = wizardData.categoryIds.indexOf(categoryId);
    const newCategoryIds =
      idx === -1 ? [...wizardData.categoryIds, categoryId] : wizardData.categoryIds.filter((id) => id !== categoryId);

    updateWizardData({ categoryIds: newCategoryIds });
  };

  const handleDragStart = (categoryId: number) => {
    setDraggedCategoryId(categoryId);
  };

  const handleDrop = (subjectId: number | null) => {
    if (draggedCategoryId === null) return;

    const newSubjectCategories = { ...wizardData.subjectCategories };

    for (const sid in newSubjectCategories) {
      const idx = newSubjectCategories[sid].indexOf(draggedCategoryId);
      if (idx !== -1) {
        newSubjectCategories[sid].splice(idx, 1);
      }
    }

    if (subjectId !== null) {
      if (!newSubjectCategories[subjectId]) {
        newSubjectCategories[subjectId] = [];
      }
      newSubjectCategories[subjectId].push(draggedCategoryId);
    }

    updateWizardData({ subjectCategories: newSubjectCategories });
    setDraggedCategoryId(null);
  };

  const handleCreateDocument = async () => {
    const subjectsData: Record<string, any> = { ...wizardData.subjectsData };

    for (const [subjectId, categoryIds] of Object.entries(wizardData.subjectCategories)) {
      if (!subjectsData[subjectId]) {
        subjectsData[subjectId] = { class_count: 1 };
      }
      subjectsData[subjectId].category_ids = [...categoryIds];
    }

    const data = {
      name: wizardData.name,
      area_id: wizardData.areaId,
      start_date: wizardData.startDate,
      end_date: wizardData.endDate,
      methodological_strategies: null,
      subjects_data: Object.keys(subjectsData).length > 0 ? subjectsData : null,
      nucleus_ids: wizardData.nucleusIds,
      category_ids: wizardData.categoryIds,
    };

    try {
      const result = await api.documents.create(data);
      resetWizardData();
      navigate(`/curso/${courseId}`);
    } catch (error) {
      console.error('Error creating document:', error);
      alert('Error al crear el documento');
    }
  };

  const progress = (wizardData.step / 3) * 100;
  const areaSubjects = getUserArea ? subjects.filter((s) => s.area_id === getUserArea.id) : [];
  const filteredCategories = getFilteredCategories();

  const selectedCategories = categories.filter((c) => wizardData.categoryIds.includes(c.id));
  const assignedCategoryIds = Object.values(wizardData.subjectCategories).flat();
  const unassignedCategories = selectedCategories.filter((c) => !assignedCategoryIds.includes(c));

  return (
    <div className="max-w-4xl mx-auto">
      <Button variant="ghost" className="mb-4" onClick={() => navigate(`/curso/${courseId}`)}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        Doc. de coordinación - {wizardData.name}
      </Button>

      <Progress value={progress} className="mb-6" />

      {wizardData.step === 1 && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold">Detalle del documento</h2>

          <div className="space-y-2">
            <Label>Núcleos problemáticos del área</Label>
            <p className="text-sm text-muted-foreground">Selecciona uno o más núcleos</p>
            <div className="flex flex-wrap gap-2">
              {nuclei.map((n) => (
                <Badge
                  key={n.id}
                  variant={wizardData.nucleusIds.includes(n.id) ? 'default' : 'outline'}
                  className="cursor-pointer"
                  onClick={() => toggleNucleus(n.id)}
                >
                  {n.name}
                </Badge>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label>Categorías a trabajar</Label>
            <p className="text-sm text-muted-foreground">
              {wizardData.nucleusIds.length === 0
                ? 'Primero selecciona al menos un núcleo problemático'
                : 'Selecciona una o más categorías'}
            </p>
            <div className="flex flex-wrap gap-2">
              {filteredCategories.length === 0 ? (
                <span className="text-sm text-muted-foreground">No hay categorías disponibles</span>
              ) : (
                filteredCategories.map((c) => (
                  <Badge
                    key={c.id}
                    variant={wizardData.categoryIds.includes(c.id) ? 'default' : 'outline'}
                    className="cursor-pointer"
                    onClick={() => toggleCategory(c.id)}
                  >
                    {c.name}
                  </Badge>
                ))
              )}
            </div>
          </div>

          <div className="flex justify-end">
            <Button onClick={() => updateWizardData({ step: 2 })} disabled={wizardData.nucleusIds.length === 0}>
              Comenzar
            </Button>
          </div>
        </div>
      )}

      {wizardData.step === 2 && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold">Fechas</h2>

          <div className="space-y-2">
            <Label>Tiempo de duración</Label>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Inicio</Label>
                <Input
                  type="date"
                  value={wizardData.startDate}
                  onChange={(e) => updateWizardData({ startDate: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Fin</Label>
                <Input
                  type="date"
                  value={wizardData.endDate}
                  onChange={(e) => updateWizardData({ endDate: e.target.value })}
                />
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Clases por disciplinas</Label>
            <div className="space-y-3">
              {areaSubjects.map((s) => (
                <div key={s.id} className="flex items-center justify-between">
                  <Label>{s.name}:</Label>
                  <Select
                    defaultValue="3"
                    onValueChange={(value) => {
                      const newSubjectsData = { ...wizardData.subjectsData };
                      newSubjectsData[s.id] = {
                        ...(newSubjectsData[s.id] || {}),
                        class_count: parseInt(value),
                      };
                      updateWizardData({ subjectsData: newSubjectsData });
                    }}
                  >
                    <SelectTrigger className="w-[180px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
                        <SelectItem key={n} value={n.toString()}>
                          {n} clases
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-between">
            <Button variant="outline" onClick={() => updateWizardData({ step: 1 })}>
              Atrás
            </Button>
            <Button onClick={() => updateWizardData({ step: 3 })}>Continuar</Button>
          </div>
        </div>
      )}

      {wizardData.step === 3 && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold">Asignar categorías a disciplinas</h2>
          <p className="text-sm text-muted-foreground">Arrastra las categorías a cada materia para asignarlas</p>

          <div
            className="border-2 border-dashed rounded-lg p-4 min-h-[100px]"
            onDragOver={(e) => e.preventDefault()}
            onDrop={() => handleDrop(null)}
          >
            <h4 className="font-semibold mb-2">Categorías sin asignar</h4>
            <div className="flex flex-wrap gap-2">
              {unassignedCategories.length === 0 ? (
                <span className="text-sm text-muted-foreground">Todas las categorías han sido asignadas</span>
              ) : (
                unassignedCategories.map((c) => (
                  <Badge key={c.id} draggable onDragStart={() => handleDragStart(c.id)} className="cursor-move">
                    {c.name}
                  </Badge>
                ))
              )}
            </div>
          </div>

          {areaSubjects.map((s) => {
            const subjectCats = (wizardData.subjectCategories[s.id] || [])
              .map((catId) => categories.find((c) => c.id === catId))
              .filter(Boolean);

            return (
              <div
                key={s.id}
                className="border-2 border-dashed rounded-lg p-4 min-h-[100px]"
                onDragOver={(e) => e.preventDefault()}
                onDrop={() => handleDrop(s.id)}
              >
                <h4 className="font-semibold mb-2">{s.name}</h4>
                <div className="flex flex-wrap gap-2">
                  {subjectCats.length === 0 ? (
                    <span className="text-sm text-muted-foreground">Arrastra categorías aquí</span>
                  ) : (
                    subjectCats.map((c) => (
                      <Badge
                        key={c!.id}
                        draggable
                        onDragStart={() => handleDragStart(c!.id)}
                        className="cursor-move bg-primary"
                      >
                        {c!.name}
                      </Badge>
                    ))
                  )}
                </div>
              </div>
            );
          })}

          <div className="flex justify-between">
            <Button variant="outline" onClick={() => updateWizardData({ step: 2 })}>
              Atrás
            </Button>
            <Button onClick={handleCreateDocument} disabled={unassignedCategories.length > 0}>
              Crear documento
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
