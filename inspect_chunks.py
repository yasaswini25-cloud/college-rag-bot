import sqlite3
db = sqlite3.connect("server/college_rag.db")
rows = db.execute("""
    SELECT
        d.title,
        c.chunk_index,
        c.page_number,
        substr(c.content, 1, 500)
    FROM document_chunks c
    JOIN documents d ON c.document_id = d.id
    WHERE d.title LIKE '%Admission Guidelines%'
    ORDER BY c.chunk_index
""").fetchall()
for title, chunk_index, page_number, content in rows:
    print(f"\n--- Chunk {chunk_index} | Page {page_number} ---")
    print(content)
db.close()
