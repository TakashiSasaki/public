import { useState } from "react";

import pictogramsData from "./assets/pictograms.json";

// --- 1. SVG Component Definitions ---

// Helper function to create a React component from raw SVG string
const createSvgComponent = (svgContent, defaultViewBox) => {
    return (props) => {
        return (
            <svg
                viewBox={defaultViewBox}
                fill="none"
                stroke="currentColor"
                strokeWidth={defaultViewBox === "0 0 16 16" ? "1.5" : "2"}
                strokeLinecap="round"
                strokeLinejoin="round"
                {...props}
                dangerouslySetInnerHTML={{ __html: svgContent }}
            />
        );
    };
};

const Bases = {};
Object.entries(pictogramsData.bases).forEach(([name, data]) => {
    Bases[name] = createSvgComponent(data.content, data.viewBox);
});

const Badges = {};
Object.entries(pictogramsData.badges).forEach(([name, data]) => {
    Badges[name] = createSvgComponent(data.content, data.viewBox);
});

// --- 2. Composition Engine ---

const CompositeCursor = ({
    baseName,
    badgeName,
    badge2Name,
    colorClass,
    size = 64,
}) => {
    const Base = Bases[baseName];
    const Badge1 = badgeName ? Badges[badgeName] : null;
    const Badge2 = badge2Name ? Badges[badge2Name] : null;

    if (!Base) return null;

    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 32 32"
            className={`overflow-visible ${colorClass} transition-colors duration-300 drop-shadow-md`}
        >
            {/* --- Base Layer --- */}
            <g>
                <Base />
            </g>

            {/* --- Top Left Badge (Badge 2) --- */}
            {Badge2 && (
                <g transform="translate(-4, -4)">
                    {/* Mask to hide underlying base lines */}
                    <circle
                        cx="8"
                        cy="8"
                        r="8"
                        className="fill-white dark:fill-gray-900"
                    />
                    <svg x="0" y="0" width="16" height="16">
                        <Badge2 />
                    </svg>
                </g>
            )}

            {/* --- Bottom Right Badge (Badge 1) --- */}
            {Badge1 && (
                <g transform="translate(16, 16)">
                    {/* Mask to hide underlying base lines */}
                    <circle
                        cx="8"
                        cy="8"
                        r="8"
                        className="fill-white dark:fill-gray-900"
                    />
                    <svg x="0" y="0" width="16" height="16">
                        <Badge1 />
                    </svg>
                </g>
            )}
        </svg>
    );
};

// --- 3. Main Application UI ---

const App = () => {
    const [selectedBase, setSelectedBase] = useState("RackServer");
    const [selectedBadge, setSelectedBadge] = useState("Database");
    const [selectedBadge2, setSelectedBadge2] = useState("");
    const [selectedColor, setSelectedColor] = useState(
        "text-red-600 dark:text-red-400",
    );

    const colorOptions = [
        {
            label: "Production (Red)",
            value: "text-red-600 dark:text-red-400",
            bg: "bg-red-100 dark:bg-red-900/30",
        },
        {
            label: "Development (Green)",
            value: "text-green-600 dark:text-green-400",
            bg: "bg-green-100 dark:bg-green-900/30",
        },
        {
            label: "Normal (Blue)",
            value: "text-blue-600 dark:text-blue-400",
            bg: "bg-blue-100 dark:bg-blue-900/30",
        },
        {
            label: "Default (Gray)",
            value: "text-gray-800 dark:text-gray-200",
            bg: "bg-gray-100 dark:bg-gray-800",
        },
    ];

    const presets = [
        {
            label: "CNC マシニングセンタ",
            base: "ControlTerminal",
            badge: "MillingMachine",
            badge2: "Warning",
            color: colorOptions[0].value,
        },
        {
            label: "NC旋盤 操作盤",
            base: "FATerminal",
            badge: "NCLathe",
            badge2: "Factory",
            color: colorOptions[1].value,
        },
        {
            label: "3Dプリントサーバ",
            base: "MiniPC",
            badge: "Printer3D",
            badge2: "Lab",
            color: colorOptions[2].value,
        },
        {
            label: "ロボットセル制御",
            base: "Industrial",
            badge: "Manipulator",
            badge2: "App",
            color: colorOptions[0].value,
        },
        {
            label: "監視・チャート用縦画面",
            base: "DualMonitorVerticalPC",
            badge: "App",
            badge2: "Office",
            color: colorOptions[2].value,
        },
        {
            label: "データ解析 (ポケコン)",
            base: "PocketComputer",
            badge: "Student",
            badge2: "Scroll",
            color: colorOptions[1].value,
        },
    ];

    return (
        <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-8 font-sans transition-colors">
            <div className="max-w-5xl mx-auto space-y-12">
                <header className="border-b border-gray-200 dark:border-gray-800 pb-6">
                    <h1 className="text-3xl font-bold tracking-tight">
                        Remote Desktop Custom Cursors
                    </h1>
                    <p className="mt-2 text-gray-600 dark:text-gray-400">
                        SVG Pictogram Synthesizer & Gallery for identifying remote machines.
                    </p>
                </header>

                {/* --- Interactive Builder Section --- */}
                <section className="bg-gray-50 dark:bg-gray-800/50 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
                    <h2 className="text-xl font-semibold mb-6 flex items-center">
                        <span className="bg-blue-500 text-white w-8 h-8 rounded-full inline-flex items-center justify-center mr-3 text-sm">
                            1
                        </span>
                        Interactive Builder
                    </h2>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Controls */}
                        <div className="lg:col-span-2 space-y-6">
                            {/* Base Selection */}
                            <div>
                                <span className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                                    Base Form (Hardware/Location)
                                </span>
                                <div className="flex flex-wrap gap-2">
                                    {Object.keys(Bases).map((baseKey) => (
                                        <button
                                            key={baseKey}
                                            onClick={() => setSelectedBase(baseKey)}
                                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors border ${selectedBase === baseKey
                                                ? "bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/40 dark:border-blue-700 dark:text-blue-300"
                                                : "bg-white border-gray-200 text-gray-700 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
                                                }`}
                                        >
                                            {baseKey}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Badges Selection */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                                <div>
                                    <label htmlFor="primary-badge-select" className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                                        Primary Badge (Bottom Right)
                                    </label>
                                    <select
                                        id="primary-badge-select"
                                        value={selectedBadge}
                                        onChange={(e) => setSelectedBadge(e.target.value)}
                                        className="w-full p-2.5 bg-white border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                                    >
                                        <option value="">-- None --</option>
                                        {Object.keys(Badges).map((badgeKey) => (
                                            <option key={badgeKey} value={badgeKey}>
                                                {badgeKey}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label htmlFor="status-badge-select" className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                                        Status Badge (Top Left)
                                    </label>
                                    <select
                                        id="status-badge-select"
                                        value={selectedBadge2}
                                        onChange={(e) => setSelectedBadge2(e.target.value)}
                                        className="w-full p-2.5 bg-white border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                                    >
                                        <option value="">-- None --</option>
                                        {Object.keys(Badges).map((badgeKey) => (
                                            <option key={badgeKey} value={badgeKey}>
                                                {badgeKey}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            {/* Color Selection */}
                            <div>
                                <span className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                                    Environment Color
                                </span>
                                <div className="flex gap-3">
                                    {colorOptions.map((opt, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => setSelectedColor(opt.value)}
                                            title={opt.label}
                                            className={`w-10 h-10 rounded-full border-2 transition-all flex items-center justify-center ${opt.bg} ${selectedColor === opt.value ? "border-gray-900 dark:border-white scale-110 shadow-md" : "border-transparent opacity-70 hover:opacity-100"}`}
                                        >
                                            {/* Inner dot reflecting stroke color approximation */}
                                            <div
                                                className={`w-3 h-3 rounded-full ${opt.value.split(" ")[0].replace("text-", "bg-")}`}
                                            ></div>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Preview Area */}
                        <div className="flex flex-col items-center justify-center bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-8 shadow-inner">
                            <span className="text-sm text-gray-400 dark:text-gray-500 mb-6 uppercase tracking-widest font-semibold">
                                Preview (64px)
                            </span>

                            {/* The Composite Component */}
                            <div className="relative group cursor-crosshair">
                                <CompositeCursor
                                    baseName={selectedBase}
                                    badgeName={selectedBadge}
                                    badge2Name={selectedBadge2}
                                    colorClass={selectedColor}
                                    size={96}
                                />

                                {/* Hotspot indicator overlay (only visible on hover for demonstration) */}
                                <div className="absolute top-0 left-0 w-3 h-3 bg-red-500 rounded-full -translate-x-1.5 -translate-y-1.5 opacity-0 group-hover:opacity-50 pointer-events-none animate-pulse"></div>
                            </div>

                            <p className="mt-8 text-xs text-center text-gray-500 dark:text-gray-400">
                                Red dot indicates standard cursor hotspot (0,0).
                            </p>
                        </div>
                    </div>
                </section>

                {/* --- Presets Gallery Section --- */}
                <section>
                    <h2 className="text-xl font-semibold mb-6 flex items-center">
                        <span className="bg-blue-500 text-white w-8 h-8 rounded-full inline-flex items-center justify-center mr-3 text-sm">
                            2
                        </span>
                        Practical Scenarios (Presets)
                    </h2>

                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {presets.map((preset, idx) => (
                            <div
                                key={idx}
                                className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5 flex flex-col items-center hover:shadow-lg transition-shadow cursor-pointer"
                                onClick={() => {
                                    setSelectedBase(preset.base);
                                    setSelectedBadge(preset.badge);
                                    setSelectedBadge2(preset.badge2);
                                    setSelectedColor(preset.color);
                                }}
                            >
                                <div className="mb-4 h-16 flex items-center justify-center">
                                    <CompositeCursor
                                        baseName={preset.base}
                                        badgeName={preset.badge}
                                        badge2Name={preset.badge2}
                                        colorClass={preset.color}
                                        size={48}
                                    />
                                </div>
                                <h3 className="text-sm font-medium text-center">
                                    {preset.label}
                                </h3>
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 text-center">
                                    {preset.base} + {preset.badge || "None"}
                                </p>
                            </div>
                        ))}
                    </div>
                </section>

                {/* --- Raw Assets Reference --- */}
                <section className="pt-8 border-t border-gray-200 dark:border-gray-800">
                    <h2 className="text-lg font-semibold mb-4 text-gray-700 dark:text-gray-300">
                        Raw Components Catalog
                    </h2>

                    <div className="mb-6">
                        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
                            Base Forms
                        </h3>
                        <div className="flex flex-wrap gap-4">
                            {Object.entries(Bases).map(([name, BaseComponent]) => (
                                <div
                                    key={name}
                                    className="flex flex-col items-center bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg border border-gray-100 dark:border-gray-700"
                                >
                                    <BaseComponent className="w-8 h-8 text-gray-800 dark:text-gray-200 mb-2" />
                                    <span className="text-xs text-gray-500">{name}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div>
                        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
                            Badges
                        </h3>
                        <div className="flex flex-wrap gap-4">
                            {Object.entries(Badges).map(([name, BadgeComponent]) => (
                                <div
                                    key={name}
                                    className="flex flex-col items-center bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg border border-gray-100 dark:border-gray-700"
                                >
                                    <BadgeComponent className="w-6 h-6 text-gray-800 dark:text-gray-200 mb-2" />
                                    <span className="text-xs text-gray-500">{name}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
};

export default App;
