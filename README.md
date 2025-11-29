# Realtime Exchange Rate RPS - Professional Dashboard (Option 3)

## Quick start

1. Extract the ZIP and open folder in VS Code.
2. Install dependencies:
```bash
npm install
```
3. Start the server:
```bash
npm start
```
4. Open http://localhost:3000 in your browser.

## What is included
- Express server (`server.js`)
- `/api/rate` endpoint fetching live USD -> EUR (configurable)
- Professional dashboard frontend (`public/index.html`) showing:
  - Latest exchange rate
  - Simple Rock-Paper-Scissors game
  - Historical small table (client-side)
- Logs saved to `logs/requests.log`

## Notes
- No API key required (uses https://api.exchangerate.host/latest)
- To change base/target currency, edit the frontend JS or server default.
