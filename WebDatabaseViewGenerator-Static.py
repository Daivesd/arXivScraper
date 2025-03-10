import sqlite3

def generate_html():
    # Connect to the database (read-only)
    conn = sqlite3.connect('Papers.db')
    cur = conn.cursor()
    
    # Query the desired columns (adjust table name if needed)
    cur.execute("SELECT date, authors, title, keyword FROM Papers")
    rows = cur.fetchall()
    conn.close()

    # Build the HTML content with DataTables integration from CDN
    html = '''
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
    '''

    # Populate table rows
    for row in rows:
        html += '<tr>'
        html += f'<td>{row[0]}</td>'
        html += f'<td>{row[1]}</td>'
        html += f'<td>{row[2]}</td>'
        html += f'<td>{row[3]}</td>'
        html += '</tr>'
    
    # Close the HTML content
    html += '''
            </tbody>
        </table>
    </body>
    </html>
    '''

    # Write the HTML to a file
    with open("papers.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML page generated as papers.html")

if __name__ == "__main__":
    generate_html()
