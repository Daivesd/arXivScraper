import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Papers.db")

def print_all_entries():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT date, authors, title, url FROM papers")
    
    papers = cursor.fetchall()
    if papers:
        print("All Papers in Database:")
        for paper in papers:
            print(f"Date: {paper[0]}, Authors: {paper[1]}, Title: {paper[2]}, URL: {paper[3]}\n")
    else:
        print("No entries found in the database.")

    conn.close()

def check_for_duplicates():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url, COUNT(*) FROM papers GROUP BY url HAVING COUNT(*) > 1")

    duplicates = cursor.fetchall()
    if duplicates:
        print("Duplicate Entries Found:")
        for url, count in duplicates:
            print(f"URL: {url} appears {count} times.")
    else:
        print("No duplicate entries found.")

    conn.close()

if __name__ == "__main__":
    print_all_entries()
    check_for_duplicates()
