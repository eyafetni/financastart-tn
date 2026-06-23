import React from 'react';
import { DollarSign, ShieldAlert, CheckCircle } from 'lucide-react';
import { translations } from '../data/interfaceTranslations';

export default function FinancingReadiness({ readinessData, lang }) {
  const t = translations[lang];
  const { score, status, statusLabel, description } = readinessData;

  const isBankable = status === 'bankable';

  // SVG Gauge calculations
  const radius = 55;
  const stroke = 8;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="glass-card p-6 flex flex-col items-center gap-6 h-full justify-between">
      {/* Header */}
      <div className="w-full flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-wide">{t.financingTitle}</h2>
          <p className="text-xs text-slate-400">{t.financingStatus}</p>
        </div>
        <div className="h-9 w-9 rounded-lg bg-slate-800 flex items-center justify-center">
          <DollarSign className="h-5 w-5 text-yellow-500" />
        </div>
      </div>

      {/* SVG Radial Gauge */}
      <div className="relative flex items-center justify-center my-2">
        <svg
          height={radius * 2}
          width={radius * 2}
          className="transform -rotate-90"
        >
          {/* Gradients definitions */}
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06b6d4" /> {/* cyan-500 */}
              <stop offset="50%" stopColor="#3b82f6" /> {/* blue-500 */}
              <stop offset="100%" stopColor="#4f46e5" /> {/* indigo-600 */}
            </linearGradient>
          </defs>
          {/* Background circle */}
          <circle
            stroke="#1e293b" // slate-800
            fill="transparent"
            strokeWidth={stroke}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
          {/* Foreground progress circle */}
          <circle
            stroke="url(#gaugeGradient)"
            fill="transparent"
            strokeWidth={stroke}
            strokeDasharray={circumference + ' ' + circumference}
            style={{ strokeDashoffset, transition: 'stroke-dashoffset 1s ease-out-in' }}
            strokeLinecap="round"
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
        </svg>

        {/* Text inside the ring */}
        <div className="absolute flex flex-col items-center justify-center">
          <span className="text-3xl font-extrabold text-white tracking-tight font-mono">
            {score}
          </span>
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
            / 100
          </span>
        </div>
      </div>

      {/* Bankability Badge Status */}
      <div className="w-full flex flex-col gap-3">
        <div className={`flex items-center justify-center gap-2 py-2 px-4 rounded-xl border font-bold text-sm text-center ${
          isBankable 
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
            : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
        }`}>
          {isBankable ? (
            <CheckCircle className="h-4 w-4" />
          ) : (
            <ShieldAlert className="h-4 w-4 animate-bounce" />
          )}
          <span className="tracking-wide text-xs">
            {isBankable ? t.bankable : t.notBankable}
          </span>
        </div>

        {/* Description justification box */}
        <div className="bg-slate-950/40 border border-slate-800 p-3 rounded-xl">
          <p className="text-xs leading-relaxed text-slate-400 text-center font-medium">
            {description[lang]}
          </p>
        </div>
      </div>
    </div>
  );
}
