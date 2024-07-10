#IMPORTS
from flask import Flask, request,jsonify
from flask_caching import Cache
import sqlite3
#SETUP
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
db = sqlite3.connect('snippets.db', check_same_thread=False)
db.execute('CREATE TABLE IF NOT EXISTS snippets (key TEXT PRIMARY KEY, snippet TEXT, explanation TEXT)')
#FLASK
@app.route("/")
def home():
    return """
        <html>
            <head>
                <title>Snippet Search</title>
                <style>
                ::placeholder {
                  color: white;
                  opacity: 1;
                }
                </style>
            </head>
            <body style="background-color: #333; color: white; text-align: center;">
                <br>
                <br>
                <h1>Snippet Search</h1>
                <form action="/search" method="GET">
                    <input type="text" name="query" placeholder=" Enter search term" style="background-color: grey;color:white;height:50px;width:350px">
                    <button type="submit" style="background-color: grey;color:white;height:50px;width:75px">Search</button>
                </form>
            </body>
        </html>
    """

@app.route("/search")
def search():
    query = request.args.get("query", "")
    results = []
    with sqlite3.connect("snippets.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, snippet, explanation FROM snippets WHERE snippet LIKE ? OR explanation LIKE ?", ("%" + query + "%", "%" + query + "%"))
        results = cursor.fetchall()
    output = ""
    resnum = 0
    if results == []:
        return f"""
            <html>
                <head>
                    <title>'{query}' not found</title>
                </head>
                <body style="background-color: #333; color: #eee; text-align: center;">
                    <h1>No results found</h1>
                    <p>There are no snippets with code or explainations containing '{query}'</p>
                </body>
            </html>
        """
    else:
        for result in results:
            key, snippet, explanation = result
            resnum += 1
            output += f"<h2>{resnum}. <a style='text-decoration: none;color: #00cc00;'  href='/snippets/{key}'>{key}</a></h2>"
        return f"""
            <html>
                <head>
                    <title>Search Results</title>
                </head>
                <body style="background-color: #333; color: #eee; text-align: center;">
                    <h1>Showing results for '{query}'</h1>
                    {output}
                </body>
            </html>
        """

@app.route("/snippets/<key>")
def snippet(key):
    result = None
    
    with sqlite3.connect("snippets.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, snippet, explanation FROM snippets WHERE key=?", (key,))
        result = cursor.fetchone()
    
    if result is None:
        return f"""
            <html>
                <head>
                    <title>Snippet Not Found</title>
                </head>
                <body style="background-color: #333; color: #eee; text-align: center;">
                    <h1>Snippet Not Found</h1>
                    <p>The snippet with key '{key}' could not be found.</p>
                </body>
            </html>
        """
    
    key, snippet, explanation = result
    
    return f"""
        <html>
            <head>
                <title>{key}</title>
                <style>
                .code-indented-borders {{
            border-style: inset;
            padding: 20px;
            background-color: grey;
            border-color: black;
            border-width: 1px;
            color: white;
            text-align: center;
            height: 75px;
            display: flex;
            top:120px;
            right:50px;
            left:50px;
            bottom:20px
      }}
                </style>
            </head>
            <body style="background-color: #333; color: #eee; text-align: center;">
                <h1 style='color: #00cc00;'>{key}</h1>
                <div class="center">
                <p class="code-indented-borders">{snippet}</p>
                <p class="code-indented-borders">{explanation}</p>
                </div>
            </body>
        </html>
    """
@app.route('/add', methods=['POST'])
def add_snippet():
    data = request.get_json()
    key = data.get('key')
    snippet = data.get('snippet')
    explanation = data.get('explanation')
    if key and snippet and explanation:
        db.execute('INSERT OR REPLACE INTO snippets (key, snippet, explanation) VALUES (?, ?, ?)', (key, snippet, explanation))
        db.commit()
        return jsonify({"result":f"Snippet with key '{key}' added successfully."})
    else:
        return jsonify({"result":"Invalid request."})
@app.route('/get/<key>', methods=['GET'])
@cache.cached(timeout=300)
def get_snippet(key):
    row = db.execute('SELECT snippet, explanation FROM snippets WHERE key = ?', (key,)).fetchone()
    if row:
        snippet, explanation = row
        return jsonify({"result":{"code":snippet,"explanation":explanation}}), 200
    else:
        return jsonify({"result":f"No snippet found with key '{key}'."}), 300
@app.route('/delete/<key>', methods=['DELETE'])
@cache.cached(timeout=300)
def delete_snippet(key):
    db.execute('DELETE FROM snippets WHERE key = ?', (key,))
    db.commit()
    return jsonify({"result":f"Snippet with key '{key}' deleted successfully."})
#RUN
if __name__ == '__main__':
    app.run("0.0.0.0")
