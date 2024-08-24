from http.server import HTTPServer, SimpleHTTPRequestHandler
import json


WIDGET_ID = 'easyproxy-widget'

def generate_widget_script(origin):
    return f"""
(function() {{
  const WIDGET_ID = '{WIDGET_ID}';
  const API_URL = '{origin}';

  function createWidget() {{
    const widget = document.createElement('div');
    widget.id = WIDGET_ID;
    widget.innerHTML = `
      <button id="${{WIDGET_ID}}-button">Analyze 2IP</button>
      <div id="${{WIDGET_ID}}-status"></div>
    `;
    document.body.appendChild(widget);

    const style = document.createElement('style');
    style.textContent = `
      #${{WIDGET_ID}} {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 200px;
        background-color: #f0f0f0;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: Arial, sans-serif;
        z-index: 10000;
      }}
      #${{WIDGET_ID}}-button {{
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
      }}
      #${{WIDGET_ID}}-status {{
        margin-top: 10px;
        font-size: 14px;
        text-align: center;
      }}
    `;
    document.head.appendChild(style);

    document.getElementById(`${{WIDGET_ID}}-button`).addEventListener('click', analyze2IP);
  }}

  async function analyze2IP() {{
    const statusElement = document.getElementById(`${{WIDGET_ID}}-status`);
    statusElement.textContent = 'Analyzing...';

    try {{
      const response = await fetch(`${{API_URL}}/analyze`);
      const result = await response.json();
      
      // Находим форму на странице easyproxy.tech
      const form = document.querySelector('form');
      const urlInput = form ? form.querySelector('input[name="url"]') : null;
      const submitButton = form ? form.querySelector('input[type="submit"]') : null;

      if (urlInput && submitButton) {{
        urlInput.value = 'https://www.2ip.ru';
        submitButton.click();

        // Отправляем сообщение родительскому окну (если виджет в iframe)
        window.parent.postMessage({{
          type: 'postSearchForm',
          message: 'https://www.2ip.ru'
        }}, '*');

        statusElement.textContent = result.message;
      }} else {{
        statusElement.textContent = 'Error: Form not found';
      }}
    }} catch (error) {{
      statusElement.textContent = 'Error occurred during analysis';
    }}

    setTimeout(() => {{
      statusElement.textContent = '';
    }}, 2000);
  }}

  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', createWidget);
  }} else {{
    createWidget();
  }}
}})();
"""

def generate_html():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EasyProxy Widget</title>
</head>
<body>
    <h1>EasyProxy Widget</h1>
    <p>To use the widget, add the following script tag to your website:</p>
    <pre><code>&lt;script src="http://localhost:8000/widget.js" async&gt;&lt;/script&gt;</code></pre>
    <p>Replace "localhost:8000" with the actual domain when deployed.</p>
    <script src="/widget.js" async></script>
</body>
</html>
"""

class WidgetHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        SimpleHTTPRequestHandler.end_headers(self)

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(generate_html().encode())
        elif self.path == '/widget.js':
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            origin = f"http://{self.headers['Host']}"
            self.wfile.write(generate_widget_script(origin).encode())
        elif self.path == '/analyze':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"status": "success", "message": "Analysis of https://www.2ip.ru completed"})
            self.wfile.write(response.encode())
        else:
            self.send_error(404)

def run(server_class=HTTPServer, handler_class=WidgetHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on http://localhost:{port}")
    httpd.serve_forever()


def run(server_class=HTTPServer, handler_class=WidgetHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()


