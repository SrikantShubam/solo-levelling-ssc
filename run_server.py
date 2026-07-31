import sys, os
sys.path.insert(0, r'C:\experiments\ssc\src')
os.chdir(r'C:\experiments\ssc')
from ssc_study.db import Database
from ssc_study.web import create_app
import uvicorn
db = Database(r'C:\experiments\ssc\data\study.db')
app = create_app(db)
uvicorn.run(app, host='127.0.0.1', port=8765, log_level='info')
