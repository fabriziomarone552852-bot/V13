// frontend/src/components/weekmonth/TrackerPanel.tsx
import React from 'react';

// 1. IL CONTRATTO DEI DATI (Zero 'any')
export interface TrackerItem {
  id: string;
  name: string;
  colorHex: string;
  currentValue: number;  
  previousValue: number; 
}

interface TrackerPanelProps {
  titleTop: string;
  titleBottom: string;
  items: TrackerItem[];
  onUpdateValue: (id: string, newValue: number) => void;
}

// --- UTILITY MATEMATICA SVG ---
const polarToCartesian = (cx: number, cy: number, r: number, angleDegrees: number) => {
  const angleRadians = (angleDegrees - 90) * Math.PI / 180.0;
  return {
    x: cx + r * Math.cos(angleRadians),
    y: cy + r * Math.sin(angleRadians)
  };
};

const describeWedge = (x: number, y: number, radius: number, startAngle: number, endAngle: number): string => {
  const start = polarToCartesian(x, y, radius, endAngle);
  const end = polarToCartesian(x, y, radius, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  return [
    "M", x, y,
    "L", start.x, start.y,
    "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y,
    "Z"
  ].join(" ");
};

const describeTextArc = (x: number, y: number, radius: number, startAngle: number, endAngle: number): string => {
  let midAngle = (startAngle + endAngle) / 2;
  midAngle = ((midAngle % 360) + 360) % 360;

  const isBottom = midAngle > 90 && midAngle < 270;

  if (isBottom) {
    const start = polarToCartesian(x, y, radius, endAngle);
    const end = polarToCartesian(x, y, radius, startAngle);
    return `M ${start.x} ${start.y} A ${radius} ${radius} 0 0 0 ${end.x} ${end.y}`;
  } else {
    const start = polarToCartesian(x, y, radius, startAngle);
    const end = polarToCartesian(x, y, radius, endAngle);
    return `M ${start.x} ${start.y} A ${radius} ${radius} 0 0 1 ${end.x} ${end.y}`;
  }
};

// --- COMPONENTE GRAFICO POLARE (Smart Component) ---
const PolarAreaChart: React.FC<{ 
  items: TrackerItem[]; 
  valueKey: 'currentValue' | 'previousValue';
  onUpdateValue?: (id: string, newValue: number) => void;
}> = ({ items, valueKey, onUpdateValue }) => {
  const size = 320; 
  const center = size / 2;
  const maxRadius = 95; 
  const labelRadius = 120; // Raggio dell'etichetta perfetto
  const angleStep = 360 / items.length;
  const isInteractive = !!onUpdateValue;

  return (
    // MAGIA INGEGNERISTICA: L'SVG ora è 'absolute inset-0', forzato a rispettare il genitore
    <svg 
      viewBox={`0 0 ${size} ${size}`} 
      preserveAspectRatio="xMidYMid meet"
      className="absolute inset-0 w-full h-full overflow-visible"
    >
      <defs>
        {items.map((item: TrackerItem, i: number) => {
          const pathData = describeTextArc(center, center, labelRadius, i * angleStep, (i + 1) * angleStep);
          return <path key={`def-${item.id}`} id={`text-path-${valueKey}-${item.id}`} d={pathData} />;
        })}
      </defs>

      {/* 1. Ragnatela concentrica */}
      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((level: number) => (
        <circle key={`circle-${level}`} cx={center} cy={center} r={(level / 10) * maxRadius} fill="none" stroke="#f3f4f6" strokeWidth="1" />
      ))}
      
      {/* 2. Linee divisorie spicchi */}
      {items.map((_: TrackerItem, i: number) => {
        const { x, y } = polarToCartesian(center, center, maxRadius, i * angleStep);
        return <line key={`line-${i}`} x1={center} y1={center} x2={x} y2={y} stroke="#e5e7eb" strokeWidth="1" />;
      })}

      {/* 3. Riempimento dei Valori Reali */}
      {items.map((item: TrackerItem, i: number) => {
        const val = item[valueKey];
        if (val === 0) return null;
        
        const pathData = describeWedge(center, center, (val / 10) * maxRadius, i * angleStep, (i + 1) * angleStep);
        return (
          <path 
            key={`value-${item.id}`} d={pathData} fill={item.colorHex} 
            fillOpacity={isInteractive ? "0.95" : "0.35"} 
            stroke="#ffffff" strokeWidth="1.5" className="transition-all duration-500 ease-out"
          />
        );
      })}

      {/* 4. Hitboxes Interattive */}
      {isInteractive && onUpdateValue && items.map((item: TrackerItem, i: number) => {
        return [10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map((level: number) => {
          const pathData = describeWedge(center, center, (level / 10) * maxRadius, i * angleStep, (i + 1) * angleStep);
          return (
            <path 
              key={`hitbox-${item.id}-${level}`} 
              d={pathData} 
              fill="transparent"
              className="cursor-pointer hover:fill-black/20 transition-colors outline-none"
              onClick={() => onUpdateValue(item.id, level)}
            >
              <title>{`${item.name}: ${level}/10`}</title>
            </path>
          );
        });
      })}

      {/* 5. Etichette Nomi */}
      {items.map((item: TrackerItem) => (
        <text 
          key={`label-${item.id}`} 
          fill={item.colorHex} 
          className="text-[12px] font-black uppercase tracking-widest" 
          style={{ textShadow: '1px 1px 2px white' }}
        >
          <textPath href={`#text-path-${valueKey}-${item.id}`} startOffset="50%" textAnchor="middle">
            {item.name}
          </textPath>
        </text>
      ))}
    </svg>
  );
};

// --- COMPONENTE PRINCIPALE ESPORTATO ---
export const TrackerPanel: React.FC<TrackerPanelProps> = ({ titleTop, titleBottom, items, onUpdateValue }) => {
  return (
    <div className="flex flex-col h-full w-full overflow-hidden p-2">
      
      {/* SEZIONE SUPERIORE */}
      <div className="flex-1 min-h-0 flex flex-col items-center relative">
        <h4 className="text-[11px] font-extrabold text-gray-500 uppercase tracking-wider mt-2 shrink-0 z-10">
          {titleTop}
        </h4>
        {/* LA GABBIA DI CONTENIMENTO: Questo div assicura che l'SVG non esca dai bordi */}
        <div className="relative w-full flex-1 min-h-0">
            <PolarAreaChart items={items} valueKey="currentValue" onUpdateValue={onUpdateValue} />
        </div>
      </div>

      <div className="w-8/12 mx-auto h-px bg-gray-200 shrink-0 my-2"></div>

      {/* SEZIONE INFERIORE */}
      <div className="flex-1 min-h-0 flex flex-col items-center relative">
        <h4 className="text-[11px] font-extrabold text-gray-500 uppercase tracking-wider mt-2 shrink-0 z-10">
          {titleBottom}
        </h4>
        {/* LA GABBIA DI CONTENIMENTO */}
        <div className="relative w-full flex-1 min-h-0">
            <PolarAreaChart items={items} valueKey="previousValue" />
        </div>
      </div>

    </div>
  );
};