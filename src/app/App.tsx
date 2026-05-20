import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { OnboardingScreen } from "./components/OnboardingScreen";
import { ChatScreen } from "./components/ChatScreen";
import { PharmacyScreen } from "./components/PharmacyScreen";
import { HistoryScreen } from "./components/HistoryScreen";
import { NavBar, type Screen } from "./components/NavBar";

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [screen, setScreen] = useState<Screen>("home");
  const [currentSymptom, setCurrentSymptom] = useState("");
  const [hasStartedChat, setHasStartedChat] = useState(false);

  const handleStartChat = (symptom: string) => {
    setCurrentSymptom(symptom);
    setHasStartedChat(true);
    setScreen("chat");
  };

  return (
    <div
      className={`min-h-screen w-full ${darkMode ? "bg-gray-950" : "bg-gray-50"}`}
      style={{ fontFamily: "'Inter', system-ui, -apple-system, sans-serif" }}
    >
      {/* Sticky top navbar */}
      <NavBar
        active={screen}
        onNavigate={setScreen}
        darkMode={darkMode}
        onToggleDark={() => setDarkMode((v) => !v)}
        hasChat={hasStartedChat}
      />

      {/* Main content */}
      <main>
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
    </div>
  );
}
