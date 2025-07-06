# gui_app_email.py (FIXED NameError)
import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import time
import os
import datetime # Added for timestamping logs

# Import from config.py
from config import LOG_FILE_PATH, FAILED_EMAILS_LOG_PATH

# Import your custom modules
from data_handler import load_contacts_from_excel
from email_tool import send_email_message
from ai_agent import SmartEmailAgent

class SmartEmailMessengerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Email Messenger AI Agent")
        self.geometry("900x780") # Increased size for more log/info
        self.resizable(False, False)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.contacts = []
        self.agent = SmartEmailAgent()
        self.selected_file_path = ""

        self.create_widgets()

    def create_widgets(self):
        # --- Frame for File Upload ---
        file_frame = ctk.CTkFrame(self)
        file_frame.pack(pady=10, padx=20, fill="x")

        self.file_label = ctk.CTkLabel(file_frame, text="No Excel file selected.")
        self.file_label.pack(side="left", padx=10, pady=5)

        self.upload_button = ctk.CTkButton(file_frame, text="Upload Excel", command=self.upload_excel_file)
        self.upload_button.pack(side="right", padx=10, pady=5)

        # --- Contact Count and Validation Info ---
        contact_info_frame = ctk.CTkFrame(self)
        contact_info_frame.pack(pady=(0, 10), padx=20, fill="x")
        self.valid_contacts_label = ctk.CTkLabel(contact_info_frame, text="Valid Contacts: 0")
        self.valid_contacts_label.pack(side="left", padx=10, pady=5)
        self.issue_contacts_label = ctk.CTkLabel(contact_info_frame, text="Issues Found: 0", text_color="orange")
        self.issue_contacts_label.pack(side="left", padx=10, pady=5)
        self.show_issues_button = ctk.CTkButton(contact_info_frame, text="Show Issues", command=self.show_contact_issues, state="disabled")
        self.show_issues_button.pack(side="right", padx=10, pady=5)
        self.contact_issues = [] # To store issues from data_handler

        # --- Frame for Personalization Option ---
        personalization_frame = ctk.CTkFrame(self)
        personalization_frame.pack(pady=10, padx=20, fill="x")
        self.personalized_checkbox = ctk.CTkCheckBox(personalization_frame, text="Generate personalized email for each contact (uses more AI tokens)", onvalue=True, offvalue=False)
        self.personalized_checkbox.pack(side="left", padx=10, pady=5)
        self.personalized_checkbox.bind("<Button-1>", self._toggle_preview_button_text) # Bind to update button text

        # --- Frame for Prompt Input ---
        prompt_frame = ctk.CTkFrame(self)
        prompt_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(prompt_frame, text="Email Content Generation Prompt (AI will use this):").pack(anchor="w", pady=(0, 5))
        self.prompt_entry = ctk.CTkTextbox(prompt_frame, height=80, width=800)
        self.prompt_entry.insert("1.0", "Generate a friendly welcome email for new subscribers. Introduce our services and offer a special first-time discount code: NEWUSER10.")
        self.prompt_entry.pack(fill="x", padx=5, pady=5)

        # --- Preview Button ---
        self.preview_button = ctk.CTkButton(self, text="Generate Preview (for first contact)", command=self.generate_preview)
        self.preview_button.pack(pady=10, padx=20, fill="x")

        # --- Preview Area ---
        preview_label = ctk.CTkLabel(self, text="Email Preview (for first contact loaded):")
        preview_label.pack(pady=(5,0), padx=20, anchor="w")

        preview_messages_frame = ctk.CTkFrame(self)
        preview_messages_frame.pack(pady=5, padx=20, fill="both", expand=True)

        ctk.CTkLabel(preview_messages_frame, text="Email Subject:").pack(anchor="w", padx=5, pady=(5,0))
        self.email_subject_preview_text = ctk.CTkEntry(preview_messages_frame)
        self.email_subject_preview_text.pack(fill="x", padx=5, pady=(0,5))

        ctk.CTkLabel(preview_messages_frame, text="Email Body:").pack(anchor="w", padx=5, pady=(5,0))
        self.email_body_preview_text = scrolledtext.ScrolledText(preview_messages_frame, wrap="word", height=12, font=("Helvetica", 10))
        self.email_body_preview_text.pack(fill="x", padx=5, pady=(0,5))

        # --- Send Button ---
        self.send_button = ctk.CTkButton(self, text="Send All Emails", command=self.confirm_and_send)
        self.send_button.pack(pady=10, padx=20, fill="x")

        # --- Log Area ---
        ctk.CTkLabel(self, text="Activity Log:").pack(pady=(5,0), padx=20, anchor="w")
        self.log_text = scrolledtext.ScrolledText(self, wrap="word", height=10, font=("Consolas", 9), background="#222222", foreground="#FFFFFF")
        self.log_text.pack(pady=5, padx=20, fill="both", expand=True)
        self.log_message(f"Application started. (Current Time: {time.strftime('%Y-%m-%d %H:%M:%S')})")
        self.log_message(f"Sending log saved to: {LOG_FILE_PATH}")
        self.log_message(f"Failed emails log saved to: {FAILED_EMAILS_LOG_PATH}")


    def _toggle_preview_button_text(self, event=None):
        """Updates the preview button text based on personalization checkbox."""
        if self.personalized_checkbox.get():
            self.preview_button.configure(text="Generate Preview (for first contact only)")
        else:
            self.preview_button.configure(text="Generate Preview (for first contact)")


    def upload_excel_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.selected_file_path = file_path
            self.file_label.configure(text=f"File: {os.path.basename(self.selected_file_path)}")
            self.log_message(f"Selected file: {self.selected_file_path}")
            
            def _load():
                loaded_contacts, issues = load_contacts_from_excel(self.selected_file_path)
                self.after(0, self._update_contacts_gui, loaded_contacts, issues)
            threading.Thread(target=_load).start()

    def _update_contacts_gui(self, loaded_contacts, issues):
        self.contacts = loaded_contacts # Only valid contacts are stored here
        self.contact_issues = issues # Store the list of issues

        if not self.contacts:
            messagebox.showwarning("No Valid Contacts", "No valid contacts were loaded from the Excel file. Please check file format and email addresses.")
            self.log_message("No valid contacts loaded from Excel.")
        else:
            self.log_message(f"Loaded {len(self.contacts)} valid contacts from Excel.")
        
        self.valid_contacts_label.configure(text=f"Valid Contacts: {len(self.contacts)}")
        self.issue_contacts_label.configure(text=f"Issues Found: {len(self.contact_issues)}")
        self.show_issues_button.configure(state="normal" if self.contact_issues else "disabled")

        self.email_subject_preview_text.delete(0, "end")
        self.email_body_preview_text.delete("1.0", "end")
        if issues:
            self.log_message("WARNING: Some contacts had issues (e.g., missing/invalid/duplicate emails). They will be skipped.")
            # FIX: Use lambda for keyword argument in self.after for log_message
            for issue in issues:
                self.log_message(f"  - {issue}", is_error=True) 

    def show_contact_issues(self):
        if self.contact_issues:
            issues_text = "\n".join(self.contact_issues)
            messagebox.showinfo("Contact Loading Issues", "The following issues were found during contact loading:\n\n" + issues_text)
        else:
            messagebox.showinfo("Contact Loading Issues", "No issues were found during contact loading.")

    def log_message(self, message, is_error=False):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Log to GUI
        if is_error:
            self.log_text.insert("end", log_entry, "error") # Add a tag for coloring
        else:
            self.log_text.insert("end", log_entry)
        self.log_text.see("end")

        # Configure tag for error messages (red color)
        self.log_text.tag_configure("error", foreground="red")

        # Log to file
        try:
            with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to main log file: {e}")

    def generate_preview(self):
        if not self.contacts:
            messagebox.showwarning("No Valid Contacts", "Please upload an Excel file with valid contacts first.")
            return

        user_prompt = self.prompt_entry.get("1.0", "end").strip()
        if not user_prompt:
            messagebox.showwarning("No Prompt", "Please enter an email generation prompt.")
            return

        self.log_message("Generating email preview for the first contact. This may take a moment...")
        self.preview_button.configure(state="disabled")
        self.send_button.configure(state="disabled")

        first_contact = self.contacts[0]
        self.log_message(f"Using first contact for preview: {first_contact.get('name', 'Unnamed Contact')}")

        self.email_subject_preview_text.delete(0, "end")
        self.email_body_preview_text.delete("1.0", "end")

        def _generate():
            try:
                preview_data = self.agent.generate_email_preview(user_prompt, first_contact)
                self.after(0, self._update_preview_gui, preview_data)
            except Exception as e:
                self.after(0, lambda: self.log_message(f"Error generating preview: {e}", is_error=True)) # FIX
                self.after(0, lambda: messagebox.showerror("Preview Error", f"An error occurred during preview generation: {e}")) # FIX
            finally:
                # FIX: Use lambda for keyword argument in self.after
                self.after(0, lambda: self.preview_button.configure(state="normal"))
                self.after(0, lambda: self.send_button.configure(state="normal"))

        threading.Thread(target=_generate).start()

    def _update_preview_gui(self, preview_data):
        email_subj = preview_data.get('email_subject', '')
        email_body = preview_data.get('email_body', '')
        raw_llm_output = preview_data.get('raw_llm_output', '') # raw_llm_output is defined here

        self.email_subject_preview_text.insert(0, email_subj)
        self.email_body_preview_text.insert("1.0", email_body)

        self.log_message("Email preview generated successfully.")
        # Now it's safe to use raw_llm_output here
        if "LLM did not return valid JSON" in raw_llm_output:
            self.log_message(f"Warning: LLM output for preview was not perfectly parsed. Raw output:\n{raw_llm_output}", is_error=True)


    def confirm_and_send(self):
        if not self.contacts:
            messagebox.showwarning("No Valid Contacts", "Please upload an Excel file with valid contacts first.")
            return

        is_personalized = self.personalized_checkbox.get()
        
        # If not personalized, get content from preview fields
        email_subject_template = self.email_subject_preview_text.get().strip()
        email_body_template = self.email_body_preview_text.get("1.0", "end").strip()

        if not is_personalized and (not email_subject_template or not email_body_template):
            messagebox.showwarning("Empty Email Content", "Email subject or body is empty. Please generate or type content for the template.")
            return
        
        if is_personalized and not self.prompt_entry.get("1.0", "end").strip():
            messagebox.showwarning("No Prompt", "Please enter a message generation prompt for personalized emails.")
            return


        num_contacts = len(self.contacts)
        confirmation_message = (
            f"You are about to send emails to {num_contacts} contacts.\n"
            f"Sending Mode: {'FULLY PERSONALIZED (AI generates for each contact)' if is_personalized else 'TEMPLATE (AI generated preview, sent to all)'}\n\n"
            "Are you sure you want to proceed?"
        )

        if not messagebox.askyesno("Confirm Send", confirmation_message):
            return

        self.log_message("Email sending process initiated...")
        self.send_button.configure(state="disabled")
        self.preview_button.configure(state="disabled")
        self.upload_button.configure(state="disabled")
        self.personalized_checkbox.configure(state="disabled") # Disable during send

        def _send():
            total_success = 0
            total_failed = 0
            user_prompt = self.prompt_entry.get("1.0", "end").strip() # Get prompt once

            for i, contact in enumerate(self.contacts):
                current_contact_name = contact.get('name', 'Unnamed Contact')
                current_email = contact.get('email', '').strip()

                self.after(0, lambda: self.log_message(f"\n--- [{i+1}/{num_contacts}] Processing contact: {current_contact_name} ({current_email}) ---")) # FIX
                
                # Determine email content based on personalization setting
                final_email_subject = ""
                final_email_body = ""

                if is_personalized:
                    # Generate personalized content for EACH contact
                    self.after(0, lambda: self.log_message(f"  Generating personalized email for {current_contact_name}...")) # FIX
                    ai_gen_result = self.agent.generate_email_preview(user_prompt, contact)
                    final_email_subject = ai_gen_result.get("email_subject", "")
                    final_email_body = ai_gen_result.get("email_body", "")
                    if ai_gen_result.get('raw_llm_output') and "LLM did not return valid JSON" in ai_gen_result['raw_llm_output']:
                         self.after(0, lambda: self.log_message(f"    AI generation issue for {current_contact_name}: {ai_gen_result['raw_llm_output']}", is_error=True)) # FIX
                         # Fallback to template content if AI generation fails during personalized send
                         if not final_email_subject: # Only fallback if AI didn't provide anything usable
                             final_email_subject = "(AI Generation Failed) " + email_subject_template
                         if not final_email_body:
                             final_email_body = "(AI Generation Failed) " + email_body_template
                else:
                    # Use the single preview content for all
                    final_email_subject = email_subject_template
                    final_email_body = email_body_template

                # Send the email
                if current_email:
                    self.after(0, lambda: self.log_message(f"  Attempting Email for {current_contact_name}...")) # FIX
                    email_result = send_email_message(current_email, final_email_subject, final_email_body)
                    self.after(0, lambda: self.log_message(f"    - Email: {email_result['status']} - {email_result['message']}", 
                                                            is_error=(email_result['status'] == 'error'))) # FIX
                    
                    if email_result['status'] == 'success':
                        total_success += 1
                    else:
                        total_failed += 1
                        # The send_email_message function already handles logging to file internally
                else:
                    total_failed += 1
                    self.after(0, lambda: self.log_message(f"    - Skipped: No email address for {current_contact_name}.", is_error=True)) # FIX

                time.sleep(0.1) # Small delay to prevent API rate limits (Gmail) and allow GUI updates

            self.after(0, lambda: self.log_message(f"\n--- Sending Complete ---")) # FIX
            self.after(0, lambda: self.log_message(f"Total contacts processed: {num_contacts}")) # FIX
            self.after(0, lambda: self.log_message(f"Successful emails sent: {total_success}")) # FIX
            self.after(0, lambda: self.log_message(f"Failed or Skipped emails: {total_failed}")) # FIX
            
            # Re-enable buttons and checkbox
            self.after(0, lambda: self.send_button.configure(state="normal")) # FIX
            self.after(0, lambda: self.preview_button.configure(state="normal")) # FIX
            self.after(0, lambda: self.upload_button.configure(state="normal")) # FIX
            self.after(0, lambda: self.personalized_checkbox.configure(state="normal")) # FIX
            
            self.after(0, lambda: messagebox.showinfo("Sending Complete", 
                       f"Finished sending emails.\nSuccessful: {total_success}\nFailed/Skipped: {total_failed}\n\nCheck the Activity Log and 'failed_emails_log.txt' for details.")) # FIX

        threading.Thread(target=_send).start()

if __name__ == "__main__":
    # Ensure a dummy Excel file exists for testing the GUI immediately
    import pandas as pd
    if not os.path.exists('dummy_contacts_email.xlsx'):
        data = {
            'Name': ['Alice Smith', 'Bob Johnson', 'Charlie Brown', 'Eve Davis', 'Duplicate Alice', 'No Email'],
            'Email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'invalid-email', 'alice@example.com', ''] # Added invalid and duplicate
        }
        dummy_df = pd.DataFrame(data)
        dummy_df.to_excel('dummy_contacts_email.xlsx', index=False)
        print("Created 'dummy_contacts_email.xlsx' for initial GUI test.")

    # Clear previous log files on app start for a fresh run
    if os.path.exists(LOG_FILE_PATH):
        os.remove(LOG_FILE_PATH)
    if os.path.exists(FAILED_EMAILS_LOG_PATH):
        os.remove(FAILED_EMAILS_LOG_PATH)

    app = SmartEmailMessengerApp()
    app.mainloop()