import os
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class SheetsHandler:
    def __init__(self):
        self.spreadsheet_id = os.environ.get("GOOGLE_SHEET_ID")
        self.sheet_name = os.environ.get("GOOGLE_SHEET_NAME", "Survey Responses")
    
    def get_access_token(self):
        hostname = os.environ.get("REPLIT_CONNECTORS_HOSTNAME")
        repl_identity = os.environ.get("REPL_IDENTITY")
        web_repl_renewal = os.environ.get("WEB_REPL_RENEWAL")
        
        if repl_identity:
            x_replit_token = f"repl {repl_identity}"
        elif web_repl_renewal:
            x_replit_token = f"depl {web_repl_renewal}"
        else:
            logger.error("No Replit token found")
            return None
        
        url = f"https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-sheet"
        
        try:
            response = requests.get(
                url,
                headers={
                    "Accept": "application/json",
                    "X_REPLIT_TOKEN": x_replit_token
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            connection = data.get("items", [{}])[0]
            settings = connection.get("settings", {})
            
            access_token = settings.get("access_token") or \
                          settings.get("oauth", {}).get("credentials", {}).get("access_token")
            
            if not access_token:
                logger.error("No access token found in connection settings")
                return None
            
            return access_token
            
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            return None
    
    def ensure_headers_exist(self, access_token):
        if not self.spreadsheet_id:
            logger.warning("GOOGLE_SHEET_ID not set, skipping header check")
            return False
        
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/{self.sheet_name}!A1:L1"
        
        try:
            response = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("values"):
                    return True
            
            headers = [
                "Timestamp",
                "User ID",
                "Chat ID",
                "Name",
                "Email",
                "Phone",
                "Company",
                "Source",
                "Satisfaction Rating",
                "Likes",
                "Improvements",
                "Would Recommend",
                "Additional Comments"
            ]
            
            update_url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/{self.sheet_name}!A1:M1?valueInputOption=RAW"
            
            response = requests.put(
                update_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json={"values": [headers]},
                timeout=10
            )
            response.raise_for_status()
            logger.info("Headers created in spreadsheet")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure headers: {e}")
            return False
    
    def save_survey_response(self, survey_data):
        if not self.spreadsheet_id:
            logger.warning("GOOGLE_SHEET_ID not set, skipping save to Google Sheets")
            logger.info(f"Survey data (not saved): {survey_data}")
            return False
        
        access_token = self.get_access_token()
        if not access_token:
            logger.error("Could not get access token")
            return False
        
        self.ensure_headers_exist(access_token)
        
        responses = survey_data.get("responses", {})
        row_data = [
            datetime.now().isoformat(),
            str(survey_data.get("user_id", "")),
            str(survey_data.get("chat_id", "")),
            responses.get("name", ""),
            responses.get("email", ""),
            responses.get("phone", ""),
            responses.get("company", ""),
            responses.get("source", ""),
            responses.get("satisfaction_rating", ""),
            responses.get("likes", ""),
            responses.get("improvements", ""),
            responses.get("would_recommend", ""),
            responses.get("additional_comments", "")
        ]
        
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/{self.sheet_name}!A:M:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS"
        
        try:
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json={"values": [row_data]},
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Survey response saved to Google Sheets")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save survey response: {e}")
            return False
