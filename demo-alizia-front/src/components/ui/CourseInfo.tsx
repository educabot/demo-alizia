import { GraduationCap, Calendar, ArrowRight } from 'lucide-react';

interface CourseInfoField {
  label: string;
  value: string;
}

interface CourseInfoProps {
  fields: CourseInfoField[];
  showSchedule?: boolean;
  onScheduleClick?: () => void;
}

export function CourseInfo({ fields, showSchedule = true, onScheduleClick }: CourseInfoProps) {
  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-4">
          <GraduationCap className="text-[#10182B]" />
          <h2 className="headline-emphasized text-[#10182B]">Sobre el curso</h2>
        </div>

        <div className="fill-primary backdrop-blur-sm border-slate-200 rounded-2xl p-6">
          <div className="space-y-4">
            {fields.map((field, index) => (
              <div key={index} className={index < fields.length - 1 ? 'pb-4 border-b border-slate-200' : ''}>
                <p className="headline-2-semi-bold text-foreground mb-1">{field.label}</p>
                <p className="body-2-regular text-foreground">{field.value}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {showSchedule && (
        <div
          className="fill-primary backdrop-blur-sm border-slate-200 rounded-2xl p-6 cursor-pointer activity-card-shadow transition-all group"
          onClick={onScheduleClick}
        >
          <div className="flex items-center justify-between">
            <h2 className=" text-foreground flex gap-2">
              <Calendar className="w-5 h-5 text-[#10182B]" />
              Grilla de horarios
            </h2>
            <ArrowRight className="w-5 h-5 text-foreground group-hover:translate-x-1 transition-transform" />
          </div>
        </div>
      )}
    </div>
  );
}
