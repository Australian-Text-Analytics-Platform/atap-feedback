import os

import requests
import panel
from panel import Row
from panel.theme import Fast
from panel.viewable import Viewer, Viewable
from panel.widgets import TextAreaInput, Button, TooltipIcon, TextInput

panel.extension(notifications=True, design=Fast)


class FeedbackPane(Viewer):
    OWNER: str = "Australian-Text-Analytics-Platform"
    REPO: str = "atap-feedback-submissions"
    ALT_EMAIL: str = "ldaca@uq.edu.au"

    def __init__(self, project_name: str, project_info: dict[str, str] = None, **params):
        super().__init__(**params)
        self.project_name: str = project_name
        self.project_info: str = ""
        if project_info is not None:
            for entry in project_info:
                self.project_info += f"{entry}: {project_info.get(entry)}\n"
        self.access_token: str = os.environ.get("GITHUB_TOKEN")
        if self.access_token is None:
            raise Exception("GITHUB_TOKEN environment variable not found. Ensure it is present in order to use the FeedbackPane")

        tooltip = TooltipIcon(value=f"Feedback will be submitted to the ATAP development team. Alternatively, send an email here: {self.ALT_EMAIL}\nFeel free to include your contact details.\nThank you for your feedback!")

        self.issue_body_input = TextAreaInput(name="Enter feedback here", placeholder="Describe what went wrong or what went right\nPaste any error messages here")
        self.contact_email = TextInput(name="Contact email (Optional)", placeholder="email@example.org")
        self.submit_feedback_button = Button(name="Submit", button_style="solid", button_type="primary", align="center")
        self.submit_feedback_button.on_click(self._submit_issue)

        self.panel = Row(self.issue_body_input, self.contact_email, self.submit_feedback_button, tooltip,
                         styles={'border': '1px solid #ceecfe', 'border-radius': '5px'})

    def __panel__(self) -> Viewable:
        return self.panel

    def _submit_issue(self, *_):
        feedback: str = self.issue_body_input.value
        if len(feedback) == 0:
            panel.state.notifications.error("Feedback body cannot be empty", duration=0)
            return
        issue_body: str = f"{self.project_info}\n{feedback}\n"
        if len(self.contact_email.value):
            issue_body += f"Contact email: {self.contact_email.value}"

        url = f"https://api.github.com/repos/{self.OWNER}/{self.REPO}/issues"
        headers = {'Accept': 'application/vnd.github+json',
                   'Authorization': f'Bearer {self.access_token}'}
        data = {"title": f"Feedback: {self.project_name}",
                "body": issue_body}
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 201:
            self.issue_body_input.value = ''
            panel.state.notifications.success("Feedback submitted successfully")
        else:
            error_message = f"{response.status_code} - {response.json().get('message')}"
            panel.state.notifications.error(f"Error submitting feedback: {error_message}\nSubmit feedback via email here: {self.ALT_EMAIL}",
                                            duration=0)
