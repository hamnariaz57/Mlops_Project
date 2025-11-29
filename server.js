const express = require('express');
const path = require('path');
const axios = require('axios');
const fs = require('fs');
const morgan = require('morgan');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan('dev'));

// static files
app.use(express.static(path.join(__dirname, 'public')));

// simple logging to file
const logStream = fs.createWriteStream(path.join(__dirname, 'logs', 'requests.log'), { flags: 'a' });

app.get('/api/rate', async (req, res) => {
  const base = req.query.base || 'USD';
  const target = req.query.target || 'EUR';
  try {
    const response = await axios.get('https://api.exchangerate.host/latest', {
      params: { base, symbols: target }
    });
    const data = response.data;
    const rate = data && data.rates ? data.rates[target] : null;
    const out = {
      base,
      target,
      rate,
      fetched_at: data.date || new Date().toISOString()
    };
    // append to logfile
    logStream.write(JSON.stringify(out) + '\n');
    res.json(out);
  } catch (err) {
    console.error(err.message);
    res.status(500).json({ error: 'Failed to fetch rate' });
  }
});

// health
app.get('/health', (req, res) => res.json({ status: 'ok' }));

// fallback to index
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
