@echo off
echo Starting all services...

REM Start main dashboard
start /B streamlit run app.py --server.port 8501

REM Start database instances
start /B streamlit run database_instance1.py --server.port 8502 --server.headless true
start /B streamlit run database_instance2.py --server.port 8503 --server.headless true
start /B streamlit run database_instance3.py --server.port 8504 --server.headless true

REM Start web instances
start /B streamlit run web_instance1.py --server.port 8511 --server.headless true
start /B streamlit run web_instance2.py --server.port 8512 --server.headless true
start /B streamlit run web_instance3.py --server.port 8513 --server.headless true


REM Start file instances
start /B streamlit run file_instance1.py --server.port 8701 --server.headless true
start /B streamlit run file_instance2.py --server.port 8702 --server.headless true
start /B streamlit run file_instance3.py --server.port 8703 --server.headless true
start /B streamlit run file_load_balancer.py --server.port 8704 --server.headless true

echo All services started!
echo Access the main dashboard at http://localhost:8501

REM Keep the window open
pause 