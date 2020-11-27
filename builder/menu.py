
class Menu:

    def __init__(self, config):
        self.__menu = None
        if 'menu' in config.keys():
            self.__menu = []
            self.__build_menu(config)

    @staticmethod
    def __get_top_level_pages(config):
        top_level_pages = []
        for page_id in config['menu'].keys():
            if 'parent_id' not in config['menu'][page_id].keys():
                menu_item = config['menu'][page_id]
                menu_item['item_id'] = page_id
                top_level_pages.append(menu_item)
        return top_level_pages

    @staticmethod
    def __get_url_for_page(config, page_id):
        if page_id.lower() == 'home':
            return "/"
        return "/" + config['pages'][page_id]['slug']

    @staticmethod
    def get_child_pages(config, page_ids):
        pages = []
        for page_id in config['menu'].keys():
            menu_item = config['menu'][page_id]
            if 'parent_id' in menu_item.keys() and menu_item['parent_id'] in page_ids:
                menu_item['item_id'] = page_id
                menu_item['parent_id'] = config['menu'][page_id]['parent_id']
                pages.append(menu_item)
        return pages

    def __build_menu(self, config):
        # First, obtain all menu items that have no parent_id: top level items
        top_level_pages = Menu.__get_top_level_pages(config)
        for page in top_level_pages:
            self.__menu.append({
                'item_id': page['item_id'],
                'title': page['title'],
                'url': Menu.__get_url_for_page(config, page['page_id']),
                'children': []
            })
        # Second, find the children of those and add them to the menu: second level items
        second_level_pages = Menu.get_child_pages(config, [x['item_id'] for x in top_level_pages])
        for page in second_level_pages:
            parent_item = [x for x in self.__menu if x['item_id'] == page['parent_id']][0]
            parent_item['children'].append({
                'item_id': page['item_id'],
                'title': page['title'],
                'url': Menu.__get_url_for_page(config, page['page_id']),
                'children': []
            })
        pass

    def get_menu(self):
        return self.__menu
