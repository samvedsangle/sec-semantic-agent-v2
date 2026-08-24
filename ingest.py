import os
from sec_edgar_downloader import Downloader

USER_AGENT_NAME = "PortfolioProject"
USER_AGENT_EMAIL = "student@university.edu"

print("Initializing SEC EDGAR Downloader...")
dl = Downloader(USER_AGENT_NAME, USER_AGENT_EMAIL)

print("Fetching latest real 10-K financial filing from the live web...")
dl.get("10-K", "AAPL", limit=1)
print("Successfully downloaded real SEC 10-K filing to ./sec-edgar-filings/")
