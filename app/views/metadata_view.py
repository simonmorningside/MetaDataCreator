import tkinter as tk
from tkinter import ttk, messagebox
from app.controllers.test_ai_controller import AIController  # ✅ use your existing controller


class MetadataView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="white")
        self.app = app

        # Title
        ttk.Label(self, text="Metadata Tools", font=("Arial", 16, "bold")).pack(pady=20)

        # Existing metadata inspection button
        ttk.Button(
            self,
            text="Inspect Metadata",
            command=self.app.metadata_controller.inspect_metadata
        ).pack(pady=5)

        # ✅ New AI caption generation button (uses test_ai_controller)
        ttk.Button(
            self,
            text="Generate Captions (AI)",
            command=self.run_ai_captioner
        ).pack(pady=5)

        # Back button
        ttk.Button(
            self,
            text="Back to Menu",
            command=lambda: app.show_frame("MainMenu")
        ).pack(pady=20)

    def run_ai_captioner(self):
        """Run AI-based caption generation using the test AI controller."""
        try:
            self.app.status_label.config(text="Generating AI captions...")
            self.app.update()

            # Safely read test_mode if your app defines it
            test_mode = self.app.test_mode.get() if hasattr(self.app, "test_mode") else False

            # ✅ Use your existing AIController
            controller = AIController(test_mode=test_mode)
            controller.caption_all_images()

            messagebox.showinfo("Success", "AI caption generation complete!")
        except FileNotFoundError as e:
            messagebox.showerror("File Not Found", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate captions:\n{e}")
        finally:
            self.app.status_label.config(text="Ready")
