import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import { register, createProject } from '../api';

export default function SignUpView({ lang = 'fr' }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const translations = {
    fr: {
      title: "Créer un compte",
      subtitle: "Rejoignez la plateforme et lancez votre évaluation",
      nameLabel: "Nom complet",
      namePlaceholder: "Jean Dupont",
      emailLabel: "Adresse e-mail",
      emailPlaceholder: "nom@entreprise.com",
      passwordLabel: "Mot de passe",
      passwordPlaceholder: "Créer un mot de passe",
      confirmPasswordLabel: "Confirmer le mot de passe",
      confirmPasswordPlaceholder: "Confirmez votre mot de passe",
      btnSubmit: "S'inscrire",
      btnSubmitting: "Inscription en cours...",
      hasAccount: "Déjà un compte ?",
      linkLogin: "Se connecter",
      errNameRequired: "Le nom complet est requis.",
      errEmailRequired: "L'adresse e-mail est requise.",
      errEmailInvalid: "L'adresse e-mail n'est pas valide.",
      errPasswordRequired: "Le mot de passe est requis.",
      errConfirmPasswordRequired: "La confirmation du mot de passe est requise.",
      errPasswordsMatch: "Les mots de passe ne correspondent pas.",
      successMsg: "Votre compte a été créé avec succès ! Redirection vers la connexion...",
    },
    ar: {
      title: "إنشاء حساب",
      subtitle: "انضم إلى المنصة وابدأ تقييمك الخاص",
      nameLabel: "الاسم الكامل",
      namePlaceholder: "أحمد بن علي",
      emailLabel: "البريد الإلكتروني",
      emailPlaceholder: "name@company.com",
      passwordLabel: "كلمة المرور",
      passwordPlaceholder: "أنشئ كلمة مرور",
      confirmPasswordLabel: "تأكيد كلمة المرور",
      confirmPasswordPlaceholder: "أعد كتابة كلمة المرور",
      btnSubmit: "إنشاء حساب",
      btnSubmitting: "جاري التسجيل...",
      hasAccount: "لديك حساب بالفعل؟",
      linkLogin: "تسجيل الدخول",
      errNameRequired: "الاسم الكامل مطلوب.",
      errEmailRequired: "البريد الإلكتروني مطلوب.",
      errEmailInvalid: "البريد الإلكتروني غير صالح.",
      errPasswordRequired: "كلمة المرور مطلوبة.",
      errConfirmPasswordRequired: "تأكيد كلمة المرور مطلوب.",
      errPasswordsMatch: "كلمات المرور غير متطابقة.",
      successMsg: "تم إنشاء حسابك بنجاح! جاري التوجيه نحو تسجيل الدخول...",
    }
  };

  const t = translations[lang] || translations.fr;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear validation error when typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.fullName.trim()) {
      newErrors.fullName = t.errNameRequired;
    }

    if (!formData.email.trim()) {
      newErrors.email = t.errEmailRequired;
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = t.errEmailInvalid;
    }
    
    if (!formData.password) {
      newErrors.password = t.errPasswordRequired;
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = t.errConfirmPasswordRequired;
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = t.errPasswordsMatch;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
  e.preventDefault();
  if (!validate()) return;

  setIsSubmitting(true);

  try {
    // Appel API pour inscription
    const data = await register(formData.email, formData.password, formData.name);

    // Créer le projet juste après inscription
    await createProject("Mon Projet", formData.secteur);

    // Message de succès
    setSuccessMessage(t.successMsg);

    // Redirection vers le questionnaire
    navigate('/questionnaire');
  } catch (error) {
    console.error("Erreur lors de l'inscription :", error);
    setSuccessMessage("Une erreur est survenue.");
  } finally {
    setIsSubmitting(false);
  }
};


  const isRtl = lang === 'ar';

  return (
    <div className="flex-1 flex items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md animate-fade-in">
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
            <form className="space-y-5" onSubmit={handleSubmit}>
              {/* Full Name Input */}
              <div className="space-y-2">
                <label htmlFor="fullName" className="block text-sm font-medium text-slate-300">
                  {t.nameLabel}
                </label>
                <input
                  id="fullName"
                  name="fullName"
                  type="text"
                  required
                  value={formData.fullName}
                  onChange={handleChange}
                  className={`glass-input w-full px-4 py-3 ${errors.fullName ? 'border-red-500/70 focus:border-red-500 focus:shadow-red-500/10' : ''}`}
                  placeholder={t.namePlaceholder}
                />
                {errors.fullName && (
                  <p className="text-xs text-red-400 mt-1 font-medium">{errors.fullName}</p>
                )}
              </div>

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
                    autoComplete="new-password"
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

              {/* Confirm Password Input */}
              <div className="space-y-2">
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-300">
                  {t.confirmPasswordLabel}
                </label>
                <div className="relative">
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    required
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className={`glass-input w-full pl-4 pr-10 py-3 ${errors.confirmPassword ? 'border-red-500/70 focus:border-red-500 focus:shadow-red-500/10' : ''}`}
                    placeholder={t.confirmPasswordPlaceholder}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-200 transition-colors"
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {errors.confirmPassword && (
                  <p className="text-xs text-red-400 mt-1 font-medium">{errors.confirmPassword}</p>
                )}
              </div>

              {/* Submit Button */}
              <div className="pt-2">
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
              {t.hasAccount}{' '}
              <Link
                to="/login"
                className="font-medium text-cyan-400 hover:text-cyan-300 transition-colors inline-flex items-center gap-0.5"
              >
                {t.linkLogin}
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
