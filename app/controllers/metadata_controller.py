from tkinter import messagebox
from app.scripts.metadata import run_load_and_inspect


class MetadataController:
    def __init__(self, app):
        self.app = app

    def inspect_metadata(self):
        try:
            self.app.status_label.config(text="Running metadata inspection...")
            self.app.update()

            csvs, _ = run_load_and_inspect(
                test_mode=self.app.test_mode.get(),
                gui_mode=True
            )

            self.app.update_csv_dropdown(csvs)
            messagebox.showinfo("Success", "Metadata inspection complete!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to inspect metadata: {e}")
        finally:
            self.app.status_label.config(text="Ready")
