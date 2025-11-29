const fs = require('fs');
const path = require('path');
const logfile = path.join(__dirname, '..', 'logs', 'requests.log');

function append(obj) {
  try {
    fs.appendFileSync(logfile, JSON.stringify(obj) + '\n');
  } catch (err) {
    console.error('Log write failed', err);
  }
}

module.exports = { append };
