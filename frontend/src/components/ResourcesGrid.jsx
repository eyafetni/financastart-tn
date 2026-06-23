import React, { useState } from 'react';
import { Bookmark, Search, ExternalLink, Filter, HelpCircle } from 'lucide-react';
import { translations } from '../data/interfaceTranslations';

export default function ResourcesGrid({ resources, lang }) {
  const t = translations[lang];
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');

  if (!resources || resources.length === 0) {
    return null;
  }

  // Extract unique resource types for filter dropdown/tabs
  const resourceTypes = [
    { code: 'all', label: t.allTypes },
    ...Array.from(new Set(resources.map(r => r.type.fr))).map(typeFr => {
      const match = resources.find(r => r.type.fr === typeFr);
      return {
        code: typeFr,
        label: match?.type[lang] || typeFr
      };
    })
  ];

  // Filter resources based on search query and type
  const filteredResources = resources.filter(res => {
    const nameText = (res.name[lang] || res.name.fr || '').toLowerCase();
    const orgText = (res.organisme[lang] || res.organisme.fr || '').toLowerCase();
    const query = searchQuery.toLowerCase();
    const matchesSearch = nameText.includes(query) || orgText.includes(query);

    const matchesType = selectedType === 'all' || res.type.fr === selectedType;

    return matchesSearch && matchesType;
  });

  const getRelevanceColor = (score) => {
    if (score >= 60) return 'text-emerald-400 bg-emerald-500/15 border-emerald-500/30';
    if (score >= 50) return 'text-amber-400 bg-amber-500/15 border-amber-500/30';
    return 'text-slate-400 bg-slate-800 border-slate-700/50';
  };

  return (
    <div className="glass-card p-6 flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-wide flex items-center gap-2">
            <Bookmark className="h-5 w-5 text-cyan-400" />
            {t.resourcesTitle}
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">{t.resourcesSubtitle}</p>
        </div>

        {/* Search & Filter Controls */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          {/* Search bar */}
          <div className="relative">
            <Search className="absolute start-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t.searchResourcePlaceholder}
              className="w-full sm:w-56 ps-9 pe-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none transition-all"
            />
          </div>

          {/* Type filter dropdown */}
          <div className="relative flex items-center gap-1.5 bg-slate-950 border border-slate-800 rounded-xl px-3 py-2">
            <Filter className="h-3.5 w-3.5 text-slate-500" />
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="bg-transparent border-none text-xs text-white focus:outline-none cursor-pointer pr-4"
            >
              {resourceTypes.map(tOption => (
                <option key={tOption.code} value={tOption.code} className="bg-slate-900 text-white text-xs">
                  {tOption.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Grid List */}
      {filteredResources.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredResources.map((res) => {
            const { id, name, organisme, type, taux, urlSource, pertinence, justification } = res;
            const relColor = getRelevanceColor(pertinence);

            return (
              <div
                key={id}
                className="rounded-2xl border border-slate-800/80 bg-slate-950/20 hover:border-slate-700/80 hover:bg-slate-950/40 p-5 flex flex-col justify-between gap-4 transition-all duration-300 shadow-md group"
              >
                <div className="flex flex-col gap-2.5">
                  {/* Top line badges */}
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-[9px] uppercase font-bold text-cyan-400 bg-cyan-950/60 border border-cyan-800/30 px-2 py-0.5 rounded">
                      {type[lang]}
                    </span>
                    <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded border ${relColor}`}>
                      {t.relevanceLabel}: {pertinence}%
                    </span>
                  </div>

                  {/* Organisme */}
                  <p className="text-[10px] text-slate-500 font-semibold tracking-wide uppercase leading-none">
                    {organisme[lang]}
                  </p>

                  {/* Resource Name */}
                  <h4 className="text-xs font-extrabold text-white group-hover:text-cyan-400 transition-colors leading-relaxed">
                    {urlSource ? (
                      <a
                        href={urlSource}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1.5 hover:underline"
                      >
                        {name[lang]}
                        <ExternalLink className="h-3 w-3 inline-block shrink-0 opacity-60 group-hover:opacity-100" />
                      </a>
                    ) : (
                      name[lang]
                    )}
                  </h4>

                  {/* Rate / Taux */}
                  {taux && taux.fr && taux.fr !== "N/A" && (
                    <div className="text-[10px] text-slate-400 bg-slate-900/60 border border-slate-850 px-2.5 py-1.5 rounded-lg flex flex-col gap-0.5">
                      <span className="text-[8px] uppercase tracking-wider text-slate-500 font-extrabold">
                        {t.rateLabel}
                      </span>
                      <span className="font-mono font-medium text-slate-300">
                        {taux[lang]}
                      </span>
                    </div>
                  )}

                  {/* Justification / Pertinence explanation */}
                  <p className="text-[11px] text-slate-450 leading-relaxed italic border-t border-slate-900 pt-2.5">
                    {justification[lang] || justification.fr}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-8 text-slate-500 text-xs font-semibold">
          {lang === 'fr' ? 'Aucune ressource ne correspond à vos critères.' : 'لا توجد موارد تطابق معايير البحث الخاصة بك.'}
        </div>
      )}
    </div>
  );
}
