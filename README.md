# What's this 

Simple web pages scrapper, which gets content & statics via Selenium, and saves them in MongoDB for further view in browser. 
Works on FastAPI.

# Todo list:

- Add docker-compose and cmd-scripts for quick deployment anywhere
- MongoDB backup/restore scripts
- Test & improve recursive mode
- Batch scrapping 
- Fix some of "local" statics downloading (.js-files)
- Better, more beautiful frontend (use some of fancy online designer?) 
- Better captcha, etc avoidance (better "user-agent" headers, requests timing, maybe change Selenium for other lib)
- Multiple instances of scrappers for recursive/batch modes, with jobs query