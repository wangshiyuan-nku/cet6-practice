"""
CET-6 词汇练习 - 桌面版
双击 .exe 启动，独立窗口，无浏览器边框
"""
import os, sys, json, threading, webbrowser, subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler
import tempfile, shutil

if getattr(sys, 'frozen', False):
    # Bundled data files are extracted to sys._MEIPASS; writable files go next to .exe
    DATA_DIR = sys._MEIPASS
    USER_DIR = os.path.dirname(sys.executable)
else:
    DATA_DIR = os.path.dirname(os.path.abspath(__file__))
    USER_DIR = DATA_DIR

PORT = 19988


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self._serve_main()
        elif self.path == '/api/save':
            self.send_response(200)
            self.end_headers()
        elif self.path == '/api/load':
            self._serve_progress()
        else:
            # Serve static files from DATA_DIR (bundled in .exe or local dir)
            path = os.path.join(DATA_DIR, self.path.lstrip('/'))
            if os.path.exists(path):
                self.send_response(200)
                ct = self._mime(path)
                self.send_header('Content-Type', ct)
                self.end_headers()
                with open(path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)

    def _serve_main(self):
        html_path = os.path.join(DATA_DIR, 'index.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Inject progress bridge: progress file lives in USER_DIR (next to .exe)
        progress_path = os.path.join(USER_DIR, 'cet6_progress.json').replace('\\', '\\\\')
        bridge = f'''
<script>
(function(){{
    var PP = '{progress_path}';
    setTimeout(function(){{
        fetch('/api/load').then(r=>r.text()).then(t=>{{
            if(t) localStorage.setItem('cet6_progress', t);
        }});
    }}, 500);
    var _set = Storage.prototype.setItem;
    Storage.prototype.setItem = function(k,v){{
        _set.call(this, k, v);
        if(k==='cet6_progress') fetch('/api/save',{{method:'POST',body:v}});
    }};
}})();
</script>
'''
        html = html.replace('</body>', bridge + '\n</body>')

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def _serve_progress(self):
        progress_path = os.path.join(USER_DIR, 'cet6_progress.json')
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        if os.path.exists(progress_path):
            with open(progress_path, 'r', encoding='utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))
        else:
            self.wfile.write(b'')

    def do_POST(self):
        if self.path.startswith('/api/save'):
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length).decode('utf-8')
            progress_path = os.path.join(USER_DIR, 'cet6_progress.json')
            with open(progress_path, 'w', encoding='utf-8') as f:
                f.write(data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'ok')
        else:
            self.send_error(404)

    def log_message(self, *args):
        pass

    @staticmethod
    def _mime(path):
        ext = os.path.splitext(path)[1].lower()
        return {
            '.html': 'text/html; charset=utf-8',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.css': 'text/css',
            '.png': 'image/png',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
        }.get(ext, 'application/octet-stream')


def find_chrome():
    """Find Chrome/Edge installation for --app mode."""
    paths = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'),
        os.path.expandvars(r'%PROGRAMFILES%\Google\Chrome\Application\chrome.exe'),
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def start_server():
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    server.serve_forever()


if __name__ == '__main__':
    # Start HTTP server in background thread
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    url = f'http://127.0.0.1:{PORT}'

    # Try Chrome --app mode first (standalone window, no browser UI)
    chrome = find_chrome()
    if chrome:
        try:
            subprocess.Popen([chrome, f'--app={url}', '--window-size=900,700'])
            print(f'Opened in app mode')
        except:
            webbrowser.open(url)
    else:
        webbrowser.open(url)

    # HTTP save endpoint: intercept localStorage saves from the page
    # The bridge script in index.html will POST to /api/save

    print(f'CET-6 练习工具已启动: {url}')
    print('关闭此窗口即可退出程序')

    # Keep main thread alive
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
