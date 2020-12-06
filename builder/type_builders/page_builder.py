from markdown import markdown
from datetime import datetime
from ..builder_utils import BuilderUtils, BuilderOutputTypes


class PageBuilder:

    @staticmethod
    def build(config, page_cfg, menu, template_env):
        content_filename = BuilderUtils.get_content_filename(page_cfg['file'])
        template = template_env.get_template('page.j2')
        output_filename = BuilderUtils.get_output_filename(page_cfg['filename'], BuilderOutputTypes.TYPE_HTML)
        page_title = page_cfg['title']
        with open(content_filename, 'r') as f_content, \
                open(output_filename, 'w') as f_output:
            md_content = f_content.read()
            html_content = markdown(md_content)
            f_output.write(template.render({
                'name': config['site_config']['name'],
                'title': page_title,
                'content': html_content,
                'menu': menu.get_menu(),
                'creation_date': page_cfg['creation_date'],
                'build_date': datetime.now().strftime(config['site_config']['dt_format'])
            }))