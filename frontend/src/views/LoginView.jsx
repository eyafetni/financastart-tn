import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import { login } from '../api';

export default function LoginView({ lang = 'fr', onLoginSuccess }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const translations = {
    fr: {
      title: "Connexion",
      subtitle: "Accédez à votre espace entrepreneur",
      emailLabel: "Adresse e-mail",
      emailPlaceholder: "nom@entreprise.com",
      passwordLabel: "Mot de passe",
      passwordPlaceholder: "Saisissez votre mot de passe",
      btnSubmit: "Se connecter",
      btnSubmitting: "Connexion en cours...",
      noAccount: "Nouveau sur la plateforme ?",
      linkSignUp: "Créer un compte",
      errEmailRequired: "L'adresse e-mail est requise.",
      errEmailInvalid: "L'adresse e-mail n'est pas valide.",
      errPasswordRequired: "Le mot de passe est requis.",
      errInvalidCredentials: "Email ou mot de passe incorrect.",
      successMsg: "Connexion réussie ! Redirection...",
    },
    ar: {
      title: "تسجيل الدخول",
      subtitle: "الوصول إلى مساحة رائد الأعمال الخاصة بك",
      emailLabel: "البريد الإلكتروني",
      emailPlaceholder: "name@company.com",
      passwordLabel: "كلمة المرور",
      passwordPlaceholder: "أدخل كلمة المرور الخاصة بك",
      btnSubmit: "تسجيل الدخول",
      btnSubmitting: "جاري تسجيل الدخول...",
      noAccount: "جديد على المنصة؟",
      linkSignUp: "إنشاء حساب",
      errEmailRequired: "البريد الإلكتروني مطلوب.",
      errEmailInvalid: "البريد الإلكتروني غير صالح.",
      errPasswordRequired: "كلمة المرور مطلوبة.",
      errInvalidCredentials: "البريد الإلكتروني أو كلمة المرور غير صحيحة.",
      successMsg: "تم تسجيل الدخول بنجاح! جاري التوجيه...",
    }
  };

  const t = translations[lang] || translations.fr;
  const isRtl = lang === 'ar';

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.email.trim()) {
      newErrors.email = t.errEmailRequired;
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = t.errEmailInvalid;
    }

    if (!formData.password) {
      newErrors.password = t.errPasswordRequired;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      // login() pose déjà "token", "user_id" et "project_id" dans localStorage
      await login(formData.email, formData.password);
      setSuccessMessage(t.successMsg);
      if (onLoginSuccess) {
        onLoginSuccess();
      }
      setTimeout(() => {
        navigate('/');
      }, 1000);
    } catch (error) {
      console.error('Erreur lors de la connexion :', error);
      setErrors({ password: t.errInvalidCredentials });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex-1 flex items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md animate-fade-in" dir={isRtl ? 'rtl' : 'ltr'}>
        <div className="text-center mb-8">

          <h2 className="text-3xl font-extrabold text-white tracking-tight">
            {t.title}
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            {t.subtitle}
          </p>
        </div>

        <div className="glass-card p-8">
          {successMessage ? (
            <div className="bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 rounded-xl p-4 text-center text-sm font-medium">
              {successMessage}
            </div>
          ) : (
            <form className="space-y-6" onSubmit={handleSubmit}>
              {/* Email Input */}
              <div className="space-y-2">
                <label htmlFor="email" className="block text-sm font-medium text-slate-300">
                  {t.emailLabel}
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className={`glass-input w-full px-4 py-3 ${errors.email ? 'border-red-500/70 focus:border-red-500 focus:shadow-red-500/10' : ''}`}
                  placeholder={t.emailPlaceholder}
                />
                {errors.email && (
                  <p className="text-xs text-red-400 mt-1 font-medium">{errors.email}</p>
                )}
              </div>

              {/* Password Input */}
              <div className="space-y-2">
                <label htmlFor="password" className="block text-sm font-medium text-slate-300">
                  {t.passwordLabel}
                </label>
                <div className="relative">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    value={formData.password}
                    onChange={handleChange}
                    className={`glass-input w-full pl-4 pr-10 py-3 ${errors.password ? 'border-red-500/70 focus:border-red-500 focus:shadow-red-500/10' : ''}`}
                    placeholder={t.passwordPlaceholder}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-200 transition-colors"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-xs text-red-400 mt-1 font-medium">{errors.password}</p>
                )}
              </div>

              {/* Submit Button */}
              <div>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full flex justify-center items-center gap-2 py-3 px-4 border border-transparent rounded-xl text-sm font-semibold text-slate-950 bg-cyan-400 hover:bg-cyan-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 transition-all shadow-lg shadow-cyan-400/15 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                >
                  {isSubmitting ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-slate-950" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      {t.btnSubmitting}
                    </>
                  ) : (
                    <span>{t.btnSubmit}</span>
                  )}
                </button>
              </div>
            </form>
          )}

          {/* Redirection Link */}
          <div className="mt-6 pt-6 border-t border-slate-800 text-center">
            <p className="text-sm text-slate-400">
              {t.noAccount}{' '}
              <Link
                to="/signup"
                className="font-medium text-cyan-400 hover:text-cyan-300 transition-colors inline-flex items-center gap-0.5"
              >
                {t.linkSignUp}
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
