from flask import Flask, request, jsonify
import psycopg2
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允許 Dify 跨域呼叫

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'db'), # 預設連線到 docker-compose 的 db service
        database=os.environ.get('DB_NAME', 'dify'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASS', 'difyai123456')
    )
    return conn

@app.route('/companies', methods=['GET'])
def get_companies():
    industry = request.args.get('industry')
    limit = request.args.get('limit', 10)
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    if industry:
        cur.execute('SELECT rank, name, symbol, industry, market_cap_usd_billions, country FROM public_companies WHERE industry = %s ORDER BY market_cap_usd_billions DESC LIMIT %s', (industry, limit))
    else:
        cur.execute('SELECT rank, name, symbol, industry, market_cap_usd_billions, country FROM public_companies ORDER BY market_cap_usd_billions DESC LIMIT %s', (limit,))
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    companies = []
    for row in rows:
        companies.append({
            "rank": row[0],
            "name": row[1],
            "symbol": row[2],
            "industry": row[3],
            "market_cap": f"${row[4]} B",
            "country": row[5]
        })
        
    return jsonify(companies)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
