import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Custom plugin to serve /api/questionnaire and /api/dashboard GET and POST requests
const apiPlugin = () => ({
  name: 'api-plugin',
  configureServer(server) {
    server.middlewares.use((req, res, next) => {
      if (req.url === '/api/questionnaire') {
        const filePath = path.resolve(__dirname, 'src/data/questionnaire.json');
        
        if (req.method === 'GET') {
          res.setHeader('Content-Type', 'application/json');
          if (fs.existsSync(filePath)) {
            try {
              const content = fs.readFileSync(filePath, 'utf-8');
              const parsedData = JSON.parse(content);
              
              // Load answers from answers.json if it exists and merge it
              const answersPath = path.resolve(__dirname, 'src/data/answers.json');
              if (fs.existsSync(answersPath)) {
                try {
                  const answersContent = fs.readFileSync(answersPath, 'utf-8');
                  if (answersContent.trim()) {
                    parsedData.answers = JSON.parse(answersContent);
                  }
                } catch (e) {
                  console.error('Error reading answers.json:', e);
                }
              }
              
              res.end(JSON.stringify(parsedData, null, 2));
            } catch (err) {
              res.statusCode = 500;
              res.end(JSON.stringify({ error: 'Failed to read questionnaire data' }));
            }
          } else {
            res.statusCode = 404;
            res.end(JSON.stringify({ error: 'File not found' }));
          }
          return;
        }
        
        if (req.method === 'POST') {
          let body = '';
          req.on('data', chunk => {
            body += chunk.toString();
          });
          req.on('end', () => {
            try {
              const data = JSON.parse(body);
              let existingData = {};
              if (fs.existsSync(filePath)) {
                try {
                  const content = fs.readFileSync(filePath, 'utf-8');
                  if (content.trim()) {
                    existingData = JSON.parse(content);
                  }
                } catch (e) {
                  console.error('Error reading existing questionnaire:', e);
                }
              }
              
              // Extract and save answers separately to answers.json
              if (data.answers) {
                const answersPath = path.resolve(__dirname, 'src/data/answers.json');
                fs.writeFileSync(answersPath, JSON.stringify(data.answers, null, 2), 'utf-8');
                delete data.answers;
              }
              if (existingData.answers) {
                delete existingData.answers;
              }
              
              const mergedData = {
                ...existingData,
                ...data,
                questions: (data.questions && data.questions.length > 0) ? data.questions : (existingData.questions || [])
              };

              fs.writeFileSync(filePath, JSON.stringify(mergedData, null, 2), 'utf-8');
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({ success: true }));
            } catch (error) {
              console.error('API Error parsing JSON payload:', error);
              res.statusCode = 400;
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({ error: 'Invalid JSON payload' }));
            }
          });
          return;
        }
      }

      if (req.url === '/api/dashboard') {
        const filePath = path.resolve(__dirname, 'src/data/dashboard.json');
        
        if (req.method === 'GET') {
          res.setHeader('Content-Type', 'application/json');
          if (fs.existsSync(filePath)) {
            const content = fs.readFileSync(filePath, 'utf-8');
            res.end(content);
          } else {
            res.statusCode = 404;
            res.end(JSON.stringify({ error: 'File not found' }));
          }
          return;
        }
        
        if (req.method === 'POST') {
          let body = '';
          req.on('data', chunk => {
            body += chunk.toString();
          });
          req.on('end', () => {
            try {
              const data = JSON.parse(body);
              let existingData = {};
              if (fs.existsSync(filePath)) {
                try {
                  const content = fs.readFileSync(filePath, 'utf-8');
                  if (content.trim()) {
                    existingData = JSON.parse(content);
                  }
                } catch (e) {
                  console.error('Error reading existing dashboard:', e);
                }
              }
              
              const mergedData = {
                ...existingData,
                ...data,
                answers: {
                  ...existingData.answers,
                  ...data.answers,
                  last_updated: new Date().toISOString().split('T')[0]
                }
              };

              fs.writeFileSync(filePath, JSON.stringify(mergedData, null, 2), 'utf-8');
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({ success: true, data: mergedData }));
            } catch (error) {
              console.error('API Error parsing JSON payload:', error);
              res.statusCode = 400;
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({ error: 'Invalid JSON payload' }));
            }
          });
          return;
        }
      }

      next();
    });
  }
});

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    apiPlugin()
  ],
  server: {
    watch: {
      ignored: ['**/src/data/questionnaire.json', '**/src/data/dashboard.json', '**/src/data/answers.json']
    }
  }
})

