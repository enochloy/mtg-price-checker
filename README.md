# MTG Cards Price Checker

### Description:
This project/website was built for the convenient sourcing of the cheapest MTG cards in Singapore. There are more than a dozen stores in Singapore that sells MTG cards and the prices fluctuate quite a lot from store to store. It is very inconvenient to compare prices across multiple websites, and it may be costly to just purchase from one store. This website makes it easy to compare prices across multiple stores, saving you both time and money.

- `app.py`: This is the main flask file that handles incoming HTTPS requests.
- `helpers.py`: This contains the helper functions for returning invalid requests and login.
- `scraping.py`: This is the python file for scraping data off the store websites.
- `apology.html`: Template for invalid requests
- `changepassword.html`: Template for changing passwords
- `login.html`: Template for logging in
- `register.html`: Template for registration
- `index.html`: Template for main page
- `layout.html`: Layout template
- `singlechecker.html`: Template for checking price of singles
- `deckchecker.html`: Template for checking prices of decks/group of cards
- `cards.db`: Database for cards information
- `users.db`: Database for users information

### Features
<b>Data Scraping</b>
- Utilized BeautifulSoup and Selenium packages to scrape cards data off 4 store websites (Agora, OneMTG, CardsCitadel, Grey Ogre).
- Using Pandas and SQLite3, I concatenated the data together and imported it as a `cards.db`
- The web scraping script can be run again to refresh data scraped from this websites

<b>Website Design</b>
- The singles checker function allow users to key in the card name, and it automatically returns the top 20 cheapest cards that matches their search query. There are also checkboxes available to allow users to pick which stores they want to include/exclude in the search query.
- Deck checker function allow users to input their entire deck list (export from Moxfield), select the stores, and press the 'Check Price' button. A spinning wheel will appear to show that it is fetching data from the database, which will be hidden once the query is completed. This will return multiple tables showing the cheapest price of each card, one table for each store.
- If more stores/data is added to the database, the HTML will automatically reflect the addition of other stores.