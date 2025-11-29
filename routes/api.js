const express = require('express');
const router = express.Router();
const axios = require('axios');

router.get('/rate', async (req, res) => {
  const base = req.query.base || 'USD';
  const target = req.query.target || 'EUR';
  try {
    const response = await axios.get('https://api.exchangerate.host/latest', { params: { base, symbols: target }});
    const data = response.data;
    const rate = data.rates ? data.rates[target] : null;
    res.json({ base, target, rate, fetched_at: data.date || new Date().toISOString() });
  } catch (err) {
    res.status(500).json({ error: 'fetch_failed' });
  }
});

module.exports = router;
