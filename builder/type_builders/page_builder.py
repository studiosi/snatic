from markdown import markdown
from datetime import datetime
from ..builder_utils import BuilderUtils, BuilderOutputTypes
from htmlmin import minify


class PageBuilder:

    @staticmethod
    def build(cfg, page_cfg, menu, template_env):
        content_filename = BuilderUtils.get_content_filename(page_cfg['file'])
        template = template_env.get_template('page.j2')
        output_filename = BuilderUtils.get_output_filename(page_cfg['filename'], BuilderOutputTypes.TYPE_HTML)
        page_title = page_cfg['title']
        with open(content_filename, 'r') as f_content, \
                open(output_filename, 'w') as f_output:
            md_content = f_content.read()
            html_content = markdown(md_content)
            content = template.render({
                'name': cfg['site_config']['name'],
                'title': page_title,
                'content': html_content,
                'menu': menu.get_menu(),
                'creation_date': page_cfg['creation_date'],
                'build_date': datetime.now().strftime(cfg['site_config']['dt_format'])
            })
            if 'minify_html' in cfg['site_config'].keys() and \
                    cfg['site_config']['minify_html'].lower() == 'true':
                content = minify(content)
            f_output.write(content)
