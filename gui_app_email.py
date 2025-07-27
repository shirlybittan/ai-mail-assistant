# gui_app_email.py

import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import time
import os
import datetime

# Import from config.py
from config import SENDER_EMAIL, SENDER_PASSWORD, OPENAI_API_KEY, FAILED_EMAILS_LOG_PATH

# Import your custom modules
from data_handler import load_contacts_from_excel
from email_tool import send_email_message
from email_agent import SmartEmailAgent # NEW: Use the unified email_agent

class SmartEmailMessengerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Email Messenger AI Agent")
        self.geometry("900x780")
        self.resizable(False, False)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.contacts = []
        self.contact_issues = []
        self.agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY) # NEW: Use the unified agent
        self.selected_file_path = ""
        self.email_preview = None

        self.create_widgets()

    def create_widgets(self):
        # --- Frame for File Upload ---
        file_frame = ctk.CTkFrame(self)
        file_frame.pack(pady=10, padx=20, fill="x")

        self.file_label = ctk.CTkLabel(file_frame, text="No Excel file selected.")
        self.file_label.pack(side="left", padx=10, pady=5)

        self.upload_button = ctk.CTkButton(file_frame, text="Upload Excel File", command=self.upload_file)
        self.upload_button.pack(side="right", padx=10, pady=5)
        
        # --- Frame for AI Instructions and Options ---
        options_frame = ctk.CTkFrame(self)
        options_frame.pack(pady=5, padx=20, fill="x")
        
        self.instruction_label = ctk.CTkLabel(options_frame, text="AI Instruction for Email:", fg_color="transparent")
        self.instruction_label.pack(anchor="w", padx=10, pady=(5, 0))
        self.instruction_textbox = ctk.CTkTextbox(options_frame, height=100)
        self.instruction_textbox.pack(padx=10, pady=5, fill="x")
        
        self.personalized_checkbox = ctk.CTkCheckBox(options_frame, text="Personalize Emails for Each Contact")
        self.personalized_checkbox.pack(anchor="w", padx=10, pady=5)
        self.personalized_checkbox.select() # Start with personalization on by default
        
        self.preview_button = ctk.CTkButton(options_frame, text="Generate Email Preview", command=self.generate_preview)
        self.preview_button.pack(padx=10, pady=5, fill="x")
        
        # --- Frame for Preview and Sending ---
        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(pady=5, padx=20, fill="both", expand=True)

        self.preview_label = ctk.CTkLabel(preview_frame, text="Email Preview:", fg_color="transparent")
        self.preview_label.pack(anchor="w", padx=10, pady=(5, 0))

        preview_text_frame = ctk.CTkFrame(preview_frame)
        preview_text_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.preview_subject_entry = ctk.CTkEntry(preview_text_frame, placeholder_text="Subject")
        self.preview_subject_entry.pack(fill="x", pady=2)
        self.preview_text = ctk.CTkTextbox(preview_text_frame, height=250)
        self.preview_text.pack(fill="both", expand=True, pady=5)
        
        # --- Log Frame ---
        log_frame = ctk.CTkFrame(self)
        log_frame.pack(pady=5, padx=20, fill="both", expand=True)

        log_label = ctk.CTkLabel(log_frame, text="Activity Log:", fg_color="transparent")
        log_label.pack(anchor="w", padx=10, pady=(5, 0))
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=ctk.WORD, height=10, bg="#2b2b2b", fg="white", insertbackground="white")
        self.log_text.pack(padx=10, pady=5, fill="both", expand=True)
        self.log_text.configure(state="disabled")

        # --- Frame for Send Button ---
        send_frame = ctk.CTkFrame(self)
        send_frame.pack(pady=10, padx=20, fill="x")

        self.send_button = ctk.CTkButton(send_frame, text="Send All Emails", command=self.send_emails)
        self.send_button.pack(padx=10, pady=5, fill="x")
        self.send_button.configure(state="disabled") # Disabled until a preview is generated

    def log(self, message):
        """Appends a timestamped message to the activity log."""
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        self.log_text.configure(state="normal")
        self.log_text.insert(ctk.END, f"{timestamp} {message}\n")
        self.log_text.see(ctk.END) # Scroll to the bottom
        self.log_text.configure(state="disabled")
        
    def upload_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.selected_file_path = file_path
            self.file_label.configure(text=f"File selected: {os.path.basename(file_path)}")
            self.log(f"Loading contacts from: {self.selected_file_path}")
            
            # Clear previous data
            self.contacts = []
            self.contact_issues = []
            self.email_preview = None
            self.preview_subject_entry.delete(0, ctk.END)
            self.preview_text.delete("1.0", ctk.END)
            self.send_button.configure(state="disabled")
            
            # Run loading in a separate thread
            threading.Thread(target=self._load_contacts).start()

    def _load_contacts(self):
        contacts, issues = load_contacts_from_excel(self.selected_file_path)
        self.contacts = contacts
        self.contact_issues = issues
        
        self.after(0, self.update_after_load)

    def update_after_load(self):
        if self.contacts:
            self.log(f"Successfully loaded {len(self.contacts)} valid contacts.")
            self.log("You can now generate a preview.")
            self.preview_button.configure(state="normal")
        else:
            self.log("No valid contacts found in the Excel file.")
            self.preview_button.configure(state="disabled")
        
        for issue in self.contact_issues:
            self.log(f"WARNING: {issue}")

    def generate_preview(self):
        instruction = self.instruction_textbox.get("1.0", ctk.END).strip()
        if not instruction:
            messagebox.showwarning("Input Error", "Please provide an AI instruction for the email.")
            return

        self.log("Generating email preview...")
        self.preview_button.configure(state="disabled")
        self.send_button.configure(state="disabled")
        self.upload_button.configure(state="disabled")
        self.personalized_checkbox.configure(state="disabled")
        
        # Get the first contact for the preview
        if not self.contacts:
            messagebox.showwarning("No Contacts", "Please upload a file and load contacts first.")
            return

        first_contact = self.contacts[0]
        is_personalized = self.personalized_checkbox.get() == 1
        
        # Run AI generation in a separate thread
        threading.Thread(target=self._generate_preview_thread, args=(instruction, first_contact, is_personalized)).start()
        
    def _generate_preview_thread(self, instruction, first_contact, is_personalized):
        if is_personalized:
            self.log(f"Using first contact ({first_contact.get('name', 'N/A')}) for preview generation.")
            
            # NEW: Call the unified generate_email method with contact info
            preview = self.agent.generate_email(prompt=instruction, contact_info=first_contact, output_language="en")
        else:
            self.log("Generating a general email template preview.")
            
            # NEW: Call the unified generate_email method without contact info
            preview = self.agent.generate_email(prompt=instruction, contact_info=None, output_language="en")
            
        self.after(0, lambda: self.update_preview(preview))

    def update_preview(self, preview):
        self.email_preview = preview
        
        if self.email_preview and self.email_preview.get("subject") != "Error":
            self.preview_subject_entry.delete(0, ctk.END)
            self.preview_subject_entry.insert(0, self.email_preview.get("subject"))
            self.preview_text.delete("1.0", ctk.END)
            self.preview_text.insert("1.0", self.email_preview.get("body"))
            self.log("Email preview generated successfully. You can now edit and send.")
            self.send_button.configure(state="normal")
        else:
            self.log(f"ERROR: Failed to generate email preview. Details: {self.email_preview.get('body', 'Unknown error.')}")
            self.preview_subject_entry.delete(0, ctk.END)
            self.preview_text.delete("1.0", ctk.END)
            self.send_button.configure(state="disabled")

        self.preview_button.configure(state="normal")
        self.upload_button.configure(state="normal")
        self.personalized_checkbox.configure(state="normal")

    def send_emails(self):
        if not self.email_preview:
            messagebox.showwarning("No Preview", "Please generate an email preview first.")
            return

        response = messagebox.askyesno("Confirm Send", 
                                       f"You are about to send emails to {len(self.contacts)} contacts. Are you sure?")
        if not response:
            return
        
        self.log("Email sending process initiated...")
        self.send_button.configure(state="disabled")
        self.preview_button.configure(state="disabled")
        self.upload_button.configure(state="disabled")
        self.personalized_checkbox.configure(state="disabled")

        threading.Thread(target=self._send_emails_thread).start()

    def _send_emails_thread(self):
        subject_template = self.preview_subject_entry.get()
        body_template = self.preview_text.get("1.0", ctk.END)
        total_emails = len(self.contacts)
        total_success = 0
        total_failed = 0
        
        is_personalized = self.personalized_checkbox.get() == 1

        for i, contact in enumerate(self.contacts):
            recipient_name = contact.get('name', 'N/A')
            recipient_email = contact.get('email', 'N/A')

            self.after(0, lambda msg=f"--- [{i+1}/{total_emails}] Processing contact: {recipient_name} ({recipient_email}) ---": self.log(msg))
            
            try:
                # Apply personalization
                final_subject = subject_template
                final_body = body_template
                
                if is_personalized:
                    final_subject = final_subject.replace("{{Name}}", recipient_name)
                    final_body = final_body.replace("{{Name}}", recipient_name)
                
                self.after(0, lambda: self.log(f"  Attempting Email for {recipient_name}..."))
                result = send_email_message(
                    sender_email=SENDER_EMAIL,
                    sender_password=SENDER_PASSWORD,
                    to_email=recipient_email,
                    subject=final_subject,
                    body=final_body,
                    attachments=[],
                    log_path=FAILED_EMAILS_LOG_PATH
                )

                if result['status'] == 'success':
                    total_success += 1
                    self.after(0, lambda: self.log(f"    - Email: success - Email sent to {recipient_email} successfully."))
                else:
                    total_failed += 1
                    self.after(0, lambda: self.log(f"    - Email: error - Failed to send to {recipient_email}. Details: {result['message']}"))
            except Exception as e:
                total_failed += 1
                self.after(0, lambda: self.log(f"    - Email: error - An unexpected error occurred for {recipient_email}: {e}"))
                
        self.after(0, lambda: self.log("--- Email sending process complete ---"))
        self.after(0, lambda: self.log(f"Summary: {total_success} successful, {total_failed} failed/skipped."))
        
        self.after(0, lambda: self.send_button.configure(state="normal"))
        self.after(0, lambda: self.preview_button.configure(state="normal"))
        self.after(0, lambda: self.upload_button.configure(state="normal"))
        self.after(0, lambda: self.personalized_checkbox.configure(state="normal"))
        
        self.after(0, lambda: messagebox.showinfo("Sending Complete", 
                                                  f"Finished sending emails.\nSuccessful: {total_success}\nFailed/Skipped: {total_failed}\n\nCheck the Activity Log and 'failed_emails_log.txt' for details."))

if __name__ == "__main__":
    app = SmartEmailMessengerApp()
    app.mainloop()