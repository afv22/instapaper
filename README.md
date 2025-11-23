# Instapaper Newsletter Archiver

Automatically archives Instapaper bookmarks tagged "newsletter" that are older than 7 days.

## Setup

1. **Get Instapaper API credentials:**
   - Visit https://www.instapaper.com/main/request_oauth_consumer_token
   - Request OAuth consumer credentials
   - You'll receive a consumer key and consumer secret

2. **Install dependencies:**
   ```bash
   pip install requests-oauthlib
   ```

3. **Create configuration file:**
   ```bash
   cp instapaper_config.example.json instapaper_config.json
   ```

4. **Edit `instapaper_config.json`** with your credentials:
   ```json
   {
     "consumer_key": "YOUR_CONSUMER_KEY",
     "consumer_secret": "YOUR_CONSUMER_SECRET",
     "username": "your_email@example.com",
     "password": "your_password"
   }
   ```

   **Note:** Some Instapaper accounts don't require a password. If yours doesn't, you can leave the password field empty or use any value.

## Usage

Run manually:
```bash
python3 archive_newsletters.py
```

Or make it executable:
```bash
chmod +x archive_newsletters.py
./archive_newsletters.py
```

## Setting up a Cron Job

To run automatically (e.g., daily at 2 AM):

1. Open crontab:
   ```bash
   crontab -e
   ```

2. Add this line:
   ```
   0 2 * * * cd /Users/edge/Documents/software-and-security-engineering/instapaper && /usr/bin/python3 archive_newsletters.py >> /tmp/instapaper_archive.log 2>&1
   ```

   This will:
   - Run daily at 2:00 AM
   - Change to the script directory
   - Execute the script
   - Log output to `/tmp/instapaper_archive.log`

3. Save and exit

To view cron logs:
```bash
cat /tmp/instapaper_archive.log
```

## What It Does

1. Authenticates with Instapaper using OAuth
2. Fetches all bookmarks tagged "newsletter"
3. Filters bookmarks created more than 7 days ago
4. Archives matching bookmarks
5. Prints summary of actions taken

## Security Notes

- Keep `instapaper_config.json` secure (it contains your credentials)
- The example file is provided for reference only
- Consider using environment variables in production if needed
