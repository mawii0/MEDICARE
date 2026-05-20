import { useState } from "react";
import { Home, MessageSquare, MapPin, Clock, Pill, Moon, Sun, Menu, X } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

export type Screen = "home" | "chat" | "pharmacy" | "history";

interface NavBarProps {
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

export function NavBar({ active, onNavigate, darkMode, onToggleDark, hasChat }: NavBarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav
      className={`sticky top-0 z-50 w-full border-b backdrop-blur-md ${
        darkMode
          ? "bg-gray-900/95 border-gray-800"
          : "bg-white/95 border-gray-100"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <div className="w-9 h-9 rounded-xl bg-blue-500 flex items-center justify-center shadow-md">
              <Pill className="w-4.5 h-4.5 text-white" style={{ width: "18px", height: "18px" }} />
            </div>
            <div>
              <p
                className={`${darkMode ? "text-white" : "text-blue-900"}`}
                style={{ fontSize: "17px", fontWeight: 700, lineHeight: 1.2 }}
              >
                MediGuide
              </p>
              <p
                className={`${darkMode ? "text-blue-400" : "text-blue-500"}`}
                style={{ fontSize: "10px" }}
              >
                AI Pharmaceutical Assistant
              </p>
            </div>
          </div>

          {/* Desktop nav links */}
          <div className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map(({ key, label, Icon }) => {
              const isActive = active === key;
              const isDisabled = key === "chat" && !hasChat;
              return (
                <button
                  key={key}
                  onClick={() => !isDisabled && onNavigate(key)}
                  disabled={isDisabled}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all ${
                    isActive
                      ? darkMode
                        ? "bg-blue-600/20 text-blue-400"
                        : "bg-blue-50 text-blue-700"
                      : isDisabled
                        ? "opacity-40 cursor-default"
                        : darkMode
                          ? "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
                          : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  }`}
                  style={{ fontSize: "14px", fontWeight: isActive ? 600 : 400 }}
                >
                  <Icon style={{ width: "16px", height: "16px" }} />
                  {label}
                </button>
              );
            })}
          </div>

          {/* Right side: dark mode toggle + mobile hamburger */}
          <div className="flex items-center gap-2">
            <button
              onClick={onToggleDark}
              className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all ${
                darkMode
                  ? "bg-gray-800 text-yellow-300 hover:bg-gray-700"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {darkMode ? (
                <Sun style={{ width: "16px", height: "16px" }} />
              ) : (
                <Moon style={{ width: "16px", height: "16px" }} />
              )}
            </button>

            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen((v) => !v)}
              className={`md:hidden w-9 h-9 rounded-xl flex items-center justify-center transition-all ${
                darkMode
                  ? "bg-gray-800 text-gray-300 hover:bg-gray-700"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {mobileMenuOpen ? (
                <X style={{ width: "18px", height: "18px" }} />
              ) : (
                <Menu style={{ width: "18px", height: "18px" }} />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile dropdown menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className={`md:hidden overflow-hidden border-t ${
              darkMode ? "border-gray-800" : "border-gray-100"
            }`}
          >
            <div className="px-4 py-3 space-y-1">
              {NAV_ITEMS.map(({ key, label, Icon }) => {
                const isActive = active === key;
                const isDisabled = key === "chat" && !hasChat;
                return (
                  <button
                    key={key}
                    onClick={() => {
                      if (!isDisabled) {
                        onNavigate(key);
                        setMobileMenuOpen(false);
                      }
                    }}
                    disabled={isDisabled}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                      isActive
                        ? darkMode
                          ? "bg-blue-600/20 text-blue-400"
                          : "bg-blue-50 text-blue-700"
                        : isDisabled
                          ? "opacity-40 cursor-default"
                          : darkMode
                            ? "text-gray-400 hover:bg-gray-800"
                            : "text-gray-600 hover:bg-gray-50"
                    }`}
                  >
                    <div
                      className={`w-9 h-9 rounded-lg flex items-center justify-center ${
                        isActive
                          ? darkMode
                            ? "bg-blue-600/30"
                            : "bg-blue-100"
                          : darkMode
                            ? "bg-gray-800"
                            : "bg-gray-100"
                      }`}
                    >
                      <Icon style={{ width: "18px", height: "18px" }} />
                    </div>
                    <span style={{ fontSize: "15px", fontWeight: isActive ? 600 : 400 }}>
                      {label}
                    </span>
                  </button>
                );
              })}

              {/* Disclaimer */}
              <div
                className={`mt-3 px-4 py-3 rounded-xl ${
                  darkMode
                    ? "bg-amber-950/40 border border-amber-800/30"
                    : "bg-amber-50 border border-amber-100"
                }`}
              >
                <p
                  className={`${darkMode ? "text-amber-400" : "text-amber-700"}`}
                  style={{ fontSize: "11px", lineHeight: 1.5 }}
                >
                  Not a substitute for professional medical advice.
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
