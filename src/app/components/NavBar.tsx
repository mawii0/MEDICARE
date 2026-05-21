import {
  Home,
  MessageSquare,
  MapPin,
  Clock,
  Pill,
  Moon,
  Sun,
  AlertTriangle,
  PanelLeftClose,
  PanelLeftOpen,
  LogOut,
} from "lucide-react";
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

const NAV_ITEMS: {
  key: Screen;
  label: string;
  subdescription: string;
  Icon: React.ElementType;
}[] = [
  { key: "home", label: "Home", subdescription: "Symptom checker", Icon: Home },
  {
    key: "chat",
    label: "Chat",
    subdescription: "AI recommendations",
    Icon: MessageSquare,
  },
  {
    key: "pharmacy",
    label: "Nearby",
    subdescription: "Find pharmacies",
    Icon: MapPin,
  },
  {
    key: "history",
    label: "Records",
    subdescription: "Health history",
    Icon: Clock,
  },
];

export function Sidebar({
  active,
  onNavigate,
  darkMode,
  onToggleDark,
  hasChat,
}: NavComponentProps) {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();

  return (
    <aside
      className={`hidden md:flex flex-col h-screen flex-shrink-0 border-r transition-[width] duration-200 ease-in-out ${
        collapsed ? "w-[68px]" : "w-64"
      } ${
        darkMode
          ? "bg-gray-900 border-gray-800"
          : "bg-white border-gray-200"
      }`}
    >
      {/* Logo area + collapse toggle */}
      <div className={`pt-6 pb-4 flex items-start ${collapsed ? "px-2 justify-center" : "px-5 justify-between"}`}>
        <div className={`flex items-center ${collapsed ? "justify-center" : "gap-3"}`}>
          <div className="w-10 h-10 rounded-xl bg-blue-500 flex items-center justify-center shadow-md flex-shrink-0">
            <Pill className="w-5 h-5 text-white" />
          </div>
          {!collapsed && (
            <div>
              <p
                className={`text-[17px] font-bold leading-tight ${
                  darkMode ? "text-white" : "text-blue-900"
                }`}
              >
                MediGuide
              </p>
              <p
                className={`text-[10px] ${
                  darkMode ? "text-blue-400" : "text-blue-500"
                }`}
              >
                AI Pharmaceutical Assistant
              </p>
            </div>
          )}
        </div>
        {!collapsed && (
          <button
            onClick={() => setCollapsed(true)}
            className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 transition-all ${
              darkMode
                ? "text-gray-500 hover:bg-gray-800 hover:text-gray-300"
                : "text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            }`}
          >
            <PanelLeftClose className="w-[16px] h-[16px]" />
          </button>
        )}
      </div>

      {/* Expand button when collapsed */}
      {collapsed && (
        <div className="px-2 pb-2">
          <button
            onClick={() => setCollapsed(false)}
            className={`w-full flex items-center justify-center h-8 rounded-lg transition-all ${
              darkMode
                ? "text-gray-500 hover:bg-gray-800 hover:text-gray-300"
                : "text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            }`}
          >
            <PanelLeftOpen className="w-[16px] h-[16px]" />
          </button>
        </div>
      )}

      {/* Nav links */}
      <nav className={`flex-1 py-2 space-y-1 ${collapsed ? "px-2" : "px-3"}`}>
        {NAV_ITEMS.map(({ key, label, subdescription, Icon }) => {
          const isActive = active === key;
          const isDisabled = key === "chat" && !hasChat;
          return (
            <button
              key={key}
              onClick={() => !isDisabled && onNavigate(key)}
              disabled={isDisabled}
              title={collapsed ? label : undefined}
              className={`relative w-full flex items-center rounded-lg transition-all text-left ${
                collapsed ? "justify-center px-0 py-2.5" : "gap-3 px-3 py-2.5"
              } ${
                isActive
                  ? darkMode
                    ? "bg-blue-600/20 text-blue-400"
                    : "bg-blue-50 text-blue-700"
                  : isDisabled
                    ? darkMode
                      ? "text-gray-400 opacity-70 cursor-default"
                      : "text-gray-500 opacity-60 cursor-default"
                    : darkMode
                      ? "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              }`}
            >
              {/* Active accent bar */}
              {isActive && (
                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-[3px] h-6 rounded-l-full bg-blue-500" />
              )}
              <div
                className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${
                  isActive
                    ? darkMode
                      ? "bg-blue-600/30"
                      : "bg-blue-100"
                    : darkMode
                      ? "bg-gray-800"
                      : "bg-gray-100"
                }`}
              >
                <Icon className="w-[18px] h-[18px]" />
              </div>
              {!collapsed && (
                <div className="min-w-0">
                  <p
                    className="text-sm leading-tight"
                    style={{ fontWeight: isActive ? 600 : 400 }}
                  >
                    {label}
                  </p>
                  <p
                    className={`text-[11px] leading-tight mt-0.5 ${
                      darkMode ? "text-gray-500" : "text-gray-400"
                    }`}
                  >
                    {subdescription}
                  </p>
                </div>
              )}
            </button>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className={`pb-4 space-y-3 ${collapsed ? "px-2" : "px-3"}`}>
        {/* Dark mode toggle */}
        <button
          onClick={onToggleDark}
          title={collapsed ? (darkMode ? "Light Mode" : "Dark Mode") : undefined}
          className={`w-full flex items-center rounded-lg transition-all ${
            collapsed ? "justify-center px-0 py-2.5" : "gap-3 px-3 py-2.5"
          } ${
            darkMode
              ? "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
              : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
          }`}
        >
          <div
            className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${
              darkMode ? "bg-gray-800" : "bg-gray-100"
            }`}
          >
            {darkMode ? (
              <Sun className="w-[18px] h-[18px] text-yellow-300" />
            ) : (
              <Moon className="w-[18px] h-[18px]" />
            )}
          </div>
          {!collapsed && (
            <span className="text-sm">
              {darkMode ? "Light Mode" : "Dark Mode"}
            </span>
          )}
        </button>

        {/* Logout button */}
        <button
          onClick={logout}
          title={collapsed ? "Sign Out" : undefined}
          className={`w-full flex items-center rounded-lg transition-all ${
            collapsed ? "justify-center px-0 py-2.5" : "gap-3 px-3 py-2.5"
          } ${
            darkMode
              ? "text-gray-500 hover:bg-red-900/20 hover:text-red-400"
              : "text-gray-500 hover:bg-red-50 hover:text-red-600"
          }`}
        >
          <div
            className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${
              darkMode ? "bg-gray-800" : "bg-gray-100"
            }`}
          >
            <LogOut className="w-[18px] h-[18px]" />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="text-sm leading-tight">Sign Out</p>
              {user && (
                <p className={`text-[11px] leading-tight mt-0.5 truncate ${darkMode ? "text-gray-500" : "text-gray-400"}`}>
                  {user.email}
                </p>
              )}
            </div>
          )}
        </button>

        {/* Disclaimer — hidden when collapsed */}
        {!collapsed && (
          <div
            className={`px-3 py-2.5 rounded-lg ${
              darkMode
                ? "bg-amber-950/40 border border-amber-800/30"
                : "bg-amber-50 border border-amber-200"
            }`}
          >
            <div className="flex items-start gap-2">
              <AlertTriangle
                className={`w-3.5 h-3.5 mt-0.5 flex-shrink-0 ${
                  darkMode ? "text-amber-400" : "text-amber-500"
                }`}
              />
              <p
                className={`text-[11px] leading-relaxed ${
                  darkMode ? "text-amber-400" : "text-amber-700"
                }`}
              >
                Not a substitute for professional medical advice.
              </p>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}

export function MobileTopBar({
  darkMode,
  onToggleDark,
}: Pick<NavComponentProps, "darkMode" | "onToggleDark">) {
  const { logout } = useAuth();

  return (
    <header
      className={`md:hidden flex items-center justify-between px-4 h-14 border-b flex-shrink-0 ${
        darkMode
          ? "bg-gray-900 border-gray-800"
          : "bg-white border-gray-200"
      }`}
    >
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center shadow-sm">
          <Pill className="w-4 h-4 text-white" />
        </div>
        <p
          className={`text-[15px] font-bold ${
            darkMode ? "text-white" : "text-blue-900"
          }`}
        >
          MediGuide
        </p>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={onToggleDark}
          className={`w-9 h-9 rounded-lg flex items-center justify-center transition-all ${
            darkMode
              ? "bg-gray-800 text-yellow-300"
              : "bg-gray-100 text-gray-600"
          }`}
        >
          {darkMode ? (
            <Sun className="w-[16px] h-[16px]" />
          ) : (
            <Moon className="w-[16px] h-[16px]" />
          )}
        </button>
        <button
          onClick={logout}
          className={`w-9 h-9 rounded-lg flex items-center justify-center transition-all ${
            darkMode
              ? "bg-gray-800 text-gray-400 hover:text-red-400"
              : "bg-gray-100 text-gray-500 hover:text-red-600"
          }`}
        >
          <LogOut className="w-[16px] h-[16px]" />
        </button>
      </div>
    </header>
  );
}

export function BottomNav({
  active,
  onNavigate,
  darkMode,
  hasChat,
}: Omit<NavComponentProps, "onToggleDark">) {
  return (
    <nav
      className={`md:hidden flex items-center justify-around h-16 border-t flex-shrink-0 ${
        darkMode
          ? "bg-gray-900 border-gray-800"
          : "bg-white border-gray-200"
      }`}
    >
      {NAV_ITEMS.map(({ key, label, Icon }) => {
        const isActive = active === key;
        const isDisabled = key === "chat" && !hasChat;
        return (
          <button
            key={key}
            onClick={() => !isDisabled && onNavigate(key)}
            disabled={isDisabled}
            className={`flex flex-col items-center justify-center min-w-[44px] min-h-[44px] px-2 transition-all ${
              isActive
                ? "text-blue-500"
                : isDisabled
                  ? darkMode
                    ? "text-gray-400 opacity-60"
                    : "text-gray-400 opacity-50"
                  : darkMode
                    ? "text-gray-500"
                    : "text-gray-400"
            }`}
          >
            <Icon className="w-5 h-5" />
            <span className="text-[10px] mt-1 font-medium">{label}</span>
          </button>
        );
      })}
    </nav>
  );
}
