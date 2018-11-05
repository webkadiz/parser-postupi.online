
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_soup(url, param = {}):
	response = requests.get(url, param)
	soup = BeautifulSoup(response.text, 'lxml')
	return soup

def get_univers():
	i = 1
	response = requests.get('https://postupi.online/vuzi/?page_num={}'.format(i))
	soup = BeautifulSoup(response.text, 'lxml')

	univers = {}

	while soup.find(class_="page_pointer forward"):
		i += 1
		print(i)
		response = requests.get('https://postupi.online/vuzi/?page_num={}'.format(i))
		soup = BeautifulSoup(response.text, 'lxml')

		for univer in soup.find_all(class_='list-flex'):
			p = univer.find('p', class_='list-flex__pre')
			name = univer.find('h2', class_='list-flex__h2').text

			univers[name] = {
				'city': p.contents[0].text,
				'goverment': p.contents[1].text
			}

	return univers


def get_directs():
	response = requests.get('https://postupi.online/')
	soup = BeautifulSoup(response.text, 'lxml')
	links = soup.find_all('a', class_="main_similar")
	
	return  {
		'links': [link.get('href') for link in links],
		'names': [link.find(class_="h3").string for link in links]
	}

def get_filters(direction):
	response = requests.get(direction)

	soup = BeautifulSoup(response.text, 'lxml')

	filters = {}

	for filter_ in soup.find(class_="filter-menu list-unstyled filter_new").find_all('li', class_="collapsed"):
		links = filter_.find_all('a')
		filter_title = filter_.find('p').text
		filters[filter_title] = {
			'links': [link.get('href')[link.get('href').rfind('/', 0, -1)+1:] for link in links],
			'names': [link.find('span').text for link in links]
		}

	return filters

def main():
	directs = get_directs()
	direct = directs['links'][3]

	univers = get_univers()
	univers_names = univers.keys()
	choose_univers = ['Национальный исследовательский университет "Высшая школа экономики"', 'Московский авиационный институт (национальный исследовательский университет) (МАИ)']
	
	filters = get_filters(direct)

	request = (direct + filters['По предметам ЕГЭ']['links'][0] +
	filters['По предметам ЕГЭ']['links'][1] + filters['По предметам ЕГЭ']['links'][2] +
	filters['Форма обучения']['links'][0] + filters['Формат обучения']['links'][0] +
	filters['Оплата обучения']['links'][1])

	i = 1
	soup = get_soup(request, {'page_num': i})

	while soup.find(class_="page_pointer forward"):
		i += 1
		print(i)
		soup = get_soup(request, {'page_num': i})

		for fac in soup.find_all(class_="list-flex"):
			link = fac.find('a', class_='list-flex__img list-flex__img_lg')
			fac_title = fac.find('h2', class_='list-flex__h2').find('a').text

			for item in get_soup(link.get('href') + 'varianti/').find(class_='list-unstyled list-flex-wrap').find_all('li'):
				univer_name = item.find('h2', class_='list-flex__h2').find('a').text

				if univer_name in choose_univers:
					print(fac_title)










if __name__ == '__main__':
  main()
