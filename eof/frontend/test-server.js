const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;

const server = http.createServer((req, res) => {
    // 1. Handle the Ticket Generation Mock Endpoint
    if (req.url === '/api/checkout/initiate' && req.method === 'POST') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        
        const mockResponse = {
            success: "true",
            ticket: "chkt_test_ticket_" + Math.random().toString(36).substr(2, 9)
        };
        console.log("[Node Test Server] Simulating Java backend -> Dispatched dynamic mock ticket token.");
        return res.end(JSON.stringify(mockResponse));
    }

    // 2. Exact Path Matching for the Astraa Sandbox Files
    let filePath = '.' + req.url;
    
    if (req.url === '/' || req.url === '/eof/frontend/checkout-test.html') {
        filePath = path.join(__dirname, 'checkout-test.html');
    } else if (req.url === '/eof/frontend/astraa-bridge.js') {
        filePath = path.join(__dirname, 'astraa-bridge.js');
    } else if (req.url.includes('moneris-checkout.html')) {
        // Force the server to look at the repository root folder
        filePath = path.join(__dirname, '../../moneris-checkout.html');
    }

    const extname = String(path.extname(filePath)).toLowerCase();
    const mimeTypes = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };
    const contentType = mimeTypes[extname] || 'application/octet-stream';

    fs.readFile(filePath, (error, content) => {
        if (error) {
            console.error(`[Node Test Server] 404 Not Found: ${req.url} -> Attempted path: ${filePath}`);
            res.writeHead(404, { 'Content-Type': 'text/html' });
            res.end('<h1>File Not Found</h1>', 'utf-8');
        } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content, 'utf-8');
        }
    });
});

server.listen(PORT, () => {
    console.log(`\n🚀 [Astraa Sandbox] Test server is running live!`);
    console.log(`👉 Open your browser and go to: http://localhost:${PORT}/eof/frontend/checkout-test.html\n`);
});
