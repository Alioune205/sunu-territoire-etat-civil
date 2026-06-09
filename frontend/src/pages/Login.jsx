// src/pages/Login.jsx
import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { toast } from '@/components/ui/use-toast';
import { Eye, EyeOff, Loader2, AlertCircle } from 'lucide-react';
import logo from '@/assets/logo.jpg';

const MAX_ATTEMPTS = 5;
const LOCKOUT_SECONDS = 30;

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [failedAttempts, setFailedAttempts] = useState(0);
  const [lockoutTimer, setLockoutTimer] = useState(0);
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Si déjà authentifié, redirect direct
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  // Lockout countdown
  useEffect(() => {
    if (lockoutTimer <= 0) return;
    const interval = setInterval(() => {
      setLockoutTimer((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [lockoutTimer]);

  const isLocked = lockoutTimer > 0;

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    setError(null);

    if (!email || !password) {
      setError('Veuillez remplir tous les champs.');
      return;
    }

    if (isLocked) return;

    setIsLoading(true);

    try {
      await login(email, password);
      toast({
        title: 'Connexion réussie',
        description: 'Bienvenue sur Teranga Civil.',
        variant: 'success',
      });
      navigate('/dashboard', { replace: true });
    } catch (err) {
      const newAttempts = failedAttempts + 1;
      setFailedAttempts(newAttempts);

      if (newAttempts >= MAX_ATTEMPTS) {
        setLockoutTimer(LOCKOUT_SECONDS);
        setFailedAttempts(0);
        setError(`Trop de tentatives. Réessayez dans ${LOCKOUT_SECONDS}s.`);
      } else {
        const message =
          err.response?.status === 401
            ? 'Identifiants incorrects. Vérifiez votre email et mot de passe.'
            : err.response?.data?.detail || 'Erreur de connexion. Veuillez réessayer.';
        setError(message);
      }
    } finally {
      setIsLoading(false);
    }
  }, [email, password, isLocked, failedAttempts, login, navigate]);

  const handleForgotPassword = (e) => {
    e.preventDefault();
    toast({
      title: 'Mot de passe oublié',
      description: 'Contactez votre administrateur système pour réinitialiser votre mot de passe.',
    });
  };

  const inputErrorClass = error && error.includes('Identifiants')
    ? 'border-[#E24B4A] bg-[#FFF8F8] focus-visible:ring-[#E24B4A]'
    : '';

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: '#F4F6F9' }}>
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full blur-3xl" style={{ background: 'rgba(30,58,95,0.05)' }} />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full blur-3xl" style={{ background: 'rgba(45,158,107,0.05)' }} />
      </div>

      <div className="w-full max-w-md relative animate-enter">
        {/* Logo section */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center mb-4">
            <img src={logo} alt="Teranga Civil Logo" className="h-24 w-auto object-contain rounded-2xl shadow-xl border border-white/20" />
          </div>
          <h1 className="text-[26px] font-semibold tracking-tight" style={{ color: '#1E3A5F', letterSpacing: '-0.3px' }}>
            Teranga Civil
          </h1>
          <p className="text-slate-500 mt-1 text-sm font-medium">
            Espace Administration
          </p>
        </div>

        <Card className="border-0 shadow-2xl shadow-slate-200/50 backdrop-blur-sm">
          <CardHeader className="pb-4">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-secondary">Connexion</h2>
              <p className="text-sm text-slate-400 mt-1">
                Accédez à votre espace de gestion
              </p>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Error banner */}
              {error && (
                <div
                  className="flex items-start gap-3 text-sm animate-enter rounded-md"
                  style={{
                    background: '#FCEBEB',
                    borderLeft: '3px solid #E24B4A',
                    color: '#A32D2D',
                    padding: '10px 14px',
                  }}
                  role="alert"
                >
                  <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>{isLocked ? `Trop de tentatives. Réessayez dans ${lockoutTimer}s.` : error}</span>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email" className="text-slate-600">
                  Adresse email
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="votre.email@teranga.sn"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setError(null); }}
                  disabled={isLoading || isLocked}
                  autoComplete="email"
                  className={`h-11 bg-white border-[#E2E8F0] text-[#1E293B] placeholder:text-[#94A3B8] focus-visible:ring-[#378ADD]/20 focus-visible:border-[#378ADD] ${inputErrorClass}`}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-slate-600">
                  Mot de passe
                </Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => { setPassword(e.target.value); setError(null); }}
                    disabled={isLoading || isLocked}
                    autoComplete="current-password"
                    className={`h-11 pr-10 bg-white border-[#E2E8F0] text-[#1E293B] placeholder:text-[#94A3B8] focus-visible:ring-[#378ADD]/20 focus-visible:border-[#378ADD] ${inputErrorClass}`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors focus-visible:outline-2 focus-visible:outline-[#378ADD] focus-visible:outline-offset-2 rounded"
                    tabIndex={-1}
                    aria-label={showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Lien mot de passe oublié */}
              <div className="flex justify-end -mt-1">
                <a
                  href="#"
                  onClick={handleForgotPassword}
                  className="text-[13px] font-medium transition-colors focus-visible:outline-2 focus-visible:outline-[#378ADD] focus-visible:outline-offset-2 rounded"
                  style={{ color: '#378ADD' }}
                  onMouseEnter={(e) => { e.target.style.color = '#1E3A5F'; }}
                  onMouseLeave={(e) => { e.target.style.color = '#378ADD'; }}
                >
                  Mot de passe oublié ?
                </a>
              </div>

              {/* Bouton Se connecter — bleu marine */}
              <button
                type="submit"
                disabled={isLoading || isLocked}
                className="w-full h-11 text-[15px] font-semibold text-white rounded-lg transition-all duration-150 focus-visible:outline-2 focus-visible:outline-[#378ADD] focus-visible:outline-offset-2 disabled:cursor-not-allowed"
                style={{
                  backgroundColor: isLoading || isLocked ? '#94A3B8' : '#1E3A5F',
                  cursor: isLoading || isLocked ? 'not-allowed' : 'pointer',
                }}
                onMouseEnter={(e) => { if (!isLoading && !isLocked) e.target.style.backgroundColor = '#162E4D'; }}
                onMouseLeave={(e) => { if (!isLoading && !isLocked) e.target.style.backgroundColor = '#1E3A5F'; }}
                onMouseDown={(e) => { e.target.style.transform = 'scale(0.99)'; }}
                onMouseUp={(e) => { e.target.style.transform = 'scale(1)'; }}
              >
                {isLoading ? (
                  <span className="inline-flex items-center justify-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Connexion en cours...
                  </span>
                ) : (
                  'Se connecter'
                )}
              </button>
            </form>
          </CardContent>
        </Card>

        <p className="text-center text-xs text-slate-400 mt-6">
          © 2026 Teranga Civil — République du Sénégal
        </p>
      </div>
    </div>
  );
}
