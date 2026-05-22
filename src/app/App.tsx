import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { AuthProvider, useAuth } from "../lib/auth";
import { LoginScreen } from "./components/LoginScreen";
import { OnboardingScreen } from "./components/OnboardingScreen";
import { ChatScreen, type Message } from "./components/ChatScreen";
import { PharmacyScreen } from "./components/PharmacyScreen";
import { HistoryScreen } from "./components/HistoryScreen";
import { Sidebar, BottomNav, MobileTopBar, type Screen } from "./components/NavBar";

function AppContent() {
  const { user, loading } = useAuth();
  const [darkMode, setDarkMode] = useState(false);
  const [screen, setScreen] = useState<Screen>("home");
  const [currentSymptom, setCurrentSymptom] = useState("");
  const [hasStartedChat, setHasStartedChat] = useState(false);
  const [chatMessages, setChatMessages] = useState<Message[]>([]);
  const [autoSentSymptom, setAutoSentSymptom] = useState<string | null>(null);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-slate-100">
        <div className="w-8 h-8 border-3 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <LoginScreen darkMode={darkMode} />;
  }

  const handleStartChat = (symptom: string) => {
    setCurrentSymptom(symptom);
    setHasStartedChat(true);
    setScreen("chat");
  };

  return (
    <div className={`relative flex h-screen w-screen overflow-hidden ${darkMode ? "bg-[#09090b]" : "bg-[#fafafa]"}`}>
      <div className={`pointer-events-none absolute inset-0 ${darkMode ? "bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.12),transparent_35%),radial-gradient(circle_at_bottom_right,rgba(59,130,246,0.08),transparent_30%)]" : "bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.12),transparent_35%),radial-gradient(circle_at_bottom_right,rgba(14,165,233,0.08),transparent_30%)]"}`} />
      <Sidebar
        active={screen}
        onNavigate={setScreen}
        darkMode={darkMode}
        onToggleDark={() => setDarkMode((v) => !v)}
        hasChat={hasStartedChat}
      />

      <div className="relative z-10 flex-1 min-w-0 overflow-hidden flex flex-col">
        <MobileTopBar
          darkMode={darkMode}
          onToggleDark={() => setDarkMode((v) => !v)}
        />

        <main className="flex-1 overflow-y-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={screen}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.18, ease: "easeInOut" }}
            >
              {screen === "home" && (
                <OnboardingScreen onStart={handleStartChat} darkMode={darkMode} />
              )}
              {screen === "chat" && (
                <ChatScreen
                  initialSymptom={currentSymptom}
                  darkMode={darkMode}
                  onNavigateToPharmacy={() => setScreen("pharmacy")}
                  messages={chatMessages}
                  setMessages={setChatMessages}
                  autoSentSymptom={autoSentSymptom}
                  onAutoSentSymptom={setAutoSentSymptom}
                />
              )}
              {screen === "pharmacy" && (
                <PharmacyScreen darkMode={darkMode} />
              )}
              {screen === "history" && (
                <HistoryScreen darkMode={darkMode} />
              )}
            </motion.div>
          </AnimatePresence>
        </main>

        <BottomNav
          active={screen}
          onNavigate={setScreen}
          darkMode={darkMode}
          hasChat={hasStartedChat}
        />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
