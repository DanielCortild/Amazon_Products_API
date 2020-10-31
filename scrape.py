import json
import progressbar
import os

from config import(
  getWebDriverOptions,
  getChromeDriver,
  setIgnoreCertificateError,
  setBrowserAsIncognito,
  setHeadless
)

from scraper_config import(
  SEARCH_TERMS,
  BASE_URL
)

class Scraper:
  def __init__(self, base_url):
    self.base_url = base_url
    options = getWebDriverOptions()
    setIgnoreCertificateError(options)
    setBrowserAsIncognito(options)
    setHeadless(options)
    self.driver = getChromeDriver(options)

    self.alreadyVisited = []
    self.finalResults = []
    
  def getResults(self, searchTerm):
    results = []
    last_results_length = -1
    page = 1 

    while True:
      if len(results) == last_results_length: 
        break
      last_results_length = len(results)

      self.driver.get(f"{self.base_url}s?k={searchTerm}&page={page}")
      page += 1

      results += self.getResultsFromPage()

    self.finalResults += results

  def getResultsFromPage(self):
    results = []

    products = self.driver.find_elements_by_xpath("//div[contains(@class, 's-search-results')]/div")

    for product in products:
      try:
        asin = product.get_attribute('data-asin')
        if asin and asin not in self.alreadyVisited:
          self.alreadyVisited.append(asin)
          results.append({
            "asin": asin,
            "title": self.getName(asin),
            "price": self.getPrice(asin),
            "image": self.getImageUrl(asin),
            "rating": self.getRating(asin)
          })
      except:
        pass

    return results


  def getImageUrl(self, asin):
    imageElement = self.driver.find_element_by_xpath(f"//div[@data-asin='{asin}']//img[@class='s-image']") 
    imageUrl = imageElement.get_attribute('src')
    return imageUrl

  def getName(self, asin):
    nameElement = self.driver.find_element_by_xpath(f"//div[@data-asin='{asin}']//span[@class='a-size-base-plus a-color-base a-text-normal']")
    name = nameElement.text
    return name

  def getPrice(self, asin):
    priceElement = self.driver.find_element_by_xpath(f"//div[@data-asin='{asin}']//span[@class='a-price-whole']") 
    price = priceElement.text.replace(".", "").replace(",", ".")
    return float(price)

  def getRating(self, asin):
    try:
      ratingElement = self.driver.find_element_by_xpath(f"//span[@data-asin='{asin}']//span[@class='a-icon-alt']")
      rating = float(ratingElement.text[0:2].replace(",", "")) / 10
      return rating
    except:
      return None

  def quit(self):
    self.driver.quit()
    return self.finalResults


def generateJSON(array):
  with open('results.json', 'w') as f:
    json.dump(array, f)
  print(f"{len(array)} results written to results.json")


if __name__ == '__main__':
  os.system('clear')
  print("Starting Scrapping Script...")
  scraper = Scraper(BASE_URL)

  for i in progressbar.progressbar(range(len(SEARCH_TERMS))):
    scraper.getResults(SEARCH_TERMS[i])

  generateJSON(scraper.quit())

