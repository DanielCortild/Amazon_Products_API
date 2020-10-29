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

from amazon_config import(
  SEARCH_TERMS,
  BASE_URL
)

class AmazonAPI:
  def __init__(self, base_url):
    self.base_url = base_url
    options = getWebDriverOptions()
    setIgnoreCertificateError(options)
    setBrowserAsIncognito(options)
    setHeadless(options)
    self.driver = getChromeDriver(options)

  def run(self, r, asins, search_term):
    results = []
    last_length = -1
    page = 1

    while True:
      if(len(results) == last_length): break
      last_length = len(results)
      self.driver.get(f"{self.base_url}s?k={search_term}&page={page}")
      results = self.driver.find_elements_by_xpath("//div[contains(@class, 's-search-results')]/div")
      for res in results:
        try:
          asin = res.get_attribute('data-asin')
          if asin:
            img = res.find_element_by_xpath(f"//div[@data-asin='{asin}']//img[@class='s-image']") 
            name = res.find_element_by_xpath(f"//div[@data-asin='{asin}']//span[@class='a-size-base-plus a-color-base a-text-normal']")
            price_tag = res.find_element_by_xpath(f"//div[@data-asin='{asin}']//span[@class='a-price-whole']") 
            image = img.get_attribute('src')
            title = name.text
            price = price_tag.text.replace(".", "").replace(",", ".")

            if(asin not in asins):
              asins.append(asin)
              r.append({
                "asin": asin,
                "title": title,
                "price": float(price),
                "image": image
              })
        except:
          pass
      page += 1
      return r, asins
        
    self.driver.quit()    


def generateJSON(array):
  with open('results.json', 'w') as f:
    json.dump(array, f)
  print(f"{len(array)} results written to results.json")


if __name__ == '__main__':
  os.system('clear')
  print("Starting Scrapping Script...")
  amazon = AmazonAPI(BASE_URL)

  results = []
  asins = []
  for i in progressbar.progressbar(range(len(SEARCH_TERMS))):
    results, asins = amazon.run(results, asins, SEARCH_TERMS[i])

  generateJSON(results)

