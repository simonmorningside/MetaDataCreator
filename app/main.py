from views.main_window import PhotoDataApp
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

if __name__ == "__main__":
    app = PhotoDataApp()
    app.mainloop()
