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
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
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
    <div className={`flex h-screen w-screen overflow-hidden ${darkMode ? "bg-[#09090b]" : "bg-[#fafafa]"}`}>
      <Sidebar
        active={screen}
        onNavigate={setScreen}
        darkMode={darkMode}
        onToggleDark={() => setDarkMode((v) => !v)}
        hasChat={hasStartedChat}
      />

      <div className="flex-1 min-w-0 overflow-hidden flex flex-col">
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
