import { Home, MessageSquare, MapPin, Clock, Moon, Sun, PanelLeftClose, PanelLeftOpen, LogOut } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../../lib/auth";

export type Screen = "home" | "chat" | "pharmacy" | "history";

interface NavComponentProps {
  active: Screen;
  onNavigate: (screen: Screen) => void;
  darkMode: boolean;
  onToggleDark: () => void;
  hasChat: boolean;
}

const NAV_ITEMS: { key: Screen; label: string; Icon: React.ElementType }[] = [
  { key: "home", label: "Home", Icon: Home },
  { key: "chat", label: "Chat", Icon: MessageSquare },
  { key: "pharmacy", label: "Nearby", Icon: MapPin },
  { key: "history", label: "Records", Icon: Clock },
];

export function Sidebar({ active, onNavigate, darkMode, onToggleDark, hasChat }: NavComponentProps) {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();

  return (
    <aside className={`hidden md:flex flex-col h-screen flex-shrink-0 border-r transition-[width] duration-200 ease-in-out ${collapsed ? "w-[60px]" : "w-56"} ${darkMode ? "bg-[#09090b] border-gray-800" : "bg-white border-gray-200"}`}>
      {/* Logo */}
      <div className={`h-14 flex items-center ${collapsed ? "px-2 justify-center" : "px-4 justify-between"} border-b ${darkMode ? "border-gray-800" : "border-gray-100"}`}>
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md bg-blue-600 flex items-center justify-center flex-shrink-0">
            <span style={{ fontSize: "13px" }}>{"\u2695\ufe0f"}</span>
          </div>
          {!collapsed && <span className={`text-sm font-bold ${darkMode ? "text-white" : "text-gray-900"}`}>Pharmacare</span>}
        </div>
        {!collapsed && (
          <button onClick={() => setCollapsed(true)}
            className={`p-1 rounded ${darkMode ? "text-gray-600 hover:text-gray-400" : "text-gray-400 hover:text-gray-600"}`}>
            <PanelLeftClose className="w-4 h-4" />
          </button>
        )}
      </div>

      {collapsed && (
        <div className="px-2 py-2">
          <button onClick={() => setCollapsed(false)}
            className={`w-full flex items-center justify-center h-7 rounded ${darkMode ? "text-gray-600 hover:text-gray-400" : "text-gray-400 hover:text-gray-600"}`}>
            <PanelLeftOpen className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Nav links */}
      <nav className={`flex-1 py-2 space-y-0.5 ${collapsed ? "px-1.5" : "px-2"}`}>
        {NAV_ITEMS.map(({ key, label, Icon }) => {
          const isActive = active === key;
          const isDisabled = key === "chat" && !hasChat;
          return (
            <button key={key} onClick={() => !isDisabled && onNavigate(key)} disabled={isDisabled}
              title={collapsed ? label : undefined}
              className={`w-full flex items-center rounded-md transition-colors ${collapsed ? "justify-center px-0 py-2" : "gap-2.5 px-2.5 py-2"} ${
                isActive
                  ? darkMode ? "bg-blue-600/15 text-blue-400" : "bg-blue-50 text-blue-700"
                  : isDisabled
                    ? "text-gray-400 opacity-50 cursor-default"
                    : darkMode ? "text-gray-500 hover:bg-gray-800 hover:text-gray-300" : "text-gray-500 hover:bg-gray-50 hover:text-gray-900"
              }`}>
              <Icon className="w-4 h-4 flex-shrink-0" />
              {!collapsed && <span className="text-sm font-medium">{label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Bottom */}
      <div className={`pb-3 space-y-1 ${collapsed ? "px-1.5" : "px-2"}`}>
        <button onClick={onToggleDark}
          className={`w-full flex items-center rounded-md transition-colors ${collapsed ? "justify-center px-0 py-2" : "gap-2.5 px-2.5 py-2"} ${darkMode ? "text-gray-500 hover:bg-gray-800" : "text-gray-500 hover:bg-gray-50"}`}>
          {darkMode ? <Sun className="w-4 h-4 text-yellow-400" /> : <Moon className="w-4 h-4" />}
          {!collapsed && <span className="text-sm">{darkMode ? "Light Mode" : "Dark Mode"}</span>}
        </button>
        <button onClick={logout}
          className={`w-full flex items-center rounded-md transition-colors ${collapsed ? "justify-center px-0 py-2" : "gap-2.5 px-2.5 py-2"} ${darkMode ? "text-gray-500 hover:bg-gray-800" : "text-gray-500 hover:bg-gray-50"}`}>
          <LogOut className="w-4 h-4" />
          {!collapsed && (
            <div className="min-w-0">
              <p className="text-sm">Sign Out</p>
              {user && <p className={`text-[11px] truncate ${darkMode ? "text-gray-600" : "text-gray-400"}`}>{user.email}</p>}
            </div>
          )}
        </button>
      </div>
    </aside>
  );
}

export function MobileTopBar({ darkMode, onToggleDark }: Pick<NavComponentProps, "darkMode" | "onToggleDark">) {
  const { logout } = useAuth();
  return (
    <header className={`md:hidden flex items-center justify-between px-4 h-14 border-b flex-shrink-0 ${darkMode ? "bg-[#09090b] border-gray-800" : "bg-white border-gray-200"}`}>
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded-md bg-blue-600 flex items-center justify-center">
          <span style={{ fontSize: "11px" }}>{"\u2695\ufe0f"}</span>
        </div>
        <span className={`text-sm font-bold ${darkMode ? "text-white" : "text-gray-900"}`}>Pharmacare</span>
      </div>
      <div className="flex items-center gap-1.5">
        <button onClick={onToggleDark}
          className={`w-8 h-8 rounded-md flex items-center justify-center ${darkMode ? "text-yellow-400" : "text-gray-500"}`}>
          {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
        <button onClick={logout}
          className={`w-8 h-8 rounded-md flex items-center justify-center ${darkMode ? "text-gray-500" : "text-gray-400"}`}>
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}

export function BottomNav({ active, onNavigate, darkMode, hasChat }: Omit<NavComponentProps, "onToggleDark">) {
  return (
    <nav className={`md:hidden flex items-center justify-around h-14 border-t flex-shrink-0 ${darkMode ? "bg-[#09090b] border-gray-800" : "bg-white border-gray-200"}`}>
      {NAV_ITEMS.map(({ key, label, Icon }) => {
        const isActive = active === key;
        const isDisabled = key === "chat" && !hasChat;
        return (
          <button key={key} onClick={() => !isDisabled && onNavigate(key)} disabled={isDisabled}
            className={`flex flex-col items-center justify-center min-w-[44px] min-h-[44px] px-2 transition-colors ${
              isActive ? "text-blue-600" : isDisabled ? "text-gray-300" : darkMode ? "text-gray-500" : "text-gray-400"
            }`}>
            <Icon className="w-4.5 h-4.5" />
            <span className="text-[10px] mt-0.5 font-medium">{label}</span>
          </button>
        );
      })}
    </nav>
  );
}
