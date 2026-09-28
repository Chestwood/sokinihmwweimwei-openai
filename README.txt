SOKINIHMWWWEIMWEI - SIMPLE CHROMEOS SETUP

WHAT THIS VERSION DOES
- Uses OpenAI only for AI generation.
- No Gemini API.
- No Node.js or npm.
- Your OpenAI API key is stored locally in this Linux app folder, not in the web page.
- After setup, launch it from the Chromebook Launcher like an app.

ONE-TIME SETUP
1. Turn on Linux on your Chromebook:
   Settings > About ChromeOS > Developers > Linux development environment > Set up
2. Extract this ZIP.
3. Move the extracted "sokinihmwweimwei_chromeos" folder into "Linux files" in the Chromebook Files app.
4. Open the Terminal app.
5. Run these two commands:

   cd ~/sokinihmwweimwei_chromeos
   bash setup.sh

6. When asked, paste your OpenAI API key and press Enter.

AFTER THAT
Open the Chromebook Launcher and search for:
   Sokinihmwweimwei

Click it. Your lesson generator will open in Chrome.

TO STOP THE LOCAL SERVER (optional)
Open Terminal and run:
   cd ~/sokinihmwweimwei_chromeos
   ./stop.sh

IMPORTANT
Keep the .env file private. It contains your OpenAI API key.
The app needs an internet connection to contact OpenAI.
