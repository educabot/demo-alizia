import { EllipsisVertical, Users } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

interface Student {
  id: number;
  name: string;
}

interface StudentsListProps {
  students: Student[];
  isLoading?: boolean;
  showActions?: boolean;
}

const getInitials = (name: string) => {
  const parts = name.split(' ');
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return name.substring(0, 2).toUpperCase();
};

const getAvatarColor = () => {
  return 'bg-violet-200 text-violet-700';
};

export function StudentsList({ students, isLoading = false, showActions = true }: StudentsListProps) {
  return (
    <div className="lg:col-span-2">
      <div className="flex items-center gap-2 mb-4">
        <Users className="text-[#10182B]" />
        <h2 className="headline-emphasized text-[#10182B]">Alumnos</h2>
        <span className="body-1-regular text-muted-foreground">({students.length})</span>
      </div>

      <div className="activity-card-bg backdrop-blur-sm border-slate-200 rounded-2xl p-4 py-5">
        <div className="space-y-4">
          {isLoading ? (
            Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="flex items-center justify-between p-4">
                <div className="flex items-center gap-3">
                  <Skeleton className="w-10 h-10 rounded-full" />
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-3 w-40" />
                  </div>
                </div>
                {showActions && <Skeleton className="w-5 h-5" />}
              </div>
            ))
          ) : students.length === 0 ? (
            <p className="body-2-regular text-muted-foreground">No hay alumnos registrados</p>
          ) : (
            students.map((student) => (
              <div
                key={student.id}
                className="flex items-center justify-between p-4 bg-[#FFFFFF4D] rounded-xl cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${getAvatarColor()}`}
                  >
                    {getInitials(student.name)}
                  </div>
                  <div>
                    <p className="body-1-medium text-foreground">{student.name}</p>
                    <p className="callout-regular text-muted-foreground">
                      {student.name.toLowerCase().replace(/\s+/g, '')}@Gmail.Com
                    </p>
                  </div>
                </div>
                {showActions && (
                  <button className="text-muted-foreground hover:text-foreground">
                    <EllipsisVertical />
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
