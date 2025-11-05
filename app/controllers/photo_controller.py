from tkinter import messagebox
from app.scripts.photo_renamer import run_photo_renamer


class PhotoController:
    def __init__(self, app):
        self.app = app

    def rename_photos(self):
        try:
            self.app.status_label.config(text="Running photo renamer...")
            self.app.update()
            run_photo_renamer(test_mode=self.app.test_mode.get(), gui_mode=True)
            messagebox.showinfo("Success", "Photo renaming complete!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename photos: {e}")
        finally:
            self.app.status_label.config(text="Ready")
