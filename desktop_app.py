"""
CET-6 词汇练习 - 桌面版
打包为单个 .exe，双击启动独立窗口
"""
import os, sys, json

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import webview

# Read HTML
with open(os.path.join(BASE_DIR, 'index.html'), 'r', encoding='utf-8') as f:
    html = f.read()

# Inject data inline (pywebview renders HTML as string, can't load relative scripts)
with open(os.path.join(BASE_DIR, 'data.js'), 'r', encoding='utf-8') as f:
    data_js = f.read()
with open(os.path.join(BASE_DIR, 'index_data.js'), 'r', encoding='utf-8') as f:
    index_js = f.read()

html = html.replace('<script src="data.js"></script>', '<script>' + data_js + '</script>')
html = html.replace('<script src="index_data.js"></script>', '<script>' + index_js + '</script>')

# File-based progress sync
progress_path = os.path.join(BASE_DIR, 'cet6_progress.json')

class API:
    def save(self, data):
        with open(progress_path, 'w', encoding='utf-8') as f:
            f.write(data)
        return 'ok'

    def load(self):
        if os.path.exists(progress_path):
            with open(progress_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ''

api = API()

# Inject progress bridge: auto-sync localStorage to file
bridge = '''
<script>
window.addEventListener('pywebviewready', function() {
    try {
        var data = pywebview.api.load();
        if (data) localStorage.setItem('cet6_progress', data);
    } catch(e) {}
    // Intercept localStorage.setItem for cet6_progress to sync to file
    var origSetItem = Storage.prototype.setItem;
    Storage.prototype.setItem = function(key, value) {
        origSetItem.call(this, key, value);
        if (key === 'cet6_progress') {
            try { pywebview.api.save(value); } catch(e) {}
        }
    };
});
</script>
'''
html = html.replace('</body>', bridge + '\n</body>')

webview.create_window(
    title='CET-6 词汇练习', html=html, js_api=api,
    width=900, height=700, min_size=(600, 400)
)
webview.start(debug=False)
