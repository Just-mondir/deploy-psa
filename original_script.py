import asyncio
import re
from playwright.async_api import Page

async def click_grader_grade(page: Page, grader: str, grade: str, stop_event) -> bool:
    """Click the '<grader> population' button matching `grade` exactly."""
    if stop_event.is_set(): return False
    try:
        print(f"🎯 Selecting: {grader} {grade}")
        popup = page.locator("div[data-testid='card-pops']").first
        await popup.scroll_into_view_if_needed()
        await page.wait_for_timeout(900)

        header = page.get_by_text(f"{grader} population", exact=True)
        if not await header.count():
            print(f"❌ Header '{grader} population' not found")
            return False

        wrapper = header.locator("xpath=..")
        buttons = wrapper.locator("button")

        button_count = await buttons.count()
        for i in range(button_count):
            if stop_event.is_set(): return False
            btn = buttons.nth(i)
            grade_span = btn.locator("span").first
            text = await grade_span.text_content()
            text = text.strip() if text else ""

            if text == grade:
                await btn.scroll_into_view_if_needed()
                await btn.click(timeout=2000)
                print(f"✅ Clicked: {grader} {grade}")
                await page.wait_for_timeout(500)
                return True

        print(f"❌ Exact grade '{grade}' not found under '{grader}'.")
    except Exception as e:
        print(f"❌ Error selecting {grader} {grade}: {e}")

    return False


async def fetch_prices(page: Page, stop_event, num_sales=4):
    if stop_event.is_set(): return []
    print("💵 Waiting for recent sales to load...")
    await page.wait_for_timeout(3000)

    prices = []
    blocks = page.locator("div.MuiTypography-body1.css-vxna0y")

    block_count = await blocks.count()
    for i in range(block_count):
        if stop_event.is_set(): break
        try:
            price_span = blocks.nth(i).locator("span[class*='css-16tlq5a']")
            price_text = await price_span.inner_text()
            match = re.search(r"\$([0-9\s,\.]+)", price_text)
            if match:
                price_str = match.group(1).replace(" ", "").replace("\u202f", "").replace(",", "")
                price = float(price_str)
                prices.append(price)
            if len(prices) >= num_sales:
                break
        except Exception as e:
            print(f"⚠️ Skipping sale {i+1}: {e}")
    return prices


async def try_click_card_button(page: Page, stop_event) -> bool:
    """Try to click the card button (first match). Return True if clicked."""
    if stop_event.is_set(): return False
    try:
        button = page.locator("button.MuiButtonBase-root.css-1ege7gw").first
        await button.wait_for(state="visible", timeout=5000)
        await button.click()
        print("✅ Clicked card button")
        await page.wait_for_timeout(1500)
        return True
    except Exception as e:
        print(f"⚠️ Could not click card button: {e}")
        return False


async def perform_login_if_needed(page: Page, email: str, password: str, stop_event) -> bool:
    """If login flow is detected, perform login. Return True if login performed (or already logged in)."""
    if stop_event.is_set(): return False
    try:
        login_btn = page.locator("button:has-text('Log in')").first
        if await login_btn.count():
            print("🔐 Login button detected — clicking it")
            await login_btn.click()
            await page.wait_for_timeout(1000)

            email_input = page.locator("input[type='email'], input[name='email']").first
            await email_input.fill(email)
            await page.wait_for_timeout(300)
            print("✅ Filled email")

            password_input = page.locator("input[type='password'], input[name='password']").first
            await password_input.fill(password)
            await page.wait_for_timeout(300)
            print("✅ Filled password")

            submit_btn = page.locator("button:has-text('Log in'), button[type='submit']").last
            await submit_btn.click()
            print("➡️ Clicked submit button")
            
            await page.wait_for_load_state("networkidle", timeout=10000)
            await page.wait_for_timeout(2000)
            print("🔓 Login attempt completed")
            return True
        else:
            return True
    except Exception as e:
        print(f"⚠️ Error during login flow: {e}")
        return False

async def process_rows(page: Page, sheet, all_values, start_row, stop_event, email, password):
    num_rows = len(all_values)
    print(f"🚀 Processing rows {start_row}..{num_rows}")

    for row_idx in range(start_row - 1, num_rows):
        if stop_event.is_set():
            print("🛑 Stop event received, halting processing.")
            break
        
        rnum = row_idx + 1
        try:
            row_vals = all_values[row_idx]
            url = row_vals[5] if len(row_vals) > 5 else ""
            grader = row_vals[2] if len(row_vals) > 2 else ""
            fake_grade = row_vals[3] if len(row_vals) > 3 else ""

            if not url or not grader or not fake_grade:
                print(f"⚠️ Skipping row {rnum}: Missing required data")
                continue

            grade = fake_grade[:2] if len(fake_grade) > 3 else fake_grade
            print(f"\n🔁 Processing row {rnum}: {grader} {grade}")

            try:
                await page.goto(url, timeout=30000)
            except Exception as e:
                print(f"⚠️ Navigation error for row {rnum}: {e}")
                continue
            await page.wait_for_timeout(2000)

            if not await try_click_card_button(page, stop_event):
                continue

            if not await perform_login_if_needed(page, email, password, stop_event):
                continue

            success = await click_grader_grade(page, grader, grade, stop_event)
            await page.wait_for_timeout(1000)

            if success:
                prices = await fetch_prices(page, stop_event, 4)
                if prices:
                    avg = sum(prices) / len(prices)
                    for i, price in enumerate(prices[:4]):
                        sheet.update_cell(rnum, 12 + i, price)
                    sheet.update_cell(rnum, 16, avg)
                    print(f"✅ Updated row {rnum} with prices and average.")
                else:
                    print(f"❌ No prices found for row {rnum}.")
            else:
                print(f"❌ Could not select grader/grade for row {rnum}.")

            await page.wait_for_timeout(1200)

        except Exception as e:
            print(f"❌ Error processing row {rnum}: {e}")
            continue