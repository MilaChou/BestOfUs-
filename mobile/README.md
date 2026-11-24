# BestOfUs — mobile app

Expo (React Native + TypeScript) app for Android (and later iOS).
It talks to the FastAPI backend in the parent folder.

## Run

1. Start the backend so the phone can reach it (in the project root):

   ```bash
   uv run fastapi dev --host 0.0.0.0
   ```

2. In this folder, the first time only:

   ```bash
   npm install
   ```

3. Start the app:

   ```bash
   npx expo start
   ```

   Scan the QR code with **Expo Go** (Android), or press `w` to open it in the browser.

The phone and the Mac must be on the same Wi-Fi. The app finds the backend by itself
(same computer as Expo, port 8000). To point it somewhere else, create `.env.local`:

```
EXPO_PUBLIC_API_URL=http://192.168.0.29:8000
```

## Checks

```bash
npx tsc --noEmit
npx expo lint
```

## Structure

- `src/app/` — screens (Expo Router: every file is a screen, `_layout.tsx` are navigators)
- `src/auth/` — who is signed in and their couple
- `src/lib/` — API client, token storage, types, Russian labels
- `src/components/` — shared UI pieces and colors
