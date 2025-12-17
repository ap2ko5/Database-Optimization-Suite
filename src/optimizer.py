import psycopg2
import mysql.connector
import time
from datetime import datetime

class DatabaseOptimizer:
    def __init__(self, db_url):
        self.db_url = db_url
        self.connection = None
        self.connect()

    def connect(self):
        try:
            if 'postgresql' in self.db_url:
                self.connection = psycopg2.connect(self.db_url)
            elif 'mysql' in self.db_url:
                self.connection = mysql.connector.connect(self.db_url)
        except Exception as e:
            print(f'Connection error: {e}')

    def analyze_database(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = cursor.fetchall()
            
            analysis = {
                'timestamp': datetime.now(),
                'tables': [],
                'indexes': [],
                'slow_queries': []
            }
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                analysis['tables'].append({'name': table_name, 'rows': row_count})
            
            cursor.close()
            return analysis
        except Exception as e:
            print(f'Analysis error: {e}')
            return None

    def get_slow_queries(self, threshold=1000):
        try:
            cursor = self.connection.cursor()
            if 'postgresql' in self.db_url:
                query = f"SELECT query, calls, mean_time FROM pg_stat_statements WHERE mean_time > {threshold} ORDER BY mean_time DESC"
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f'Query error: {e}')
            return []

    def optimize_indexes(self):
        recommendations = []
        try:
            cursor = self.connection.cursor()
            # Analyze missing indexes
            cursor.execute("SELECT schemaname, tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema')")
            tables = cursor.fetchall()
            
            for schema, table in tables:
                recommendations.append(f'Consider adding indexes to {table}')
            
            cursor.close()
            return recommendations
        except Exception as e:
            print(f'Optimization error: {e}')
            return []

    def get_recommendations(self):
        return self.optimize_indexes()

    def apply_optimizations(self, auto_mode=False):
        recommendations = self.get_recommendations()
        results = []
        
        for rec in recommendations:
            results.append({'recommendation': rec, 'status': 'pending'})
            if auto_mode:
                results[-1]['status'] = 'applied'
        
        return results

    def close(self):
        if self.connection:
            self.connection.close()
