import { useState } from "react";

// --- 1. SVG Component Definitions ---

// Base Forms (32x32 viewBox)
const Bases = {
    RackServer: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* 2U servers in a rack */}
            <rect x="3" y="6" width="26" height="8" rx="1" />
            <rect x="3" y="18" width="26" height="8" rx="1" />
            {/* LED indicators */}
            <circle cx="24" cy="10" r="1.5" fill="currentColor" stroke="none" />
            <circle cx="24" cy="22" r="1.5" fill="currentColor" stroke="none" />
            {/* Rack ears */}
            <line x1="1" y1="8" x2="3" y2="8" />
            <line x1="1" y1="12" x2="3" y2="12" />
            <line x1="1" y1="20" x2="3" y2="20" />
            <line x1="1" y1="24" x2="3" y2="24" />
            <line x1="29" y1="8" x2="31" y2="8" />
            <line x1="29" y1="12" x2="31" y2="12" />
            <line x1="29" y1="20" x2="31" y2="20" />
            <line x1="29" y1="24" x2="31" y2="24" />
        </svg>
    ),
    TowerServer: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            <rect x="8" y="4" width="16" height="24" rx="2" />
            {/* Grills */}
            <line x1="12" y1="19" x2="20" y2="19" />
            <line x1="12" y1="22" x2="20" y2="22" />
            <line x1="12" y1="25" x2="20" y2="25" />
            {/* Power button */}
            <circle cx="16" cy="10" r="2" fill="currentColor" stroke="none" />
        </svg>
    ),
    DesktopPC: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Monitor */}
            <rect x="2" y="8" width="18" height="14" rx="1" />
            <path d="M7,22 v3 M15,22 v3 M5,25 h12" />
            {/* Tower */}
            <rect x="22" y="8" width="8" height="17" rx="1" />
            <line x1="24" y1="12" x2="28" y2="12" />
        </svg>
    ),
    Laptop: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Screen */}
            <rect x="5" y="8" width="22" height="14" rx="1" />
            {/* Keyboard base */}
            <path d="M3,22 h26 l-3,5 H6 Z" fill="currentColor" stroke="none" />
        </svg>
    ),
    MiniPC: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Box */}
            <rect x="6" y="10" width="20" height="14" rx="2" />
            {/* Power button / Logo area */}
            <circle cx="16" cy="17" r="4" />
            <line x1="16" y1="13" x2="16" y2="17" />
        </svg>
    ),
    Industrial: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Rugged Chassis */}
            <rect x="6" y="6" width="20" height="20" rx="1" />
            {/* Heatsink fins */}
            <path d="M6,10 h-2 M6,16 h-2 M6,22 h-2 M26,10 h2 M26,16 h2 M26,22 h2" />
            {/* Inner details */}
            <rect x="10" y="10" width="12" height="12" rx="1" />
            <circle cx="16" cy="16" r="2" fill="currentColor" stroke="none" />
        </svg>
    ),
    Cloud: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Cloud Silhouette */}
            <path d="M10,22 C6,22 4,19 4,16 C4,13.2 6.2,11 9,11 C10,7 13.5,5 17.5,6 C21.5,7 23,10 23,12 C26,12.5 28,15 28,18 C28,21 25.5,22 22,22 L10,22 Z" />
            {/* Inner Box (Instance) */}
            <rect x="12" y="12" width="6" height="6" rx="1" strokeDasharray="1 1" />
        </svg>
    ),
    SignageSTB: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* STB peeking out from behind (top right) */}
            <rect x="20" y="4" width="7" height="8" rx="1" />
            <line x1="22" y1="6" x2="25" y2="6" strokeWidth="1" />
            {/* Main Large Display with masking to hide STB bottom */}
            <rect
                x="2"
                y="10"
                width="28"
                height="16"
                rx="1"
                className="fill-white dark:fill-gray-900"
            />
            <rect x="2" y="10" width="28" height="16" rx="1" />
            {/* Simple wall mount / stand hint */}
            <path d="M12,26 v4 M20,26 v4 M10,30 h12" />
        </svg>
    ),
    LaptopSmallBlack: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Screen with inner cutout using evenodd fill rule for thick bezel effect */}
            <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M6,8 h20 a1,1 0 0,1 1,1 v11 a1,1 0 0,1 -1,1 h-20 a1,1 0 0,1 -1,-1 v-11 a1,1 0 0,1 1,-1 z M8,10 h16 v8 h-16 z"
                fill="currentColor"
                stroke="none"
            />
            {/* Keyboard base (Solid fill, slightly separated from screen) */}
            <path d="M3,23 h26 l-2,4 h-22 z" fill="currentColor" stroke="none" />
        </svg>
    ),
    LaptopSmallWhite: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Screen (Outline) */}
            <rect x="7" y="10" width="18" height="11" rx="1" />
            {/* Keyboard base (Outline) */}
            <path d="M5,21 h22 l-2,4 H7 Z" />
        </svg>
    ),
    NasVertical: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            <rect x="6" y="8" width="20" height="16" rx="2" />
            {/* HDD Vertical Slots */}
            <line x1="11" y1="8" x2="11" y2="24" />
            <line x1="16" y1="8" x2="16" y2="24" />
            <line x1="21" y1="8" x2="21" y2="24" />
            {/* Status LEDs */}
            <circle cx="8.5" cy="11" r="0.5" fill="currentColor" stroke="none" />
            <circle cx="13.5" cy="11" r="0.5" fill="currentColor" stroke="none" />
            <circle cx="18.5" cy="11" r="0.5" fill="currentColor" stroke="none" />
            <circle cx="23.5" cy="11" r="0.5" fill="currentColor" stroke="none" />
        </svg>
    ),
    DualMonitorPC: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Monitor 1 */}
            <rect x="1" y="10" width="11" height="8" rx="1" />
            <path d="M6.5,18 v3 M3,21 h7" />
            {/* Monitor 2 */}
            <rect x="13" y="10" width="11" height="8" rx="1" />
            <path d="M18.5,18 v3 M15,21 h7" />
            {/* Tower PC */}
            <rect x="25" y="8" width="6" height="13" rx="1" />
            <line x1="26" y1="12" x2="30" y2="12" />
        </svg>
    ),
    DualMonitorVerticalPC: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Stand Base */}
            <path d="M7,25 h8 M11,21 v4" />
            {/* Bottom Monitor */}
            <rect x="3" y="13" width="16" height="9" rx="1" />
            {/* Top Monitor */}
            <rect x="3" y="2" width="16" height="9" rx="1" />
            {/* Tower PC */}
            <rect x="22" y="6" width="8" height="20" rx="1" />
            <line x1="24" y1="10" x2="28" y2="10" />
            <line x1="24" y1="22" x2="28" y2="22" />
        </svg>
    ),
    LaptopFrontOpen: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Screen */}
            <rect x="6" y="6" width="20" height="12" rx="1" />
            {/* Keyboard Deck (Trapezoid perspective) */}
            <path d="M 4,20 L 28,20 L 31,26 L 1,26 Z" />
            {/* Trackpad */}
            <rect x="13" y="23" width="6" height="2" rx="0.5" />
            {/* Keys (simplified perspective lines) */}
            <line x1="7" y1="21.5" x2="25" y2="21.5" strokeWidth="1" />
            <line x1="6" y1="23.5" x2="11" y2="23.5" strokeWidth="1" />
            <line x1="21" y1="23.5" x2="26" y2="23.5" strokeWidth="1" />
        </svg>
    ),
    LaptopFlat: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Screen top half */}
            <rect x="6" y="2" width="20" height="13" rx="1" />
            {/* Keyboard bottom half */}
            <rect x="6" y="16" width="20" height="14" rx="1" />
            {/* Keyboard area with explicit key grid lines */}
            <rect x="8" y="18" width="16" height="7" rx="0.5" />
            <line x1="8" y1="20.5" x2="24" y2="20.5" strokeWidth="1" />
            <line x1="8" y1="23" x2="24" y2="23" strokeWidth="1" />
            <line x1="12" y1="18" x2="12" y2="25" strokeWidth="1" />
            <line x1="16" y1="18" x2="16" y2="25" strokeWidth="1" />
            <line x1="20" y1="18" x2="20" y2="25" strokeWidth="1" />
            {/* Trackpad */}
            <rect x="13" y="27" width="6" height="2" rx="0.5" />
        </svg>
    ),
    NasHorizontal: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            <rect x="6" y="8" width="20" height="16" rx="2" />
            {/* HDD Horizontal Slots */}
            <line x1="6" y1="13" x2="21" y2="13" />
            <line x1="6" y1="18" x2="21" y2="18" />
            {/* Control panel / LEDs on the right side */}
            <line x1="21" y1="8" x2="21" y2="24" />
            <circle cx="23.5" cy="11" r="0.5" fill="currentColor" stroke="none" />
            <circle cx="23.5" cy="14" r="0.5" fill="currentColor" stroke="none" />
            <circle cx="23.5" cy="17" r="0.5" fill="currentColor" stroke="none" />
            <circle cx="23.5" cy="20" r="0.5" fill="currentColor" stroke="none" />
        </svg>
    ),
    ScientificCalculator: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            <rect x="6" y="2" width="20" height="28" rx="2" />
            {/* Screen */}
            <rect x="8" y="5" width="16" height="6" rx="0.5" />
            {/* D-Pad / Nav */}
            <ellipse cx="16" cy="14" rx="3" ry="2" />
            {/* Grid of tiny buttons */}
            <path
                d="M9,18 h14 M9,21 h14 M9,24 h14 M9,27 h14"
                strokeWidth="1"
                strokeDasharray="2 2"
            />
        </svg>
    ),
    PocketComputer: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Body */}
            <rect x="2" y="10" width="28" height="12" rx="1" />
            {/* Screen (left side) */}
            <rect x="4" y="12" width="8" height="8" rx="0.5" />
            {/* Keyboard grid (right side) */}
            <path
                d="M14,13 h14 M14,16 h14 M14,19 h14"
                strokeWidth="1"
                strokeDasharray="1.5 2"
            />
        </svg>
    ),
    ComputeServer: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Large Enclosure */}
            <rect x="4" y="4" width="24" height="24" rx="1" />
            {/* Parallel Compute Blades */}
            <line x1="8" y1="4" x2="8" y2="20" strokeWidth="1.5" />
            <line x1="12" y1="4" x2="12" y2="20" strokeWidth="1.5" />
            <line x1="16" y1="4" x2="16" y2="20" strokeWidth="1.5" />
            <line x1="20" y1="4" x2="20" y2="20" strokeWidth="1.5" />
            <line x1="24" y1="4" x2="24" y2="20" strokeWidth="1.5" />
            {/* Divider */}
            <line x1="4" y1="20" x2="28" y2="20" />
            {/* Heavy Cooling Fans */}
            <circle cx="9" cy="24" r="2" />
            <circle cx="16" cy="24" r="2" />
            <circle cx="23" cy="24" r="2" />
        </svg>
    ),
    ControlTerminal: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Panel / Bezel */}
            <rect x="4" y="4" width="24" height="24" rx="2" />
            {/* Touch Screen */}
            <rect x="6" y="6" width="20" height="14" rx="1" />
            {/* Physical Buttons */}
            <circle cx="10" cy="24" r="2" />
            <circle cx="16" cy="24" r="2" />
            <circle cx="22" cy="24" r="2" />
        </svg>
    ),
    FATerminal: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* PLC/Controller Body */}
            <rect x="5" y="4" width="22" height="24" rx="1" />
            {/* Module Dividers */}
            <line x1="12" y1="4" x2="12" y2="28" />
            <line x1="19" y1="4" x2="19" y2="28" />
            {/* Status LEDs (Left Module) */}
            <circle cx="8.5" cy="8" r="1" fill="currentColor" stroke="none" />
            <circle cx="8.5" cy="12" r="1" fill="currentColor" stroke="none" />
            {/* IO Terminals (Middle & Right Modules) */}
            <rect x="14" y="20" width="3" height="4" />
            <rect x="21" y="20" width="3" height="4" />
            <line x1="14" y1="8" x2="17" y2="8" />
            <line x1="21" y1="8" x2="24" y2="8" />
        </svg>
    ),
    MonitoringDevice: (props) => (
        <svg
            viewBox="0 0 32 32"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Main Display (Quad split for CCTV) */}
            <rect x="2" y="6" width="28" height="18" rx="1" />
            <line x1="16" y1="6" x2="16" y2="24" />
            <line x1="2" y1="15" x2="30" y2="15" />
            {/* Stand */}
            <path d="M12,24 L10,28 H22 L20,24" />
        </svg>
    ),
};

// Badges (16x16 viewBox)
const Badges = {
    Database: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            <ellipse cx="8" cy="4" rx="6" ry="2" />
            <path d="M2,4 v4 a6,2 0 0,0 12,0 v-4" />
            <path d="M2,8 v4 a6,2 0 0,0 12,0 v-4" />
        </svg>
    ),
    Web: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            <circle cx="8" cy="8" r="7" />
            <ellipse cx="8" cy="8" rx="3" ry="7" />
            <line x1="1" y1="8" x2="15" y2="8" />
        </svg>
    ),
    App: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            <circle cx="8" cy="8" r="4" />
            {/* Gear teeth */}
            <path d="M8,1 v3 M8,12 v3 M1,8 h3 M12,8 h3 M3,3 l2,2 M11,11 l2,2 M3,13 l2,-2 M11,5 l2,-2" />
        </svg>
    ),
    Warning: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Triangle */}
            <path d="M8,1 L15,14 L1,14 Z" />
            {/* Exclamation */}
            <line x1="8" y1="5" x2="8" y2="10" />
            <circle cx="8" cy="12.5" r="0.5" fill="currentColor" stroke="none" />
        </svg>
    ),
    Test: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Flask */}
            <path d="M10,2 h-4 v5 l-4,7 h12 l-4,-7 Z" />
            {/* Opening */}
            <line x1="6" y1="2" x2="10" y2="2" />
            {/* Liquid level */}
            <path d="M4,11 h8" strokeDasharray="1 1" />
        </svg>
    ),
    Storage: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            <path d="M2,4 h4 l2,2 h6 v7 a1,1 0 0,1 -1,1 h-10 a1,1 0 0,1 -1,-1 Z" />
        </svg>
    ),
    Secure: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            <rect x="3" y="7" width="10" height="8" rx="1" />
            <path d="M5,7 v-3 a3,3 0 0,1 6,0 v3" />
            <circle cx="8" cy="11" r="1" fill="currentColor" stroke="none" />
        </svg>
    ),
    Firewall: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Brick wall outline */}
            <rect x="1" y="2" width="14" height="12" rx="1" />
            {/* Horizontal mortar lines */}
            <line x1="1" y1="6" x2="15" y2="6" strokeWidth="1" />
            <line x1="1" y1="10" x2="15" y2="10" strokeWidth="1" />
            {/* Vertical mortar lines (staggered) */}
            <line x1="5" y1="2" x2="5" y2="6" strokeWidth="1" />
            <line x1="11" y1="2" x2="11" y2="6" strokeWidth="1" />
            <line x1="8" y1="6" x2="8" y2="10" strokeWidth="1" />
            <line x1="4" y1="10" x2="4" y2="14" strokeWidth="1" />
            <line x1="12" y1="10" x2="12" y2="14" strokeWidth="1" />
        </svg>
    ),
    Maintenance: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Wrench head */}
            <path d="M11,2 A4,4 0 0,0 7,6 C7,6 10,9 10,9 A4,4 0 0,0 14,5 L12,7 L9,4 Z" />
            {/* Slim handle */}
            <path d="M8.5,7.5 L2.5,13.5 A1.5,1.5 0 0,0 4.5,15.5 L10.5,9.5" />
        </svg>
    ),
    Writing: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Pencil shape */}
            <path d="M12.5,3.5 L14,5 L5,14 L2,15 L3,12 Z" />
            {/* Eraser division */}
            <line x1="10.5" y1="2.5" x2="13.5" y2="5.5" strokeWidth="1" />
            {/* Wood division */}
            <line x1="4.5" y1="10.5" x2="7.5" y2="13.5" strokeWidth="1" />
        </svg>
    ),
    Programming: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Code Brackets */}
            <polyline points="5,4 1,8 5,12" />
            <polyline points="11,4 15,8 11,12" />
            <line x1="10" y1="2" x2="6" y2="14" />
        </svg>
    ),
    CAD: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Isometric Cube */}
            <polygon points="8,2 14,5 14,11 8,14 2,11 2,5" />
            <polyline points="2,5 8,8 14,5" />
            <line x1="8" y1="14" x2="8" y2="8" />
        </svg>
    ),
    Home: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* House */}
            <path d="M2,6 L8,1.5 L14,6" />
            <path d="M3,5.5 V14 H6 V10 H10 V14 H13 V5.5" />
        </svg>
    ),
    Lab: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Atom structure */}
            <ellipse cx="8" cy="8" rx="6.5" ry="2.5" transform="rotate(45 8 8)" />
            <ellipse cx="8" cy="8" rx="6.5" ry="2.5" transform="rotate(-45 8 8)" />
            <circle cx="8" cy="8" r="1.5" fill="currentColor" stroke="none" />
        </svg>
    ),
    Office: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Document */}
            <path d="M4,2 L9,2 L13,6 L13,13 A1,1 0 0,1 12,14 L4,14 A1,1 0 0,1 3,13 L3,3 A1,1 0 0,1 4,2 Z" />
            {/* Folded corner */}
            <path d="M9,2 L9,6 L13,6" />
            {/* Text lines */}
            <line x1="6" y1="9" x2="10" y2="9" />
            <line x1="6" y1="11" x2="8" y2="11" />
        </svg>
    ),
    Building: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Main building */}
            <rect x="3" y="2" width="10" height="14" rx="0.5" />
            {/* Windows */}
            <rect x="5" y="4" width="2" height="2" />
            <rect x="9" y="4" width="2" height="2" />
            <rect x="5" y="8" width="2" height="2" />
            <rect x="9" y="8" width="2" height="2" />
            {/* Door */}
            <rect x="6" y="12" width="4" height="4" />
        </svg>
    ),
    School: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Roof with a small clock tower shape */}
            <path d="M1,6 L8,1 L15,6" />
            <line x1="8" y1="1" x2="8" y2="4" />
            {/* Building Body */}
            <rect x="3" y="6" width="10" height="8" />
            {/* Door */}
            <rect x="6" y="10" width="4" height="4" />
            {/* Windows */}
            <rect x="4" y="7" width="2" height="2" strokeWidth="1" />
            <rect x="10" y="7" width="2" height="2" strokeWidth="1" />
        </svg>
    ),
    Shield: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            <path d="M8,1 L2,3 v4 c0,4 6,7 6,7 c0,0 6,-3 6,-7 V3 Z" />
        </svg>
    ),
    Scroll: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Left and right rolls */}
            <path d="M4,3 C4,2 6,2 6,3 V13 C6,14 4,14 4,13 Z" />
            <path d="M12,3 C12,2 14,2 14,3 V13 C14,14 12,14 12,13 Z" />
            {/* Paper spanning between rolls */}
            <line x1="6" y1="4" x2="12" y2="4" />
            <line x1="6" y1="12" x2="12" y2="12" />
            {/* Text lines */}
            <line x1="7" y1="6" x2="11" y2="6" strokeWidth="1" />
            <line x1="7" y1="8" x2="11" y2="8" strokeWidth="1" />
            <line x1="7" y1="10" x2="9" y2="10" strokeWidth="1" />
        </svg>
    ),
    Student: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Mortarboard hat (Academic dress) */}
            <path d="M1,6 L8,2 L15,6 L8,10 Z" />
            {/* Cap base */}
            <path d="M4,8.5 V11 C4,13 8,14 8,14 C8,14 12,13 12,11 V8.5" />
            {/* Tassel */}
            <line x1="14" y1="6.5" x2="14" y2="10" />
            <circle cx="14" cy="11" r="1" fill="currentColor" stroke="none" />
        </svg>
    ),
    Factory: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Sawtooth Roof */}
            <path d="M1,14 V8 L5,5 V8 L9,5 V8 L13,5 V14 Z" />
            {/* Chimney */}
            <line x1="11" y1="5" x2="11" y2="2" />
            <line x1="13" y1="5" x2="13" y2="2" />
            <line x1="10" y1="2" x2="14" y2="2" />
        </svg>
    ),
    RobotArm: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Base */}
            <line x1="4" y1="14" x2="10" y2="14" strokeWidth="2" />
            <line x1="7" y1="14" x2="7" y2="12" strokeWidth="2" />
            {/* Arm segments */}
            <line x1="7" y1="12" x2="11" y2="7" strokeWidth="1.5" />
            <line x1="11" y1="7" x2="5" y2="4" strokeWidth="1.5" />
            {/* Gripper */}
            <path d="M5,4 L3,2 M5,4 L7,2" strokeWidth="1" />
            {/* Joints */}
            <circle cx="7" cy="12" r="1.5" fill="currentColor" stroke="none" />
            <circle cx="11" cy="7" r="1.5" fill="currentColor" stroke="none" />
            <circle cx="5" cy="4" r="1.5" fill="currentColor" stroke="none" />
        </svg>
    ),
    Manipulator: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Base / Wrist */}
            <path d="M8,1 v5" />
            <rect x="5" y="6" width="6" height="3" rx="0.5" />
            {/* Gripper Fingers */}
            <path d="M5,9 v2 l-2,2 M11,9 v2 l2,2" />
            {/* Holding an object */}
            <circle cx="8" cy="13" r="1.5" fill="currentColor" stroke="none" />
        </svg>
    ),
    MillingMachine: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Spindle */}
            <rect x="5" y="1" width="6" height="4" rx="0.5" />
            {/* Tool */}
            <line x1="8" y1="5" x2="8" y2="10" />
            <path d="M7,7 l2,1 M7,9 l2,1" strokeWidth="1" />
            {/* Workpiece */}
            <rect
                x="6"
                y="10"
                width="4"
                height="3"
                fill="currentColor"
                stroke="none"
            />
            {/* Table */}
            <line x1="2" y1="14" x2="14" y2="14" strokeWidth="2" />
        </svg>
    ),
    Printer3D: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Frame */}
            <rect x="2" y="2" width="12" height="12" rx="1" />
            {/* X-axis gantry */}
            <line x1="2" y1="5" x2="14" y2="5" />
            {/* Extruder nozzle */}
            <polygon points="7,5 9,5 8,8" fill="currentColor" stroke="none" />
            {/* Printed object (layers) */}
            <line x1="5" y1="14" x2="11" y2="14" />
            <line x1="6" y1="12" x2="10" y2="12" />
            <line x1="7" y1="10" x2="9" y2="10" />
        </svg>
    ),
    NCLathe: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Chuck */}
            <rect x="1" y="4" width="4" height="8" rx="0.5" />
            {/* Workpiece (cylindrical with step) */}
            <path d="M5,6 h4 l2,2 v0 l-2,2 h-4 z" />
            {/* Cutting Tool (Bite) */}
            <path d="M11,10 l2,-2 h2 v5 h-4 z" />
            <circle cx="13" cy="11" r="0.5" fill="currentColor" stroke="none" />
        </svg>
    ),
    Sensor: (props) => (
        <svg
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >
            {/* Sensor Device (Node) */}
            <rect x="2" y="10" width="4" height="4" rx="1" />
            <circle cx="4" cy="12" r="1" fill="currentColor" stroke="none" />
            {/* Wireless / Detection Waves */}
            <path d="M7,9 A3.5,3.5 0 0,1 10.5,12.5" />
            <path d="M10,6 A7.5,7.5 0 0,1 14.5,12.5" />
        </svg>
    ),
};

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
