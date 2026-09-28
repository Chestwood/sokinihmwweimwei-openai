#!/usr/bin/env python3
import json, os, sys, urllib.error, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
HOST = '127.0.0.1'
PORT = int(os.environ.get('PORT', '8787'))
MODEL = os.environ.get('OPENAI_MODEL', 'gpt-5.6-luna')


def load_env():
    env = APP_DIR / '.env'
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


load_env()
API_KEY = os.environ.get('OPENAI_API_KEY', '').strip()

SCHEMA = {
    'type': 'object',
    'properties': {
        'benchmark': {'type': 'string'},
        'objective': {'type': 'string'},
        'vocabulary': {'type': 'string'},
        'crossLinkages': {'type': 'string'},
        'textbook': {'type': 'string'},
        'supplies': {'type': 'string'},
        'reflection': {'type': 'string'},
        'future': {'type': 'string'},
        'steps': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'phase': {'type': 'string'},
                    'teacher': {'type': 'string'},
                    'student': {'type': 'string'}
                },
                'required': ['phase', 'teacher', 'student'],
                'additionalProperties': False
            }
        }
    },
    'required': ['benchmark', 'objective', 'vocabulary', 'crossLinkages', 'textbook', 'supplies', 'reflection', 'future', 'steps'],
    'additionalProperties': False
}


def make_prompt(subject, grade, topic):
    return f'''You are a master curriculum designer creating a hyper-explicit, zero-guesswork lesson plan for a substitute or green teacher in Pohnpei.
Subject: {subject}
Grade: {grade}
Topic: {topic}

CRITICAL PEDAGOGICAL INSTRUCTIONS:
1. Do NOT use generic templates or repeating placeholder sentences across different topics.
2. If Subject is Math: Use Concrete-Representational-Abstract (CRA) model with explicit worked numerical examples and step-by-step board writing routines.
3. If Subject is Science/Social Studies: Focus on visual process diagrams, cause-and-effect relationships, and domain-specific vocabulary routines.
4. If Subject is Reading/Writing: Provide explicit text modeling ("I Do"), text annotation steps, and graphic organizer modeling.
5. Provide VERBATIM teacher read-aloud scripts and TOPIC-SPECIFIC ESL sentence stems for students.
6. Make the lesson appropriate for ESL students. Use clear, concrete language and specific teacher/student actions.
7. Do not invent a textbook title beyond the requested Pohnpei State Curriculum Series wording.

Return only the requested JSON object. Do not add markdown or commentary.

Create these exact fields:
- benchmark: standard/benchmark statement specifically connected to the topic. Do not pretend to know an official code if you do not know it; give the benchmark wording instead.
- objective: 1-2 measurable SMART/Bloom objectives.
- vocabulary: 6-8 topic-specific academic terms.
- crossLinkages: 1-2 sentences connecting the lesson to another subject or real-life context.
- textbook: "Pohnpei State Curriculum Series ({grade}), Unit on {topic}"
- supplies: specific physical materials needed.
- reflection: strengths and weaknesses to watch for during this lesson.
- future: a practical reteach/extension plan.
- steps: exactly these five phases:
  1. Pre-Assessment (Engage Me) - 5-7 min
  2. Show Me (I Do) - 10-12 min
  3. Help Me (We Do) - 15 min
  4. Post Assessment (Let Me) - 5-7 min
  5. Wrap Up & Homework - 3 min

For every step, include concrete teacher actions, board setup, exact teacher words where useful, IEP/ESL supports, student actions, and topic-specific ESL speaking stems.''' 


def extract_output_text(data):
    if isinstance(data.get('output_text'), str) and data['output_text'].strip():
        return data['output_text']
    pieces = []
    for item in data.get('output', []) or []:
        for content in item.get('content', []) or []:
            if content.get('type') == 'output_text' and isinstance(content.get('text'), str):
                pieces.append(content['text'])
    return ''.join(pieces)


def generate(subject, grade, topic):
    if not API_KEY:
        raise RuntimeError('OpenAI API key is not set. Run setup.sh first.')
    prompt = make_prompt(subject, grade, topic)
    payload = {
        'model': MODEL,
        'input': prompt,
        'text': {
            'format': {
                'type': 'json_schema',
                'name': 'lesson_plan',
                'strict': True,
                'schema': SCHEMA
            }
        }
    }
    req = urllib.request.Request(
        'https://api.openai.com/v1/responses',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            data = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            detail = json.loads(body).get('error', {}).get('message', body)
        except Exception:
            detail = body
        raise RuntimeError(f'OpenAI error ({e.code}): {detail}')
    except urllib.error.URLError as e:
        raise RuntimeError(f'Could not reach OpenAI: {e.reason}')

    text = extract_output_text(data)
    if not text:
        raise RuntimeError('OpenAI returned no lesson-plan text.')
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise RuntimeError('OpenAI returned an unexpected response. Please try again.')


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, content_type='application/json; charset=utf-8'):
        raw = body if isinstance(body, bytes) else body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            try:
                html = (APP_DIR / 'index.html').read_bytes()
                self._send(200, html, 'text/html; charset=utf-8')
            except Exception as e:
                self._send(500, json.dumps({'error': str(e)}))
        elif self.path == '/api/health':
            self._send(200, json.dumps({'ok': True, 'model': MODEL, 'keyConfigured': bool(API_KEY)}))
        else:
            self._send(404, json.dumps({'error': 'Not found'}))

    def do_POST(self):
        if self.path != '/api/generate-lesson':
            self._send(404, json.dumps({'error': 'Not found'}))
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            body = self.rfile.read(length)
            data = json.loads(body.decode('utf-8'))
            subject = str(data.get('subject', '')).strip()
            grade = str(data.get('grade', '')).strip()
            topic = str(data.get('topic', '')).strip()
            if not topic:
                raise ValueError('Please enter a lesson topic.')
            result = generate(subject, grade, topic)
            self._send(200, json.dumps(result, ensure_ascii=False))
        except ValueError as e:
            self._send(400, json.dumps({'error': str(e)}))
        except Exception as e:
            self._send(500, json.dumps({'error': str(e)}))

    def log_message(self, fmt, *args):
        sys.stdout.write('%s - %s\n' % (self.address_string(), fmt % args))
        sys.stdout.flush()


if __name__ == '__main__':
    print(f'Sokinihmwweimwei running at http://{HOST}:{PORT}')
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
