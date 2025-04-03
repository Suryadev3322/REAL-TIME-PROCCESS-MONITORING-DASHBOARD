def init_db():
    conn = sqlite3.connect("system_metrics.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS metrics 
                 (timestamp TEXT, cpu_usage REAL, memory_usage REAL, disk_usage REAL, network_sent REAL, network_received REAL)''')
    conn.commit()
    conn.close()

def collect_metrics():
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        net_io = psutil.net_io_counters()
        network_sent = net_io.bytes_sent
        network_received = net_io.bytes_recv
        
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        conn = sqlite3.connect("system_metrics.db")
        c = conn.cursor()
        c.execute("INSERT INTO metrics (timestamp, cpu_usage, memory_usage, disk_usage, network_sent, network_received) VALUES (?, ?, ?, ?, ?, ?)", 
                  (timestamp, cpu_usage, memory_usage, disk_usage, network_sent, network_received))
        conn.commit()
        conn.close()
        
        time.sleep(5)  # Collect data every 5 seconds

def get_latest_metrics():
    conn = sqlite3.connect("system_metrics.db")
    c = conn.cursor()
    c.execute("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 10")
    data = c.fetchall()
    conn.close()
    return data

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/metrics')
def metrics():
    data = get_latest_metrics()
    return jsonify(data)

if __name__ == '__main__':
    init_db()
    
    # Start background thread for collecting metrics
    metrics_thread = threading.Thread(target=collect_metrics, daemon=True)
    metrics_thread.start()
    
    app.run(debug=True)
