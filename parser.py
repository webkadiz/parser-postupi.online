
import requests
from pprint import pprint
from bs4 import BeautifulSoup
from datetime import datetime
from tkinter import tix as tk
import tkinter.ttk as ttk
import json
from PIL import Image


class Parser():
	BASE_URL = 'https://postupi.online/'
	def __init__(self):
		self.directs = {}
		self.direct_url = ''
		self.direct = ''
		self.filters = {}
		self.filter_url = ''
		self.univers = []
		self.univers_chosen = []
		self.facultets = {}


	def get_html(self, url, param={}):
		response = requests.get(url, param)
		soup = BeautifulSoup(response.text, 'lxml')
		return soup

	def get_directs(self):
		html = self.get_html(Parser.BASE_URL)
		links = html.find_all('a', class_="main_similar")
		
		self.directs = {
			'links': [link.get('href') for link in links],
			'names': [link.find(class_="h3").string for link in links]
		}

	def get_filters(self):
		html = self.get_html(self.direct_url)	

		for filter_ in html.find(class_="filter-menu list-unstyled filter_new").find_all('li', class_="collapsed"):
			links = filter_.find_all('a')
			filter_title = filter_.find('p').text
			self.filters[filter_title] = {
				'links': [link.get('href')[link.get('href').rfind('/', 0, -1)+1:] for link in links],
				'names': [link.find('span').text for link in links]
			}

	def get_univers(self):
		with open('univers.txt', 'r') as f:
			for line in f:
				self.univers += [json.loads(line)]

		self.univers.sort(key=lambda item: item['city'])
		cities = [city['city'] for city in self.univers]
		
		i = 0
		j = 0
		while i < len(self.univers):
			name = cities[j]
			count = cities.count(name)		
			self.univers[i:count+i] = [self.univers[i:count+i]]
			j += count
			i += 1
			

	def get_facultets(self):
		i = 0
		while True: # пока есть странички
			i += 1
			print(i)

			html = self.get_html(self.filter_url, param={'page_num': i}) # страничка с факультетами

			if not html.find(class_="page_pointer forward"): break

			for fac in html.find_all(class_="list-flex"): # перебор факультетов
				link = fac.find('a', class_='list-flex__img list-flex__img_lg') # подробнее о факультетов
				fac_name = fac.find('h2', class_='list-flex__h2').find('a').text # название о факультетов
				flag = True

				for univer in self.get_html(link.get('href') + 'varianti/').find(class_='list-unstyled list-flex-wrap').find_all('li'): # перебор вузов факультета
					univer_name = univer.find('h2', class_='list-flex__h2').find('a').text

					if univer_name in self.univers_chosen and flag: # если есть отмеченный вуз, то собираем все данные о факультете
						flag = False
						description_data = ''
						courses_data = []
						salary_data = 0
						careers_data = []
						professions_data = []

						fac_careers = self.get_html(link.get('href') + 'deyat/')
						fac_courses= self.get_html(link.get('href'))
						careers = fac_careers.find(class_='descr_max')
						courses = fac_courses.find(class_='descr_max')
						description_data = courses.find('p').text

						try: salary_data = fac_careers.find_all(class_='cnt_rght')[-1].text
						except: pass

						for career in careers.find_all('ul'):
							for sub_career in career.find_all('li'):
								careers_data.append(sub_career.text)

						for course in courses.find_all('ul'):
							for sub_course in course.find_all('li'):
								courses_data.append(sub_course.text)

						j = 0
						while True:
							j += 1
							professions = self.get_html(link.get('href') + 'professii/', param={'page_num': j})

							if not professions.find(class_="page_pointer forward") and j != 1: break

							for profession in professions.find(class_='list-unstyled flex-panel').find_all('li'):
								professions_data.append({
									'name': profession.find(class_='flex-panel__h2').text,
									'actuality': profession.find(class_='prof_inner').text or 'обычная профессия'
								})

						self.facultets[fac_name] = { # заполняем данные
							'description': description_data,
							'courses': courses_data,
							'salary': salary_data,
							'careers': careers_data,
							'professions': professions_data,
							'univers': [],
						}
				
				if univer_name in self.univers_chosen:
					self.facultets[fac_name]['univers'].append(univer_name)




class GUI():
	def __init__(self):
		self.root = tk.Tk()
		self.root.geometry('700x700')

		self.scrollbar = tk.ScrolledWindow(self.root, scrollbar=tk.BOTH)
		self.scrollbar.pack(fill=tk.BOTH, expand=1)

		self.top_frame = tk.Frame(self.scrollbar.window)
		self.top_frame.pack(side=tk.TOP)

		self.bottom_frame = tk.Frame(self.scrollbar.window)
		self.bottom_frame.pack(side=tk.BOTTOM)

		self.forward = tk.Button(self.bottom_frame, text='далее')
		self.forward.pack(side=tk.LEFT)
		self.forward.bind('<1>', self.click_forward)
		self.forward.pos = ''

		self.path = tk.Label(self.bottom_frame, text='')
		self.path.pack(side=tk.LEFT)

	def show_directs(self):
		for i, name in enumerate(self.directs['names']):
			print(name)
			for j in range(3):
				btn = tk.Button(self.top_frame, text=name)
				btn.bind('<Button-1>', self.direct_chosen)
				btn.grid(row=i, column=j)

		self.widget_directs = self.top_frame.grid_slaves()
	
	def show_filters(self):
		for i, (key, value) in enumerate(self.filters.items()):
			label = tk.Label(self.top_frame, text=key)
			label.grid(row=0, column=i)
			for j, name in enumerate(value['names']):
				var = tk.IntVar()
				btn = tk.Checkbutton(self.top_frame, text=name, variable=var)
				btn.var = var
				btn.label = label['text']
				btn.grid(row=j + 1, column=i)
				btn.bind('<1>', self.gen_filter_url)

		self.widget_filters = self.top_frame.grid_slaves()

	def show_univers(self):
		i = 0
		for cities in self.univers:
			label = tk.Label(self.top_frame, text=cities[0]['city'])
			label.grid(row=i, column=0)
			label.label = False
			label.collapsed = True
			label.bind('<1>', self.switch_univers)
			i += 1
			for univer in cities:
				var = tk.IntVar()
				checkbutton = tk.Checkbutton(self.top_frame, text=univer['name'], variable=var)
				checkbutton.var = var
				checkbutton.grid(row=i, column=0)
				checkbutton.label = label
				checkbutton.bind('<1>', self.gen_univers_chosen)
				i += 1

		self.widget_univers = self.top_frame.grid_slaves()

		for widget in self.widget_univers:
			if ~str(widget.winfo_class).find('checkbutton'): widget.grid_remove()
	
	def show_facultets(self):
		pass

	def write_univers(self):
		f = open('univers.txt', 'w')
		i = 0
		while True:
			i += 1
			print(i)
			html = self.get_html('https://postupi.online/vuzi', param={'page_num': i})

			if not html.find(class_="page_pointer forward"): break

			for univer in html.find_all(class_='list-flex'):
				p = univer.find('p', class_='list-flex__pre')
				name = univer.find('h2', class_='list-flex__h2').text
				img_url = univer.find('a', class_='list-flex__img').find('img')['src']
				img = self.get_html(img_url).text

				f.write(json.dumps({
					'name': name,
					'city': p.contents[-2].text,
					'goverment': p.contents[-1].text,
					#'img': img
				}) + '\n')




class Logic(GUI, Parser):
	def __init__(self):
		Parser.__init__(self)
		GUI.__init__(self)

		self.windows = ['directs', 'filters', 'univers', 'facultets']
	
	def run(self):
		self.get_directs()
		self.show_directs()
		self.root.mainloop()
		
	def direct_chosen(self, event):
		self.path['text'] = event.widget['text']		
		self.direct_url = self.directs['links'][self.directs['names'].index(self.path['text'])]
		self.direct = self.path['text']

	def gen_filter_url(self, event):
		widget = event.widget
		if not self.filter_url:
			self.filter_url = self.direct_url

		print(self.filter_url)

		if widget['state'] == 'normal':
			switch = widget.var.get()
			link = self.filters[widget.label]['links'][self.filters[widget.label]['names'].index(widget['text'])]
			if switch: # unchecked
				state = tk.NORMAL
				self.filter_url = self.filter_url.replace(link, '')
			else: # checked
				state = tk.DISABLED
				self.filter_url += link
			for item in self.top_frame.grid_slaves():
				if (item['text'] in self.filters[widget.label]['names'] and 
						widget.label != 'По предметам ЕГЭ' 									and 
						item['text'] != widget['text']):
					item.config(state=state)

	def gen_univers_chosen(self, event):
		self.univers_chosen.remove(event.widget['text']) if event.widget.var.get() else self.univers_chosen.append(event.widget['text'])

	def switch_univers(self, event):
		widget = event.widget
		flag =  widget.collapsed

		for univer in self.widget_univers:
			if univer.label == widget: univer.grid() if flag else univer.grid_remove()

		widget.collapsed = not flag

	def click_forward(self, event):
		forward = event.widget

		if not forward.pos:
			forward.pos = self.windows[1]
		else: 
			forward.pos = self.windows[self.windows.index(forward.pos) + 1]

		if forward.pos == 'filters':
			for slave in self.widget_directs:
				slave.grid_remove()

			self.get_filters()
			self.show_filters()
		elif forward.pos == 'univers':
			for slave in self.widget_filters:
				slave.grid_remove()

			self.get_univers()
			self.show_univers()
		elif forward.pos == 'facultets':
			for slave in self.widget_univers:
				slave.grid_remove()

			self.get_facultets()
			self.show_facultets()



if __name__ == '__main__':
	app = Logic()

	app.run()

