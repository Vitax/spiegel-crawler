from src.scrape import Scrape


def run():
    s = Scrape()
    s.extract_information_to_json();


if __name__ == '__main__':
    run()
