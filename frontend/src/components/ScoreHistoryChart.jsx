import React, { useRef, useEffect, useState } from 'react';
import { scoreKeys, scoreLabels, scoreColors } from '../data/sessionHistory';

/**
 * Pure SVG line chart showing score progression over sessions.
 * No external charting library needed.
 */
export default function ScoreHistoryChart({ sessions, lang }) {
  const svgRef = useRef(null);
  const [tooltip, setTooltip] = useState(null);
  const [svgWidth, setSvgWidth] = useState(600);

  const PADDING = { top: 24, right: 24, bottom: 48, left: 40 };
  const HEIGHT = 240;

  useEffect(() => {
    const update = () => {
      if (svgRef.current) {
        setSvgWidth(svgRef.current.parentElement?.clientWidth || 600);
      }
    };
    update();
    const ro = new ResizeObserver(update);
    if (svgRef.current?.parentElement) ro.observe(svgRef.current.parentElement);
    return () => ro.disconnect();
  }, []);

  const innerW = svgWidth - PADDING.left - PADDING.right;
  const innerH = HEIGHT - PADDING.top - PADDING.bottom;
  const n = sessions.length;

  const xPos = (i) => PADDING.left + (n === 1 ? innerW / 2 : (i / (n - 1)) * innerW);
  const yPos = (v) => PADDING.top + innerH - (v / 100) * innerH;

  // Y-axis gridlines
  const gridLines = [0, 25, 50, 75, 100];

  return (
    <div className="relative w-full select-none">
      <svg
        ref={svgRef}
        width="100%"
        height={HEIGHT}
        className="overflow-visible"
        onMouseLeave={() => setTooltip(null)}
      >
        {/* Grid lines */}
        {gridLines.map((g) => (
          <g key={g}>
            <line
              x1={PADDING.left}
              x2={svgWidth - PADDING.right}
              y1={yPos(g)}
              y2={yPos(g)}
              stroke="#1e293b"
              strokeWidth={1}
              strokeDasharray={g === 0 ? 'none' : '4 4'}
            />
            <text
              x={PADDING.left - 6}
              y={yPos(g) + 4}
              textAnchor="end"
              fontSize={10}
              fill="#475569"
            >
              {g}
            </text>
          </g>
        ))}

        {/* X-axis date labels */}
        {sessions.map((sess, i) => (
          <text
            key={sess.id}
            x={xPos(i)}
            y={HEIGHT - 6}
            textAnchor="middle"
            fontSize={9}
            fill={sess.isCurrent ? '#06b6d4' : '#64748b'}
            fontWeight={sess.isCurrent ? '700' : '400'}
          >
            {sess.date.slice(5)} {/* MM-DD */}
          </text>
        ))}

        {/* Lines per score key */}
        {scoreKeys.map((key) => {
          const color = scoreColors[key];
          const points = sessions.map((s, i) => `${xPos(i)},${yPos(s.scores[key])}`).join(' ');

          return (
            <g key={key}>
              {/* Area fill */}
              <polygon
                points={`${xPos(0)},${yPos(0)} ${points} ${xPos(n - 1)},${yPos(0)}`}
                fill={color}
                fillOpacity={0.04}
              />
              {/* Line */}
              <polyline
                points={points}
                fill="none"
                stroke={color}
                strokeWidth={2}
                strokeLinejoin="round"
                strokeLinecap="round"
              />
              {/* Dots */}
              {sessions.map((sess, i) => (
                <circle
                  key={`${key}-${i}`}
                  cx={xPos(i)}
                  cy={yPos(sess.scores[key])}
                  r={sess.isCurrent ? 5 : 3.5}
                  fill={sess.isCurrent ? color : '#0f172a'}
                  stroke={color}
                  strokeWidth={sess.isCurrent ? 2.5 : 1.5}
                  style={{ cursor: 'pointer' }}
                  onMouseEnter={(e) => {
                    const rect = svgRef.current.getBoundingClientRect();
                    setTooltip({
                      x: e.clientX - rect.left,
                      y: e.clientY - rect.top,
                      key,
                      idx: i,
                      value: sess.scores[key],
                      date: sess.date,
                    });
                  }}
                />
              ))}
            </g>
          );
        })}

        {/* Tooltip */}
        {tooltip && (
          <g>
            <rect
              x={Math.min(tooltip.x + 8, svgWidth - 120)}
              y={tooltip.y - 36}
              width={110}
              height={36}
              rx={6}
              fill="#0f172a"
              stroke="#334155"
              strokeWidth={1}
            />
            <text
              x={Math.min(tooltip.x + 63, svgWidth - 65)}
              y={tooltip.y - 20}
              textAnchor="middle"
              fontSize={9}
              fill="#94a3b8"
            >
              {scoreLabels[lang][tooltip.key]} — {tooltip.date}
            </text>
            <text
              x={Math.min(tooltip.x + 63, svgWidth - 65)}
              y={tooltip.y - 6}
              textAnchor="middle"
              fontSize={12}
              fontWeight="700"
              fill={scoreColors[tooltip.key]}
            >
              {tooltip.value} / 100
            </text>
          </g>
        )}
      </svg>

      {/* Legend */}
      <div className="flex flex-wrap gap-x-4 gap-y-2 mt-2 justify-center">
        {scoreKeys.map((key) => (
          <div key={key} className="flex items-center gap-1.5">
            <span
              className="inline-block w-3 h-3 rounded-full"
              style={{ background: scoreColors[key] }}
            />
            <span className="text-[10px] text-slate-400">{scoreLabels[lang][key]}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
