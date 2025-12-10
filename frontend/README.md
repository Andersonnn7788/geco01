# Frontend

This is the Next.js frontend application for the Infinity8 workspace booking system.

## Directory Structure

```
frontend/
├── app/              # Next.js app directory (pages and API routes)
├── lib/              # Shared utilities and configurations
├── public/           # Static assets
├── middleware.ts     # Next.js middleware
├── next.config.ts    # Next.js configuration
├── package.json      # Frontend dependencies
└── tsconfig.json     # TypeScript configuration
```

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000)

### Build

```bash
npm run build
npm start
```

## Environment Variables

Create a `.env` file in the frontend directory with the following variables:

```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_ADMIN_SECRET_KEY=your_admin_secret
NEXT_PUBLIC_BOOKING_API_URL=http://localhost:8000
```

See `.env.example` for a complete list of required environment variables.

## Features

- User authentication and authorization
- Space booking management
- Admin dashboard
- Real-time availability tracking
- Payment processing with Stripe
- AI-powered chatbot assistance
- Knowledge base management

## Tech Stack

- Next.js 16.0.7
- React 19
- TypeScript
- Tailwind CSS
- Supabase (Database & Auth)
- Stripe (Payments)
