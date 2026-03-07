import re
import requests
from bs4 import BeautifulSoup
import openpyxl

url = input("Enter website URL: ").strip()

page = requests.get(url)
soup = BeautifulSoup(page.text, "html.parser")
text = soup.get_text()

emails = list(set(re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)))

wb = openpyxl.Workbook()
ws = wb.active
ws.append(["Email"])
for email in emails:
    ws.append([email])

wb.save("emails.xlsx")
print(f"Done! {len(emails)} email(s) saved to emails.xlsx")
