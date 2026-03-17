import { useState } from 'react';
import { Check, FileText } from 'lucide-react';
import type { Font } from '@/types';
import { cn } from '@/lib/utils';

interface FontSelectorProps {
  fonts: Font[];
  selectedFontId: number | null;
  onSelect: (fontId: number | null) => void;
  label?: string;
}

function FontThumbnail({ font }: { font: Font }) {
  const [hasError, setHasError] = useState(false);

  if (!font.thumbnail_url || hasError) {
    return <FileText className="w-5 h-5 text-[#324155]" />;
  }

  return (
    <img
      src={font.thumbnail_url}
      alt={font.name}
      className="w-full h-full object-cover rounded-lg"
      onError={() => setHasError(true)}
    />
  );
}

export function FontSelector({ fonts, selectedFontId, onSelect, label }: FontSelectorProps) {
  const handleClick = (fontId: number) => {
    if (selectedFontId === fontId) {
      onSelect(null);
    } else {
      onSelect(fontId);
    }
  };

  if (fonts.length === 0) {
    return (
      <div className="text-sm text-muted-foreground italic">
        No hay recursos disponibles para esta área.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {label && <p className="body-2-medium text-secondary-foreground">{label}</p>}
      <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto pr-1">
        {fonts.map((font) => (
          <button
            key={font.id}
            type="button"
            onClick={() => handleClick(font.id)}
            className={cn(
              'flex items-center gap-3 p-3 rounded-xl border text-left transition-all cursor-pointer',
              selectedFontId === font.id
                ? 'border-primary bg-primary/5'
                : 'border-gray-200 hover:border-gray-300 bg-white'
            )}
          >
            <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0 overflow-hidden">
              <FontThumbnail font={font} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-[#10182B] truncate">{font.name}</p>
              {font.description && (
                <p className="text-xs text-muted-foreground line-clamp-1">{font.description}</p>
              )}
            </div>
            {selectedFontId === font.id && (
              <div className="w-5 h-5 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                <Check className="w-3 h-3 text-white" />
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
