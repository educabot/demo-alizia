import { useNavigate } from 'react-router-dom';
import { useStore } from '@/store/useStore';
import { LogOut } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { TabsCustom, TabsCustomList, TabsCustomTrigger } from '@/components/ui/tabs-custom';

export function Header() {
  const navigate = useNavigate();
  const currentUser = useStore((state) => state.currentUser);
  const setCurrentUser = useStore((state) => state.setCurrentUser);
  const avatar = currentUser?.name.charAt(0).toUpperCase() || 'U';

  const handleLogout = () => {
    setCurrentUser(null);
    navigate('/login');
  };

  return (
    <header className="fixed top-0 left-0 w-full h-16 py-6 px-4 border-b border-primary/15 flex items-center justify-between z-20 backdrop-blur-sm">
      <div className="h-full flex items-center gap-4">
        <img
          src="https://storage.googleapis.com/content-generator-ia/ANIMACION%20TRANSPARENTE%203.gif"
          alt="alizia logo by educabot"
          className="w-46 object-contain will-change-auto image-render-pixelated"
        />
      </div>
      <div className="flex items-center gap-4">
        <TabsCustom defaultValue="docente" className="max-w-[10.3rem] w-full">
          <TabsCustomList className="p-1">
            <TabsCustomTrigger value="docente">Docente</TabsCustomTrigger>
            <TabsCustomTrigger value="aula">Aula</TabsCustomTrigger>
          </TabsCustomList>
        </TabsCustom>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="w-9 h-9 rounded-full bg-[#735fe3] text-primary-foreground flex items-center justify-center shrink-0 hover:bg-primary/90 transition-colors cursor-pointer">
              {avatar}
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <div className="px-2 py-1.5">
              <p className="body-2-medium">{currentUser?.name}</p>
              <p className="callout-regular text-muted-foreground">{currentUser?.email}</p>
            </div>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={handleLogout}
              className="cursor-pointer hover:bg-[#735fe3]! hover:text-white! focus:bg-[#735fe3]! focus:text-white!"
            >
              <LogOut className="mr-2 h-4 w-4" />
              <span>Cerrar sesión</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
