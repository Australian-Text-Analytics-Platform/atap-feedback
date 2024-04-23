import requests
import panel
from panel import Column, Row
from panel.theme import Fast
from panel.viewable import Viewer, Viewable
from panel.widgets import TextAreaInput, Button, TooltipIcon

panel.extension(notifications=True, design=Fast)


class FeedbackPane(Viewer):
    OWNER: str = "Australian-Text-Analytics-Platform"
    ISSUE_TITLE: str = "User-generated feedback"
    ALT_EMAIL: str = "ldaca@uq.edu.au"

    def __init__(self, repo: str, access_token: str, **params):
        super().__init__(**params)
        self.repo: str = repo
        self.access_token: str = access_token

        tooltip = TooltipIcon(value=f"Feedback will be submitted to the ATAP development team. Alternatively, send an email here: {self.ALT_EMAIL}\nFeel free to include your contact details.\nThank you for your feedback!")

        self.issue_body_input = TextAreaInput(name="Enter feedback here", placeholder="Describe what went wrong or what went right")
        self.submit_feedback_button = Button(name="Submit", button_style="solid", button_type="primary")
        self.submit_feedback_button.on_click(self._submit_issue)

        self.panel = Column(self.issue_body_input,
                            Row(self.submit_feedback_button, tooltip),
                            styles={'border': '1px solid #ceecfe', 'border-radius': '5px'}
                            )

    def __panel__(self) -> Viewable:
        return self.panel

    def _submit_issue(self, *_):
        issue_body: str = self.issue_body_input.value
        if len(issue_body) == 0:
            panel.state.notifications.error("Feedback body cannot be empty", duration=0)
            return

        url = f"https://api.github.com/repos/{self.OWNER}/{self.repo}/issues"
        headers = {'Accept': 'application/vnd.github+json',
                   'Authorization': f'Bearer {self.access_token}'}
        data = {"title": self.ISSUE_TITLE,
                "body": issue_body}
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 201:
            self.issue_body_input.value = ''
            panel.state.notifications.success("Feedback submitted successfully")
        else:
            error_message = f"{response.status_code} - {response.json().get('message')}"
            panel.state.notifications.error(f"Error submitting feedback: {error_message}\nSubmit feedback via email here: {self.ALT_EMAIL}",
                                            duration=0)
