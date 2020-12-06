from ..builder_utils import BuilderUtils, BuilderOutputTypes
from ..menu import Menu


class ArchiveBuilder:

    @staticmethod
    def __filter_pages(pages, archive_cfg):
        filtered_pages = []
        archive_categories = set([
            category.lower()
            for category
            in archive_cfg['categories'].split(',')
        ])
        for page in pages:
            page_categories = set(page['categories'])
            if len(archive_categories.intersection(page_categories)) > 0:
                filtered_pages.append(page)
        return filtered_pages

    @staticmethod
    def build(cfg, archive_cfg, pages_cfg, menu, template_env):
        pages = [
            {
                'page_id': k,
                'page_title': pages_cfg[k]['title'],
                'url': Menu.get_url_for_page(cfg, k),
                'categories': [
                    category.lower()
                    for category
                    in pages_cfg[k]['categories'].split(',')
                ],
                'creation_date': pages_cfg[k]['creation_date']
            }
            for k in pages_cfg.keys()
            if pages_cfg[k]['type'].lower() != 'archive' and k.lower() != 'home'
        ]
        if archive_cfg['categories'] != '*':
            pages = ArchiveBuilder.__filter_pages(pages, archive_cfg)
        # Build the information to pass to the template
        template = template_env.get_template('archive.j2')
        output_filename = BuilderUtils.get_output_filename(
            archive_cfg['slug'] + ".html",
            BuilderOutputTypes.TYPE_HTML
        )
        page_title = archive_cfg['title']
        with open(output_filename, 'w') as f_output:
            f_output.write(template.render({
                'name': cfg['site_config']['name'],
                'menu': menu.get_menu(),
                'title': page_title,
                'pages': pages
            }))
