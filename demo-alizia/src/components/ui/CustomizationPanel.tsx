import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Textarea } from '@/components/ui/textarea';
import { FontSelector } from '@/components/ui/FontSelector';
import type { Font } from '@/types';
import { cn } from '@/lib/utils';

interface CustomizationPanelProps {
  customInstruction: string;
  onCustomInstructionChange: (value: string) => void;
  resourcesMode: 'global' | 'per_moment';
  onResourcesModeChange: (mode: 'global' | 'per_moment') => void;
  globalFontId: number | null;
  onGlobalFontChange: (fontId: number | null) => void;
  momentFontIds: { apertura: number | null; desarrollo: number | null; cierre: number | null };
  onMomentFontChange: (moment: 'apertura' | 'desarrollo' | 'cierre', fontId: number | null) => void;
  fonts: Font[];
}

export function CustomizationPanel({
  customInstruction,
  onCustomInstructionChange,
  resourcesMode,
  onResourcesModeChange,
  globalFontId,
  onGlobalFontChange,
  momentFontIds,
  onMomentFontChange,
  fonts,
}: CustomizationPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const momentLabels = {
    apertura: 'Apertura/Motivacion',
    desarrollo: 'Desarrollo/Construccion',
    cierre: 'Cierre/Metacognicion',
  };

  return (
    <div className="activity-card-bg rounded-2xl overflow-hidden">
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50/50 transition-colors"
      >
        <span className="body-1-medium text-secondary-foreground">Personalizar clase (opcional)</span>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-muted-foreground" />
        ) : (
          <ChevronDown className="w-5 h-5 text-muted-foreground" />
        )}
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 space-y-6">
          {/* Instruction textarea */}
          <div className="space-y-2">
            <label className="body-2-medium text-secondary-foreground">Instrucciones adicionales</label>
            <Textarea
              value={customInstruction}
              onChange={(e) => onCustomInstructionChange(e.target.value)}
              placeholder="Agrega instrucciones especificas para esta clase (ej: 'Enfocarse en ejemplos practicos', 'Incluir actividad grupal')..."
              className="min-h-[80px] resize-none"
            />
          </div>

          {/* Resources section */}
          <div className="space-y-3">
            <label className="body-2-medium text-secondary-foreground">Recursos validados</label>

            {/* Toggle for global vs per moment */}
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => onResourcesModeChange('global')}
                className={cn(
                  'px-3 py-1.5 text-sm rounded-lg transition-colors cursor-pointer',
                  resourcesMode === 'global'
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                )}
              >
                Para toda la clase
              </button>
              <button
                type="button"
                onClick={() => onResourcesModeChange('per_moment')}
                className={cn(
                  'px-3 py-1.5 text-sm rounded-lg transition-colors cursor-pointer',
                  resourcesMode === 'per_moment'
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                )}
              >
                Por momento
              </button>
            </div>

            {/* Font selectors */}
            {resourcesMode === 'global' ? (
              <FontSelector
                fonts={fonts}
                selectedFontId={globalFontId}
                onSelect={onGlobalFontChange}
              />
            ) : (
              <div className="space-y-4">
                {(['apertura', 'desarrollo', 'cierre'] as const).map((moment) => (
                  <div key={moment} className="space-y-2">
                    <p className="text-sm font-medium text-[#10182B]">{momentLabels[moment]}</p>
                    <FontSelector
                      fonts={fonts}
                      selectedFontId={momentFontIds[moment]}
                      onSelect={(fontId) => onMomentFontChange(moment, fontId)}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
