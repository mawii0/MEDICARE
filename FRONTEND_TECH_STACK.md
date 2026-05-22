# Frontend Technical Stack

This document describes the frontend technologies used in this project.

## Core Framework
- React 18.3.1
- TypeScript (used across app and server source files)
- Vite 6.3.5 for build/dev tooling
- @vitejs/plugin-react for React integration

## UI and Styling
- Tailwind CSS 4.1.12
- @tailwindcss/vite plugin for Tailwind + Vite integration
- CSS variable based design tokens in `src/styles/theme.css`
- Global and layered style entry points in `src/styles/`

## Component System
- shadcn/ui-style component structure in `src/app/components/ui/`
- Radix UI primitives (accordion, dialog, popover, tabs, etc.)
- class-variance-authority + clsx + tailwind-merge for variant and class composition

## Motion and UX
- motion (Motion One for React) for screen transitions and animations
- sonner for toast notifications
- lucide-react for iconography
- canvas-confetti for celebratory UI effects

## Forms and Input
- react-hook-form for form state management
- input-otp for OTP input handling
- react-day-picker for date picking

## Navigation and App Flow
- Internal screen-based navigation state in `src/app/App.tsx`
- react-router is available as a dependency for route-based expansion

## Data and API Layer
- Frontend API/auth helpers in `src/lib/api.ts` and `src/lib/auth.tsx`
- Vite dev proxy forwards `/api` to `http://localhost:3001` (configured in `vite.config.ts`)

## Domain-Specific Frontend Libraries
- leaflet for map-based pharmacy/location UI
- recharts for charting and data visualization
- react-dnd + react-dnd-html5-backend for drag-and-drop interactions
- embla-carousel-react and react-slick for carousel/slider experiences

## Build and Run Commands
```bash
npm install
npm run dev
npm run build
```

## Frontend Source Layout (High Level)
- `src/main.tsx`: React entry point
- `src/app/App.tsx`: main app shell and screen orchestration
- `src/app/components/`: feature screens and reusable UI
- `src/lib/`: API and auth client utilities
- `src/styles/`: global styles, Tailwind layers, and theme tokens
