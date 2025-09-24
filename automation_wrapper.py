import asyncio
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.async_api import async_playwright
from original_script import process_rows

async def run_automation_async(creds_path, sheet_name, stop_event, status_callback):
    """
    The main async function that sets up the browser and runs the automation.
    """
    try:
        with open(creds_path, 'r') as f:
            creds_data = json.load(f)
        
        email = creds_data.get("email")
        password = creds_data.get("password")

        if not email or not password:
            raise ValueError("Credentials file must contain 'email' and 'password' keys.")

        # Setup Google Sheets
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open(sheet_name).sheet1
        all_values = sheet.get_all_values()
        print(f"Read {len(all_values)} rows from sheet '{sheet_name}'")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--window-size=1920,1080",
                ],
            )
            context = await browser.new_context()
            page = await context.new_page()

            status_callback("Running")
            await process_rows(page, sheet, all_values, 1, stop_event, email, password)

            await browser.close()
            print("🎉 Automation finished.")

    except Exception as e:
        print(f"❌ An error occurred in the automation wrapper: {e}")
        status_callback("Error", str(e))
    finally:
        if not stop_event.is_set():
            status_callback("Stopped")

def run_automation(creds_path, sheet_name, stop_event, status_callback):
    """
    Wrapper to run the async automation function in a new event loop.
    """
    asyncio.run(run_automation_async(creds_path, sheet_name, stop_event, status_callback))
