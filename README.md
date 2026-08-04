services:
  - type: web
    name: quan-ly-ao-nuoi
    env: python
    region: singapore
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port 10000 --server.address 0.0.0.0
