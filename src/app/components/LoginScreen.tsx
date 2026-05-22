import { useState } from "react";
import { Mail, Lock, User, Eye, EyeOff, ArrowRight } from "lucide-react";
import { useAuth } from "../../lib/auth";

export function LoginScreen({ darkMode }: { darkMode: boolean }) {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await register(email, password, name);
      } else {
        await login(email, password);
      }
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`min-h-screen flex ${darkMode ? "bg-[#09090b]" : "bg-[#fafafa]"}`}>
      {/* Left panel - branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-blue-600 items-center justify-center p-12">
        <div className="max-w-md">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center">
              <span style={{ fontSize: "20px" }}>{"\u2695\ufe0f"}</span>
            </div>
            <span className="text-white text-xl font-bold">Pharmacare</span>
          </div>
          <h1 className="text-white text-4xl font-bold leading-tight mb-4">
            Your AI-Powered Pharmaceutical Assistant
          </h1>
          <p className="text-blue-100 text-lg leading-relaxed">
            Get instant medicine recommendations with dosages, prices, and availability at Philippine pharmacies. Powered by a fine-tuned language model.
          </p>
          <div className="mt-10 flex items-center gap-4">
            <div className="flex -space-x-2">
              {["bg-blue-400", "bg-blue-300", "bg-blue-200"].map((c, i) => (
                <div key={i} className={`w-8 h-8 rounded-full ${c} border-2 border-blue-600 flex items-center justify-center text-xs text-blue-800 font-bold`}>
                  {String.fromCharCode(65 + i)}
                </div>
              ))}
            </div>
            <p className="text-blue-100 text-sm">Trusted by students and professionals</p>
          </div>
        </div>
      </div>

      {/* Right panel - form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-10 lg:hidden">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <span style={{ fontSize: "16px" }}>{"\u2695\ufe0f"}</span>
            </div>
            <span className={`text-lg font-bold ${darkMode ? "text-white" : "text-gray-900"}`}>Pharmacare</span>
          </div>

          <h2 className={`text-2xl font-bold mb-1 ${darkMode ? "text-white" : "text-gray-900"}`}>
            {mode === "login" ? "Welcome back" : "Create an account"}
          </h2>
          <p className={`text-sm mb-8 ${darkMode ? "text-gray-400" : "text-gray-500"}`}>
            {mode === "login" ? "Sign in to continue to Pharmacare" : "Get started with Pharmacare"}
          </p>

          {/* Tab switcher */}
          <div className={`flex rounded-lg p-0.5 mb-6 border ${darkMode ? "bg-gray-900 border-gray-800" : "bg-gray-100 border-gray-200"}`}>
            {(["login", "register"] as const).map((tab) => (
              <button key={tab} onClick={() => { setMode(tab); setError(""); }}
                className={`flex-1 py-2 rounded-md text-sm font-medium transition-all ${
                  mode === tab
                    ? "bg-blue-600 text-white"
                    : darkMode ? "text-gray-400 hover:text-gray-300" : "text-gray-500 hover:text-gray-700"
                }`}>
                {tab === "login" ? "Sign In" : "Create Account"}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === "register" && (
              <div>
                <label className={`block text-xs font-medium mb-1.5 ${darkMode ? "text-gray-400" : "text-gray-500"}`}>Full name</label>
                <div className="relative">
                  <User className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${darkMode ? "text-gray-500" : "text-gray-400"}`} />
                  <input type="text" placeholder="Juan Dela Cruz" value={name} onChange={(e) => setName(e.target.value)} required
                    className={`w-full pl-10 pr-4 py-2.5 rounded-lg text-sm border ${darkMode ? "bg-gray-900 border-gray-800 text-white placeholder-gray-600" : "bg-white border-gray-200 text-gray-900 placeholder-gray-400"} focus:outline-none focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600`} />
                </div>
              </div>
            )}

            <div>
              <label className={`block text-xs font-medium mb-1.5 ${darkMode ? "text-gray-400" : "text-gray-500"}`}>Email</label>
              <div className="relative">
                <Mail className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${darkMode ? "text-gray-500" : "text-gray-400"}`} />
                <input type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required
                  className={`w-full pl-10 pr-4 py-2.5 rounded-lg text-sm border ${darkMode ? "bg-gray-900 border-gray-800 text-white placeholder-gray-600" : "bg-white border-gray-200 text-gray-900 placeholder-gray-400"} focus:outline-none focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600`} />
              </div>
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1.5 ${darkMode ? "text-gray-400" : "text-gray-500"}`}>Password</label>
              <div className="relative">
                <Lock className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${darkMode ? "text-gray-500" : "text-gray-400"}`} />
                <input type={showPassword ? "text" : "password"} placeholder="Min. 6 characters" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6}
                  className={`w-full pl-10 pr-10 py-2.5 rounded-lg text-sm border ${darkMode ? "bg-gray-900 border-gray-800 text-white placeholder-gray-600" : "bg-white border-gray-200 text-gray-900 placeholder-gray-400"} focus:outline-none focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600`} />
                <button type="button" onClick={() => setShowPassword(v => !v)}
                  className={`absolute right-3 top-1/2 -translate-y-1/2 ${darkMode ? "text-gray-500" : "text-gray-400"}`}>
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="px-3 py-2 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
                {error}
              </div>
            )}

            <button type="submit" disabled={loading}
              className="w-full py-2.5 rounded-lg bg-blue-600 text-white text-sm font-medium flex items-center justify-center gap-2 hover:bg-blue-700 disabled:opacity-50 transition-colors">
              {loading ? "Please wait..." : mode === "login" ? "Sign In" : "Create Account"}
              {!loading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          <p className={`mt-8 text-center text-xs ${darkMode ? "text-gray-600" : "text-gray-400"}`}>
            For educational purposes only. Not a substitute for professional medical advice.
          </p>
        </div>
      </div>
    </div>
  );
}
