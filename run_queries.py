import os
import re
import sqlite3
import pandas as pd

def parse_queries(sql_content):
    # Regex to split by semicolon while ignoring comments
    # We will remove single-line comments first, then split by semicolon
    cleaned_sql = re.sub(r'--.*?\n', '\n', sql_content)
    
    # Split by semicolon
    raw_statements = cleaned_sql.split(';')
    queries = []
    
    for stmt in raw_statements:
        stmt_cleaned = stmt.strip()
        if stmt_cleaned:
            queries.append(stmt_cleaned)
            
    return queries

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "bluestock_mf.db")
    sql_path = os.path.join(script_dir, "queries.sql")
    
    if not os.path.exists(sql_path):
        print(f"Error: {sql_path} does not exist.")
        return
        
    print("=== Executing Analytical SQL Queries on bluestock_mf.db ===\n")
    
    with open(sql_path, 'r') as f:
        sql_content = f.read()
        
    # Extract queries with titles
    # Find block comments/single line comments preceding each query for titles
    query_blocks = re.split(r';', sql_content)
    
    conn = sqlite3.connect(db_path)
    
    query_idx = 1
    for block in query_blocks:
        block = block.strip()
        if not block:
            continue
            
        # Try to find a title from comments
        title_match = re.findall(r'--\s*([0-9]+\.\s*.*?)\n', block)
        if title_match:
            title = title_match[0]
        else:
            title_match_simple = re.findall(r'--\s*(.*?)\n', block)
            if title_match_simple:
                title = f"Query {query_idx}: {title_match_simple[0]}"
            else:
                title = f"Query {query_idx}"
                
        # Clean query text
        # Remove comments inside the execution block
        query_text = re.sub(r'--.*?\n', '\n', block).strip()
        if not query_text:
            continue
            
        print("=" * 80)
        print(f"[{query_idx}] {title}")
        print("=" * 80)
        print(f"SQL:\n{query_text}\n")
        
        try:
            df = pd.read_sql_query(query_text, conn)
            # Limit printing to 15 rows to keep it readable, but print shape
            print(f"Result Shape: {df.shape[0]} rows, {df.shape[1]} columns")
            if df.empty:
                print("No results returned.")
            else:
                # Format print nicely
                print(df.head(15).to_string(index=False))
                if len(df) > 15:
                    print(f"... and {len(df) - 15} more rows.")
            print("\n")
            query_idx += 1
        except Exception as e:
            print(f"Error running query: {e}\n")
            
    conn.close()
    print("=== All Queries Executed ===")

if __name__ == "__main__":
    main()
