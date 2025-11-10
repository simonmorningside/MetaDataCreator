from tkinter import messagebox
from scripts.metadata import run_load_and_inspect

class MetadataController:
    def __init__(self, app):
        self.app = app  # This should be the PhotoDataApp instance

    def inspect_metadata(self):
        """Run the metadata inspection and update the UI accordingly."""
        try:
            # Safely update status label if it exists
            if hasattr(self.app, "status_label"):
                self.app.status_label.config(text="Running metadata inspection...")
                self.app.update_idletasks()

            # Run the inspection script
            csvs, _ = run_load_and_inspect(
                test_mode=self.app.test_mode.get(),
                gui_mode=True
            )

            # Update the dropdown in the app
            self.app.update_csv_dropdown(csvs)

            # Notify the user of success
            messagebox.showinfo("Success", "Metadata inspection complete!")

        except Exception as e:
            # Handle unexpected errors gracefully
            messagebox.showerror("Error", f"Failed to inspect metadata:\n{e}")

        finally:
            # Always restore the status text
            if hasattr(self.app, "status_label"):
                self.app.status_label.config(text="Ready")
            else:
                print("⚠ No status_label found on app.")
