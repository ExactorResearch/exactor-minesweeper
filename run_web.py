"""
Launch Exactor Minesweeper AI Arena Web Application.
"""

import sys
import os
import uvicorn

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "exactor-jev")))

from exactor_minesweeper.web.server import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"\n========================================================")
    print(f"🚀 Starting Exactor Minesweeper Web Arena...")
    print(f"🌐 Access Web Dashboard: http://localhost:{port}")
    print(f"========================================================\n")
    uvicorn.run("exactor_minesweeper.web.server:app", host="0.0.0.0", port=port, reload=True)
