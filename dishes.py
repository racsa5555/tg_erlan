from PIL import Image

d1_ru = {'id':1,'title':'Каша','reciept':'Это рецепт по приготовлению Каши','img':'./images/d1.jpeg'}
d2_ru = {'id':2,'title':'Суп','reciept':'Это рецепт по приготовлению Борща ','img':'./images/d2.jpeg'}
d3_ru = {'id':3,'title':'Блины','reciept':'Это рецепт по приготовлению Блинов ','img':'./images/d3.jpeg'}

d1_en = {'id':1,'title':'Porridge','reciept':'This is reciept for porridge','img':'./images/d1.jpeg'}
d2_en = {'id':2,'title':'Soup','reciept':'This is reciept for soup','img':'./images/d2.jpeg'}
d3_en = {'id':3,'title':'Pancakes','reciept':'This is reciept for pancakes','img':'./images/d3.jpeg'}

static_t = {'ru':'Описание','en':'Title'}
static_r = {'ru':'Рецепт','en':'Reciept'}

def pretty_dish(data,lang):
    image_path = data['img']
    res = static_t.get(lang) + ' ' + data.get('title') + '\n' + static_r.get(lang) +' ' + data.get('reciept')

    return image_path,res