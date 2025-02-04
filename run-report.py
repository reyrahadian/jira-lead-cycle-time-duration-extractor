import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reporting_app.app import app

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False, port=8081)