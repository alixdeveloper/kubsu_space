from bs4 import BeautifulSoup
import requests
import urllib.request


# получение всех тегов с изображениями преподов в img_list
soup = BeautifulSoup(requests.get('https://www.kubsu.ru/ru/node/944').text, 'html.parser')
img_list = soup.findAll('div',{'class':'views-field views-field-field-user-avatar'})
names_list = soup.findAll('div',{'class':'views-field views-field-field-employee-name'})
result = {}
for x in img_list:
    # Сохраняет в словарь {имя препода:ссылка на аватар}
    result[names_list[img_list.index(x)].findAll('div',{'class':'field-content'})[0].text] = x.find_all('img')[0].get('src')
    # Сохраняет картинку по ссылке x в path y
    urllib.request.urlretrieve(x,y)
print(result)


# Парсинг полностью
data = {}
soup = BeautifulSoup(requests.get('https://www.kubsu.ru/ru/university/structure').text,'html.parser')
for i in soup.find_all('div', {'class':'field-item odd'}):
    if i.find_all('div', string='Факультеты'):
        break
for facultet in i.find_all('a')[10:]:
    print(facultet.text)
    data[facultet.text] = '' # получаем название факультета
    soup = BeautifulSoup(requests.get(facultet.get('href')).text, 'html.parser')
    for kafedra in soup.find_all('div', id='field-faculty-structure'):
        data[facultet.text] = {x.text:'' for x in kafedra.find_all('a') if 'кафедра' in x.text.lower() or 'Общего, стратегического, информационного менеджмента и бизнес-процессов' in x.text.lower() or 'Социальной работы, психологии и педагогики высшего образования' in x.text.lower() or 'Социальной психологии и социологии управления' in x.text.lower() or 'Психологии личности и общей психологии' in x.text.lower() or 'Политологии и политического управления' in x.text.lower() or 'Государственной политики и государственного управления' in x.text.lower() or 'Организации и планирования местного развития' in x.text.lower() or 'Государственного и муниципального управления' in x.text.lower() }
        for x in kafedra.find_all('a'):
            print(x.text)
            if 'кафедра' in x.text.lower()  or 'Общего, стратегического, информационного менеджмента и бизнес-процессов' in x.text.lower() or 'Социальной работы, психологии и педагогики высшего образования' in x.text.lower() or 'Социальной психологии и социологии управления' in x.text.lower() or 'Психологии личности и общей психологии' in x.text.lower() or 'Политологии и политического управления' in x.text.lower() or 'Государственной политики и государственного управления' in x.text.lower() or 'Организации и планирования местного развития' in x.text.lower() or 'Государственного и муниципального управления' in x.text.lower():
                if 'kubsu' not in x.get('href'):
                    z = 'https://www.kubsu.ru'+x.get('href')
                else:
                    z= x.get('href')
                soup = BeautifulSoup(requests.get(z).text, 'html.parser')
                data[facultet.text][x.text] = []

                img_list = soup.findAll('div', {'class': 'views-field views-field-field-user-avatar'})
                names_list = soup.findAll('div', {'class': 'views-field views-field-field-employee-name'})
                result = {}
                # for g in img_list:
                #     # Сохраняет в словарь {имя препода:ссылка на аватар}
                #     result[names_list[img_list.index(g)].findAll('div', {'class': 'field-content'})[0].text] = \
                #     g.find_all('img')[0].get('src')
                #     # Сохраняет картинку по ссылке x в path y
                #     # urllib.request.urlretrieve(x, y)
                #     # data[facultet.text][x.text].append({names_list[img_list.index(g)].findAll('div', {'class': 'field-content'})[0].text:g.find_all('img')[0].get('src')})
                for xy in soup.find_all('a'):
                    if xy.text.lower() == 'публичное портфолио':
                        if 'kubsu' not in xy.get('href'):
                            xz = 'https://www.kubsu.ru'+xy.get('href')
                        else:
                            xz= xy.get('href')
                        soup = BeautifulSoup(requests.get(xz).text, 'html.parser')
                        dolshnost = soup.find_all('div',{'class':'field field-name-field-employee-post field-type-text field-label-hidden'})[0].text
                        about = soup.find_all('div',{'class':'views-field'})
                        name = soup.find(id='page-title').text
                        print(name)

                        img_user = soup.find_all('div',{'class':'views-field views-field-field-user-avatar'})[0].find('img').get('src')
                        for a in about:
                            if 'дисциплины' in a.text:
                                break
                        img = soup.find_all('div', {'class': 'views-field views-field-field-user-avatar'})[0].find_all('img')[0].get('src')
                        data[facultet.text][x.text].append({'name':name,'img': img_user, 'dolshnost': dolshnost,'about':a.text})
                        print(data[facultet.text][x.text][-1])