from flask import Flask, render_template_string
import sqlite3

app = Flask(__name__)

# HTML template including DataTables
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Papers</title>
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.5.1.js"></script>
    <!-- DataTables CSS -->
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.css">
    <!-- DataTables JS -->
    <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.js"></script>
    <script>
        $(document).ready(function() {
            $('#papers').DataTable();
        });
    </script>
</head>
<body>
    <table id="papers" class="display" style="width:100%">
        <thead>
            <tr>
                <th>Date</th>
                <th>Authors</th>
                <th>Title</th>
                <th>Keyword</th>
            </tr>
        </thead>
        <tbody>
            {% for paper in papers %}
            <tr>
                <td>{{ paper['date'] }}</td>
                <td>{{ paper['authors'] }}</td>
                <td>{{ paper['title'] }}</td>
                <td>{{ paper['keyword'] }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
'''

def get_papers():
    # Connect to the database and fetch data
    conn = sqlite3.connect('Papers.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT date, authors, title, keyword FROM Papers")
    papers = cur.fetchall()
    conn.close()
    return papers

@app.route('/')
def index():
    papers = get_papers()
    return render_template_string(HTML_TEMPLATE, papers=papers)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
